
`include "uart_globals.svh"

/**
 * Receiver module for uart.
 */
module uart_rx(
    // current state of the state machine
    output reg[$clog2(`STATES_NUM)-1:0]   state,
    // oversampling (1/2 oversampling to find start bit middle, then full oversampling)
    output reg[$clog2(`OVERSAMPLING)-1:0] oversample_idx, // counter for oversampling
    // data bit buffer
    output reg[`NUM_DATA_BITS-1:0]  data_buffer,          // data buffer for state machine
    // data bit counter
    output reg[$clog2(`NUM_DATA_BITS):0]  data_idx,       // counter for current data bit
    // parity valid checker
    output reg parity_valid, // 1 if parity is valid (signal valid in parity state)
    output reg[(`NUM_DATA_BITS+`NUM_PARITY_BIT)-1:0] data_and_parity_bits, // concatenation of signals

    input  wire                     baud,   // baud clk
    input  wire                     enable, // enable rx read
    input  wire                     rx,     // rx line
    output reg[`NUM_DATA_BITS-1:0]  data,   // read data bits
    output reg                      done,   // end of packet transaction
    output reg                      busy,   // transaction is in progress
    output reg                      error   // error detected at some point
);

// declarations ////////////////////////////////////////////////////////////////
// // current state of the state machine
// reg[$clog2(`STATES_NUM)-1:0]   state;
// // oversampling (1/2 oversampling to find start bit middle, then full oversampling)
// reg[$clog2(`OVERSAMPLING)-1:0] oversample_idx; // counter for oversampling
// // data bit counter
// reg[$clog2(`NUM_DATA_BITS):0]  data_idx;       // counter for current data bit
// // parity valid checker
// reg parity_valid; // 1 if parity is valid (signal valid in parity state)
// reg[(`NUM_DATA_BITS+`NUM_PARITY_BIT)-1:0] data_and_parity_bits; // concatenation of signals

// helper logic ////////////////////////////////////////////////////////////////
// determine if parity is ok
always @(*) begin
    data_and_parity_bits <= {data_buffer, rx};
    `ifdef PARITY_EVEN
    // valid if even # of 1s in data and parity bit.
    parity_valid <= ~^data_and_parity_bits; // XNOR
    `elsif PARITY_ODD
    // valid if odd # of 1s in data and parity bit.
    parity_valid <= ^data_and_parity_bits; // XOR
    `endif
end

// uart state machine //////////////////////////////////////////////////////////
always @(posedge baud) begin
    // receiver should not be receiving data
    if (!enable) begin
        RESET();
    end
    // start state machine
    else begin
        case (state) 
            `STATE_IDLE       : IDLE();
            `STATE_DATA_BITS  : DATA_BITS();
            `STATE_PARITY_BIT : PARITY_BIT();
            `STATE_STOP_BIT   : STOP_BIT();
            default : state <= `STATE_IDLE;
        endcase
    end
    
end

// state tasks /////////////////////////////////////////////////////////////////
task RESET();
    // start idling for start bit
    state = `STATE_IDLE;
    // initialize output signals
    data  <= 0;
    done  <= 0;
    busy  <= 0;
    error <= 0;
    // initialize helper signals
    oversample_idx <= 0;
    data_buffer    <= 0;
    data_idx       <= 0;
endtask
task IDLE();
    error <= 0;
    done  <= 0;
    // check for start bit 
    if (!rx) begin
        // detected a start bit 
        busy  <= 1;
        // check if at middle of start bit x
        if (oversample_idx == (`OVERSAMPLING/2)-1) begin
            // at middle of start bit
            state <= `STATE_DATA_BITS;
            oversample_idx <= 0; 
            data_buffer    <= 0;
            data_idx       <= 0;
        end else begin
            // not at middle of start bit yet
            oversample_idx <= oversample_idx + 1;
        end
    end else begin
        // idling
        oversample_idx <= 0;
        busy           <= 0;
    end
endtask
task DATA_BITS();
    // check for next data bit
    if (oversample_idx == `OVERSAMPLING-1) begin
        // at middle of next data bit 
        // shift rx data bit in (uart LSB -> MSB so MSB is last)
        data_buffer <= {rx, data_buffer[`NUM_DATA_BITS-1:1]};
        // data[data_idx] <= rx;
        // increment counters
        data_idx <= data_idx + 1;
        oversample_idx <= oversample_idx + 1;
        // check if last data bit 
        if (data_idx == `NUM_DATA_BITS-1) begin
            // at last data bit 
            state <= `STATE_PARITY_BIT; 
        end
    end else begin
        // not at next data bit -> increment oversampling counter
        oversample_idx <= oversample_idx + 1;
    end
endtask
task PARITY_BIT();
    // check if at middle of parity bit
    if (oversample_idx == `OVERSAMPLING-1) begin
        // at parity bit -> check if data is valid
        oversample_idx <= oversample_idx + 1; 
        if (parity_valid) begin
            // parity valid
            state <= `STATE_STOP_BIT; 
        end else begin
            // invalid parity
            state <= `STATE_IDLE;
            error <= 1;
        end
    end else begin
        // not at middle of parity bit -> increment oversampling counter
        oversample_idx <= oversample_idx + 1;
    end
endtask
task STOP_BIT();
    // check if at middle of stop bit
    if (oversample_idx == `OVERSAMPLING-1) begin
        // at middle of stop bit
        state <= `STATE_IDLE;
        busy  <= 0;
        // check if stop bit is valid (should be high)
        if (rx) begin
            // valid stop bit
            done  <= 1;
            data  <= data_buffer;
        end else begin
            // invalid stop bit
            error <= 1;
        end
    end else begin 
        // not at middle of stop bit -> increment oversampling counter
        oversample_idx <= oversample_idx + 1;
    end
endtask


endmodule