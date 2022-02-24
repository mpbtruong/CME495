
`include "uart_globals.svh"

/**
 * Transmitter module for uart.
 */
module uart_tx(
    output reg[$clog2(`STATES_NUM)-1:0]    state,    // current state of the state machine
    output reg[`NUM_DATA_BITS-1:0]         data_reg, // clk data in at start of transmission
    output reg[$clog2(`NUM_DATA_BITS)-1:0] data_idx, // counter for current data bit


    input  wire                     baud,   // baud clk
    input  wire                     enable, // enable rx read
    input  wire                     write,  // pulse signal to write when enabled
    input  reg[`NUM_DATA_BITS-1:0]  data,   // data bits to write
    output reg                      tx,     // tx line
    output reg                      done,   // end of packet transaction
    output reg                      busy,   // transaction is in progress
    output reg                      error   // error detected at some point 
);

// declarations ////////////////////////////////////////////////////////////////


// add debug regs back here later (TO-DO)



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
    tx    <= 1; // drive uart tx line high
    done  <= 0;
    busy  <= 0;
    error <= 0;
    // initialize helper signals
    data_reg <= 0;
    data_idx <= 0;
endtask
task IDLE();
    // set idle values
    done     <= 0;
    error    <= 0;
    // detect start of transmission
    if (enable && write) begin
        busy     <= 1;
        // starting transmission
        state    <= `STATE_DATA_BITS;
        tx       <= 0;    // drive uart tx line low (start bit)
        data_reg <= data; // clk in data for transmission
        data_idx <= 0;    // reset data bit counter to LSB bit
    end else begin
        busy     <= 0;
        tx       <= 1; // drive uart tx line high
        // data_reg <= 0; // clear transmitted data buffer
    end
endtask
task DATA_BITS();
    tx <= data_reg[data_idx]; // transmit current data bit
    // check if done transmitting bits
    if (data_idx == `NUM_DATA_BITS-1) begin
        // done transmitting bits -> go to parity bit state
        state <= `STATE_PARITY_BIT;
    end else begin
        // not done transmitting bits
        data_idx <= data_idx + 1; // increment data bit counter
    end
endtask
task PARITY_BIT();
    // transmit the parity bit
    `ifdef PARITY_EVEN
    // need to make {data_reg, parity bit} have even # of 1s
    tx <= ^data_reg; // XOR
    `elsif PARITY_ODD
    // need to make {data_reg, parity bit} have odd # of 1s
    tx <= ~^data_reg; // XNOR
    `endif
    // go to stop bit state
    state <= `STATE_STOP_BIT;
endtask
task STOP_BIT();
    // transmit the stop bit
    tx    <= 1;
    // set flag states
    done  <= 1;
    busy  <= 0;
    // go back to idling
    state <= `STATE_IDLE;
endtask

endmodule