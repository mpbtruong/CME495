
`include "uart_globals.svh"

/**
 * Receiver module for uart.
 */
module uart_rx(
    input  wire                     baud,   // baud clk
    input  wire                     enable, // enable rx read
    input  wire                     rx,     // rx line
    output reg[`NUM_DATA_BITS-1:0]  data,   // read data bits
    output reg                      done,   // end of packet transaction
    output reg                      busy,   // transaction is in progress
    output reg                      error   // error detected at some point
);

// declarations ////////////////////////////////////////////////////////////////
// current state of the state machine
reg[$clog2(`STATES_NUM)-1:0]   state;
// oversampling (1/2 oversampling to find start bit middle, then full oversampling)
reg[$clog2(`OVERSAMPLING)-1:0]            oversample_idx;        // counter for oversampling
reg                                       stop_extra_oversample; // flag so stop bit gets its full time
// data bit buffer
reg[`NUM_DATA_BITS-1:0]                   data_buffer;           // data buffer for state machine
// data bit counter
reg[$clog2(`NUM_DATA_BITS)-1:0]           data_idx;              // counter for current data bit
// parity valid checker
reg                                       parity_valid;          // 1 if parity is valid
reg[(`NUM_DATA_BITS+`NUM_PARITY_BIT)-1:0] data_and_parity_bits;  // concatenation of signals


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
    state <= `STATE_IDLE;
    // initialize output signals
    data  <= 0;
    done  <= 0;
    busy  <= 0;
    error <= 0;
    // initialize helper signals
    oversample_idx        <= 0;
    data_buffer           <= 0;
    data_idx              <= 0;
    stop_extra_oversample <= 0;
endtask
task IDLE();
    done           <= 0;
    busy           <= 0;
    error          <= 0;
    oversample_idx <= 0;
    // check for start bit 
    if (!rx) begin
        // detected a start bit 
        busy  <= 1;
        // check if at middle of start bit x
        if (oversample_idx == (`OVERSAMPLING/2)) begin
            // at middle of start bit
            state <= `STATE_DATA_BITS;
            oversample_idx <= 0; 
            data_buffer    <= 0;
            data_idx       <= 0;
        end else begin
            // not at middle of start bit yet
            oversample_idx <= oversample_idx + 1;
        end
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
            stop_extra_oversample <= 1;
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
    // check if need to get to middle of stop bit
    if (stop_extra_oversample) begin
        // need to get to the start bit
        if (oversample_idx == `OVERSAMPLING-1) begin
            // around the middle now
            stop_extra_oversample <= 0;
            // give remaining half of oversampling for stop bit detection
            oversample_idx <= (`OVERSAMPLING/2)-2;
        end else begin 
            // not at middle of stop bit yet
            oversample_idx <= oversample_idx + 1;
        end
    end else begin
        // past the stop bit middle -> detect stop bit
        if (rx) begin
            // found the stop bit
            data  <= data_buffer;
            done  <= 1;
            busy  <= 0;
            state <= `STATE_IDLE;
        end else if (!rx && oversample_idx == `OVERSAMPLING-1) begin
            // end of oversampling without detecting stop bit
            error <= 1;
            state <= `STATE_IDLE;
        end else begin
            // have not detected stop bit yet
            oversample_idx <= oversample_idx + 1;
        end
    end
endtask


endmodule