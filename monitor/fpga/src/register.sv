
/**
 * Register for storing data for all of the parameterized signals that
 * are read/written from the pc monitor/controller.
 */
module register
#(parameter DATA_BYTES = 4, parameter RESET_VALUE = 0)(
    input  wire                         clk,
    input  wire                         reset,
    input  wire                         write,      // active high register write
    input  wire                         write_done, // done writing bytes
    input  wire[$clog2(DATA_BYTES)-1:0] write_byte, // byte to write
    
    input  wire                         read_ack,
    output reg                          changed,
    output reg[8*DATA_BYTES-1:0]        data
);

always @(posedge clk) begin
    if (reset) begin
        data <= RESET_VALUE;
    end
    else begin
        data <= data;
    end
end

endmodule