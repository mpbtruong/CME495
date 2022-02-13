
`include "uart_globals.svh"

/**
 * Receiver module for uart.
 */
module uart_rx(
    input  wire                     baud,  // baud clk
    input  wire                     reset, // baud clk
    input  wire                     en,    // enable rx read
    input  wire                     rx,    // rx line
    output reg[`NUM_DATA_BITS-1:0]  data,  // read data bits
    output reg                      done,  // end of packet transaction
    output reg                      busy,  // transaction is in progress
    output reg                      error  // error detected at some point
);

// declarations ////////////////////////////////////////////////////////////////
// current state of the state machine
reg[2:0] state;

// uart state machine //////////////////////////////////////////////////////////


endmodule