
`include "uart_globals.svh"
/**
 * Transmitter module for uart.
 */
module uart_tx(
    input  wire                     baud,   // baud clk
    input  wire                     enable, // enable rx read
    input  wire                     write,  // pulse signal to write when enabled
    input  reg[`NUM_DATA_BITS-1:0]  data,   // data bits to write
    output wire                     tx,     // tx line
    output reg                      done,   // end of packet transaction
    output reg                      busy,   // transaction is in progress
    output reg                      error   // error detected at some point 
);

// declarations ////////////////////////////////////////////////////////////////
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

endtask
task IDLE();

endtask
task DATA_BITS();

endtask
task PARITY_BIT();

endtask
task STOP_BIT();

endtask

endmodule