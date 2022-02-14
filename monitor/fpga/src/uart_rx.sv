
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
reg[2:0] state;
// oversampling
reg[$clog2(`OVERSAMPLING)-1:0]  sample_idx;  // current sample number
reg[`OVERSAMPLING-1:0]          oversamples; // 1-hot encoding of all samples
reg                             sample;      // the majority of the oversampling
// data bits
reg[$clog2(`NUM_DATA_BITS)-1:0] data_idx;    // current data bit
// parity checking 
reg[$clog2(`NUM_DATA_BITS+`PARITY_BIT)-1:0] parity_ones; // number of ones in data
reg                                         parity_ok;   // 1 if parity is valid

// instantiations //////////////////////////////////////////////////////////////
// determine the sample by determining the majority of the oversamples
count_ones #(.BITWIDTH(`OVERSAMPLING))
decide_oversampling(
    .signal(oversamples),
    .ones(sample)
);
// determine the number of parity ones used to determine if parity is correct
count_ones #(.BITWIDTH(`NUM_DATA_BITS+`PARITY_BIT))
count_parity_ones(
    .signal({data, sample}), // data bits + parity bit
    .ones(parity_ones)
);

// helper blocks ///////////////////////////////////////////////////////////////
// parity_ok
`ifdef PARITY_EVEN
always @(*) parity_ok <= !(parity_ones % 2); // even # of 1s good
`elsif PARITY_ODD
always @(*) parity_ok <=  (parity_ones % 2); // odd # of 1s good
`endif

// uart state machine //////////////////////////////////////////////////////////
always @(posedge baud) begin
    // receiver should not be receiving data
    if (!enable) begin
        state = `STATE_RESET;
    end
    // start state machine
    else begin
        case (state) 
            `STATE_RESET      : RESET();
            `STATE_IDLE       : IDLE();
            `STATE_START_BIT  : START_BIT();
            `STATE_DATA_BITS  : DATA_BITS();
            `STATE_PARITY_BIT : PARITY_BIT();
            `STATE_STOP_BIT   : STOP_BIT();
            default : state <= `STATE_IDLE;
        endcase
    end
    
end

// state tasks /////////////////////////////////////////////////////////////////
task RESET();
    // main outputs
    data  <= 0;
    done  <= 0;
    busy  <= 0;
    error <= 0;
    // helper signals
    sample_idx  <= 0;
    oversamples <= 0;
    data_idx    <= 0;
    if (enable) state <= `STATE_IDLE;
endtask
task IDLE();
    busy <= 0;
    if (!rx) state <= `STATE_START_BIT;
endtask
task START_BIT();
    // done sampling
    if (sample_idx == `OVERSAMPLING - 1) begin
        sample_idx <= 0;
        // start bit is low -> start reading data
        if (!sample) begin
            state <= `STATE_DATA_BITS;
            busy  <= 1;
        end
        else begin
            state <= `STATE_RESET;
            error <= 1;
        end
    end
    // continue sampling
    else begin
        oversamples[sample_idx] <= rx;
        sample_idx += 1;
    end
endtask
task DATA_BITS();
    // read all the data bits
    if (data_idx == `NUM_DATA_BITS - 1) begin
        data_idx <= 0;
        // go to parity state and check if data is ok
        state <= `STATE_PARITY_BIT;
    end
    // keep reading data bits
    else begin
        // done sampling
        if (sample_idx == `OVERSAMPLING - 1) begin
            sample_idx <= 0;
            // assign the oversampled data bit
            data[data_idx] <= sample;
        end
        // continue sampling
        else begin
            oversamples[sample_idx] <= rx;
            sample_idx += 1;
        end
    end
endtask
task PARITY_BIT();
    // done sampling
    if (sample_idx == `OVERSAMPLING - 1) begin
        sample_idx <= 0;
        // check parity
        if (parity_ok) state <= `STATE_STOP_BIT;
        // parity was not valid
        else begin
            state <= `STATE_RESET;
            error <= 1;
        end
    end
    // continue sampling
    else begin
        oversamples[sample_idx] <= rx;
        sample_idx += 1;
    end
endtask
task STOP_BIT();
    // done sampling
    if (sample_idx == `OVERSAMPLING - 1) begin
        sample_idx <= 0;
        // check stop bit
        if (sample) begin
            state <= `STATE_IDLE;
            done  <= 1;
        end
        // stop bit was not valid
        else begin 
            state <= `STATE_RESET;
            error <= 1;
        end
    end
    // continue sampling
    else begin
        oversamples[sample_idx] <= rx;
        sample_idx += 1;
    end
endtask


endmodule