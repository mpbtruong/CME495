module monitor_fpga(
    input clk, reset,
    output reset_flag
);

assign reset_flag = ~reset;

endmodule