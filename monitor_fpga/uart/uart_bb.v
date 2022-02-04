
module uart (
	clk_clk,
	reset_reset_n,
	uart_0_external_connection_rxd,
	uart_0_external_connection_txd,
	uart_0_irq_irq,
	uart_0_s1_address,
	uart_0_s1_begintransfer,
	uart_0_s1_chipselect,
	uart_0_s1_read_n,
	uart_0_s1_write_n,
	uart_0_s1_writedata,
	uart_0_s1_readdata);	

	input		clk_clk;
	input		reset_reset_n;
	input		uart_0_external_connection_rxd;
	output		uart_0_external_connection_txd;
	output		uart_0_irq_irq;
	input	[2:0]	uart_0_s1_address;
	input		uart_0_s1_begintransfer;
	input		uart_0_s1_chipselect;
	input		uart_0_s1_read_n;
	input		uart_0_s1_write_n;
	input	[15:0]	uart_0_s1_writedata;
	output	[15:0]	uart_0_s1_readdata;
endmodule
