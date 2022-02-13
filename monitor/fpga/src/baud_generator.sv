
/**
 * Generates a baud rate given a 50Mhz clock.
 */
module baud_generator #(parameter BAUD_RATE=115200)(
    input  wire clk50, reset,
    output wire baud
);

/* 
Ticks needed to divide the 50Mhz clk to the BAUD_RATE

ticks = 50Mhz / BAUD_RATE
      = 50_000_000 / 115_200
      = 434
*/
localparam BAUD_TICKS = 434;

// generate the baud signal
reg[8:0] ticks;
always @(posedge clk50) begin
    if (reset) begin
        ticks <= 0;
        baud  <= 0;
    end
    else if (ticks == BAUD_TICKS - 1) begin
        ticks <= 0;
        baud  <= ~baud;
    end
    else begin
        ticks <= ticks + 1;
        baud  <= baud;
    end
end

endmodule