module top(
	// FPGA I/O
	input wire CLOCK_50,
	input wire [17:0] SW,
	input wire [5:0] KEY,
	output reg [17:0] LEDR,
	output reg [7:0] LEDG,
	// UART IO
	input wire UART_RXD,
	output reg UART_TXD,
	input wire UART_RTS,
	output reg UART_CTS,
	
	// PCB I/O
	input wire RECV_tx_sdo,
	input wire RECV_pps,
	input wire SMA_CLKIN,
	output wire DAC_CS_n,
	output wire DAC_clk,
	output wire DAC_data,
	output reg RECV_rx_sdi,
	output reg RECV_sck,
	output reg RECV_scl,
	output reg RECV_sda,
	output reg RECV_int,
	output reg RECV_rst_n,

	// Design I/0
	output reg clk_200,
	
	output reg [15:0] DAC_val,
	output reg [15:0] count,
	output reg [7:0] SPI_byte,
	output reg valid,
	output reg tx_start,
	
	output reg [1:0] pps_shft,
	output reg [1:0] ref_pps_shft,
	output reg [6:0] pps_negedge_shft,
	
	output wire ref_pps_posedge,
	output wire pps_posedge,
	output wire [5:0] pps_negedge,
	
	output reg signed [24:0] clk_count,
	output reg [31:0] count_200,
	output reg signed [31:0] pps_count,
	output reg signed [31:0] ref_count,
	
	output reg signed [31:0] total_error,
	output reg signed [31:0] prop_error,
	output reg signed [31:0] int,
	output reg signed [15:0] pid_out,
	output reg error_dir,
	output reg [3:0] dac_rdy,
	output wire locked,
	output reg pps_reset,

	output reg recov_pps,
	output reg reset
);
wire w_UART_CTS,w_UART_TXD;
wire w_reset;
//parameter DAC_reset = 16'h0;
//parameter DAC_reset = 16'h7FFF;
parameter DAC_reset = 16'h9E23;
reg ref_clk;
reg key_reset;
//16'h9E23
initial DAC_val = DAC_reset;
//initial DAC_val = 16'h0;
reg flag,flag_last,clk_reset,count_reset;
reg sw_reset;
reg data_rdy;

// ************************************* Design Setup ************************************* //
always @ *
	begin
		RECV_rx_sdi = 1'b0;
		RECV_sck = 1'b0;
		RECV_scl = 1'b0;
		RECV_sck = 1'b0;
		RECV_sda = 1'b0;
		RECV_int = 1'b0;
		RECV_rst_n = 1'b1;
		LEDR[0] = RECV_pps;
		LEDR[1] = recov_pps;
		reset = w_reset;
		ref_clk = SMA_CLKIN;
		clk_200 = wclk_200;
		UART_TXD = w_UART_TXD;
		UART_CTS = w_UART_CTS;
		key_reset = KEY[0];
	end

// ************************************* DAC SPI Control ************************************* //

