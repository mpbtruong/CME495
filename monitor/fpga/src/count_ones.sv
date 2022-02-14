
module count_ones
#(parameter BITWIDTH = 8)(
    input  wire[`BITWIDTH-1:0]         signal, // signal to count 1s
    output wire[$clog2(`BITWIDTH)-1:0] ones    // # of 1s in signal
);

integer i;
always @(*) begin
    ones = 0;
    for (i = 0; i < `BITWIDTH; i += 1) begin
        if (signal[i]) ones += 1;
    end
end

endmodule