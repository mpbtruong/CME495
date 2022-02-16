
`include "uart_globals.svh"

/**
 * Transmitter module for uart.
 */
module uart_tx(
    output reg                            data_reg, // clk data in at start of transmission
    output reg[$clog2(`NUM_DATA_BITS):0]  data_idx, // counter for current data bit


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
endtask
task IDLE();
    // set idle values
    done     <= 0;
    error    <= 0;
    data_reg <= 0;
    // detect start of transmission
    if (enable && write) begin
        // starting transmission
        state <= `STATE_DATA_BITS;
        busy  <= 1;
    end else begin
        tx    <= 1; // drive uart tx line high
        busy  <= 0;
    end
endtask
task DATA_BITS();
    
endtask
task PARITY_BIT();

endtask
task STOP_BIT();

endtask

endmodule