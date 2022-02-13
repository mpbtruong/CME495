module monitor_fpga(
    input  wire clk, 
    input  wire reset,
    output wire reset_flag,

    // UART
    input  wire uart_rxd, // receiver
    output wire uart_txd, // transmitter
    input  wire uart_cts, // clear to send
    output wire uart_rts  // request to send
);

assign reset_flag = ~reset;



endmodule