always @ (posedge CLOCK_50)
	if(dac_rdy) tx_start = 1'b1;
	else if(count == 16'd600) tx_start = 1'b0;

always @ (posedge CLOCK_50)
	if(dac_rdy) count = 16'b0;
	else if(tx_start) count = count + 1'b1;
	
always @ (posedge CLOCK_50)
	if(count == 16'd0 || count == 16'd550) valid = 1;
	else valid = 0;

always @ (posedge CLOCK_50)
	if(count == 16'd0) SPI_byte = DAC_val[15:8];
	else if(count == 16'd550) SPI_byte = DAC_val[7:0];

// ************************************* DPPL Phase Detector ************************************* //
always @ (posedge clk_200) pps_shft = {pps_shft[0],RECV_pps};

always @ (posedge clk_200) ref_pps_shft = {ref_pps_shft[0],recov_pps};
 
always @ (posedge clk_200) pps_negedge_shft = {pps_negedge_shft[5:0],RECV_pps};

// Asynchronus to Synchronus Reset Logic
always @ (posedge clk_200)
	if(!reset || !key_reset) pps_reset = 1'b1;
	else if(pps_posedge) pps_reset = 1'b0;

always @ (posedge ref_clk)
	begin
		flag_last = flag;
		flag = RECV_pps;
		if(flag && !flag_last && !SW[6]) clk_reset = 1'b1;
		else clk_reset = 1'b0;
	end

always @ *
	sw_reset = count_reset;
	
always @ (posedge ref_clk)
	if(clk_count == 24'd9_999_999) count_reset = 1'b1;
	else count_reset = 1'b0;
	
// PPS Edge Detection
assign pps_posedge = pps_shft[0] && ~pps_shft[1]; 
assign ref_pps_posedge = ref_pps_shft[0] && ~ref_pps_shft[1]; 

assign pps_negedge[0] = ~pps_negedge_shft[0] && pps_negedge_shft[1]; 
assign pps_negedge[1] = ~pps_negedge_shft[1] && pps_negedge_shft[2]; 
assign pps_negedge[2] = ~pps_negedge_shft[2] && pps_negedge_shft[3]; 
assign pps_negedge[3] = ~pps_negedge_shft[3] && pps_negedge_shft[4]; 
assign pps_negedge[4] = ~pps_negedge_shft[4] && pps_negedge_shft[5]; 
assign pps_negedge[5] = ~pps_negedge_shft[5] && pps_negedge_shft[6]; 

// ************************************* DPLL Ref Clock Counters ************************************* //

always @ (posedge ref_clk)
//	if(!reset || !key_reset) clk_count = 16'b0;
	if(sw_reset || pps_reset) begin
		clk_count <= 25'b0;
	end
	else clk_count = clk_count + 25'b1;

always @ (posedge ref_clk)
	if(clk_count == 25'd10_000_000) recov_pps = 1'b1;
	else if(clk_count == 25'd1_000_000) recov_pps = 1'b0;
	
always @ (posedge clk_200) count_200 = count_200 + 32'b1;

// ************************************* DPPL Error Detection ************************************* //

always @ (posedge clk_200)
	if(pps_posedge) pps_count = count_200;

always @ (posedge clk_200)
	if(ref_pps_posedge) ref_count = count_200;

always @ (posedge clk_200)
	if(!reset || !key_reset) total_error <= 32'b0;
	else if(pps_negedge[0]) begin
		if(pps_count > ref_count) total_error <= pps_count - ref_count;
		else if(pps_count < ref_count) total_error <= ref_count - pps_count;
		else if(pps_count == ref_count) total_error <= 32'b0;
	end

always @ (posedge clk_200)
	if(pps_negedge[0]) begin
		if(pps_count < ref_count) error_dir = 1'b1;
		else if(pps_count >= ref_count) error_dir = 1'b0;
	end

// ************************************* DPLL PID Controller ************************************* //
always @ (posedge clk_200)
	if(!reset || !key_reset) prop_error = 32'b0;
	else if(pps_negedge[1]) begin
		if(total_error < 50_000) begin
			if(error_dir) prop_error = total_error;
			else prop_error = -1*total_error;
		end
		else prop_error = prop_error;
	end
	
always @ (posedge clk_200)
	if(!reset || !key_reset) int = 32'b0;
	else if(pps_negedge[2]) int = int + prop_error;

reg signed [15:0] prop_1;
reg signed [15:0] prop_2;
reg signed [15:0] prop_4;
reg signed [15:0] prop_8;
reg signed [15:0] prop_16;

reg signed [15:0] int_1;
reg signed [15:0] int_2;
reg signed [15:0] int_3;
reg signed [15:0] int_4;
reg signed [15:0] int_5;
reg signed [15:0] int_6;
reg signed [15:0] int_7;
reg signed [15:0] int_8;
reg signed [15:0] int_9;
reg signed [15:0] int_10;
reg signed [15:0] int_11;
reg signed [15:0] int_12;
reg signed [15:0] int_13;

always @ *
	begin
		if(SW[0]) prop_1 = prop_error;
		else prop_1 = 16'b0;
		if(SW[1]) prop_2 = {prop_error[15],prop_error[15:1]};
		else prop_2 = 16'b0;
		if(SW[2]) prop_4 = {prop_error[15],prop_error[15],prop_error[15:2]};
		else prop_4 = 16'b0;
		if(SW[3]) prop_8 = {prop_error[15],prop_error[15],prop_error[15],prop_error[15:3]};
		else prop_8 = 16'b0;
		if(SW[4]) prop_16 = {prop_error[15],prop_error[15],prop_error[15],prop_error[15],prop_error[15:4]};
		else prop_16 = 16'b0;
	end
	
always @ *
	begin
		if(SW[5]) int_1 = int;
		else int_1 = 16'b0;
		if(SW[6]) int_2 = {int[15],int[15:1]};
		else int_2 = 16'b0;
		if(SW[7]) int_3 = {int[15],int[15],int[15:2]};
		else int_3 = 16'b0;
		if(SW[8]) int_4 = {int[15],int[15],int[15],int[15:3]};
		else int_4 = 16'b0;
		if(SW[9]) int_5 = {int[15],int[15],int[15],int[15],int[15:4]};
		else int_5 = 16'b0;
		if(SW[10]) int_6 = {int[15],int[15],int[15],int[15],int[15],int[15:5]};
		else int_6 = 16'b0;
		if(SW[11]) int_7 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15:6]};
		else int_7 = 16'b0;
		if(SW[12]) int_8 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:7]};
		else int_8 = 16'b0;
		if(SW[13]) int_9 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:8]};
		else int_9 = 16'b0;
		if(SW[14]) int_10 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:9]};
		else int_10 = 16'b0;
		if(SW[15]) int_11 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:10]};
		else int_11 = 16'b0;
		if(SW[16]) int_12 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:11]};
		else int_12 = 16'b0;
		if(SW[17]) int_13 = {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:12]};
		else int_13 = 16'b0;
	end
	
