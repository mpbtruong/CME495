
/**
 * Register for storing data for all of the parameterized signals that
 * are read/written from the pc monitor/controller.
 */
module register
#(parameter DATA_BITS = 32, parameter RESET_VALUE = 0)(
    input  wire                         clk,
    input  wire                         reset,   // reset to default value
    input  wire                         write,   // active high to write reg
    input  wire[DATA_BITS-1:0]          data_in, // data to write
    
    output reg[DATA_BITS-1:0]           data     // current reg data
);

always @(posedge clk) begin
    if (reset) begin
        // reset to default value
        data <= RESET_VALUE;
    end else if (write) begin
        // write new data
        data <= data_in;
    end else begin
        // maintain data
        data <= data;
    end
end

endmodule