always @ (posedge clk_200)
	if(!reset || !key_reset) pid_out <= 16'b0;
	else if(pps_negedge[3]) pid_out <= prop_1 + prop_2 + prop_4 + prop_8 + prop_16 + int_1 + int_2 + int_3 + int_4 + int_5 + int_6 + int_7 + int_8 + int_9 + int_10 + int_11 + int_12 + int_13;
	
always @ (posedge clk_200)
	if(!reset || !key_reset) DAC_val = DAC_reset;
	else if(pps_negedge[4]) begin
		if(pid_out < 1000 && pid_out > -1000) DAC_val = DAC_val + pid_out;
		else DAC_val = DAC_val;
	end
reg signed [15:0] pid_out_mon;
always @ (posedge clk_200) 
	if(!reset || !key_reset) pid_out_mon = 16'b0;
	else if(pps_negedge[4]) begin
	if(pid_out < 1000 && pid_out > -1000) pid_out_mon = pid_out;
	else pid_out_mon = pid_out;
	end
	
always @ (posedge clk_200)
	if(pps_negedge[5]) begin
		dac_rdy[3] <= dac_rdy[2];
		dac_rdy[2] <= dac_rdy[1];
		dac_rdy[1] <= dac_rdy[0];
		dac_rdy[0] <= 1'b1;
		end
	else
		begin
		dac_rdy[3] <= dac_rdy[2];
		dac_rdy[2] <= dac_rdy[1];
		dac_rdy[1] <= dac_rdy[0];
		dac_rdy[0] <= 1'b0;
		end

PLL_200MHz p1(
	.inclk0(CLOCK_50),
	.c0(wclk_200)
);

SPI_Master_With_Single_CS u1(
	.i_Rst_L(reset),
	.i_Clk(CLOCK_50),
	.i_TX_Count(2),
	.i_TX_Byte(SPI_byte),
	.i_TX_DV(valid),
	.o_TX_Ready(TX_Ready),
	.o_SPI_Clk(DAC_clk),
	.o_SPI_MOSI(DAC_data),
	.o_SPI_CS_n(DAC_CS_n)
);

monitor_top t1(
	.clk50(CLOCK_50),
	.reset(~reset),
	.uart_rxd(UART_RXD),
	.uart_txd(w_UART_TXD),
	.uart_rts(UART_RTS),
	.uart_cts(w_UART_CTS),
	.reg127(prop_error[15:0]),
	.reg126(pid_out_mon),
	.reg125(DAC_val),
	.reg124(int),
	.reg0(w_reset)
);

endmodule