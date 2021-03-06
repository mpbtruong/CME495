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
	
	output reg [19:0] ref_clk_shft,
	output reg [1:0] pps_shft,
	output wire [18:0] ref_posedge,
	output reg [18:0] ref_posedge_hold,
	output wire pps_posedge,
	output reg signed [31:0] clk_count,
	output reg signed [31:0] clk_count_neg,
	output reg signed [31:0] clk_err,
	output reg signed [31:0] clk_err_lst,
	output reg signed [15:0] phase_err,
	output reg [3:0] dac_rdy,
	output wire locked,
	output reg pps_reset,

		
	output reg recov_pps,
	output reg signed [15:0] pid_out,
	output reg signed [31:0] phase_accum,
	output reg signed [15:0] int,
	output reg signed [31:0] prop_err,
	output reg signed [31:0] cycle_error,
	output reg clk_err_dir,
	output reg debug_clk,
	output reg reset
);
wire w_UART_CTS,w_UART_TXD;
wire w_reset;

reg ref_clk;
reg key_reset;

initial DAC_val = 16'h9E23;
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
	if(dac_rdy) count = 32'b0;
	else if(tx_start) count = count + 1'b1;
	
always @ (posedge CLOCK_50)
	if(count == 16'd0 || count == 16'd550) valid = 1;
	else valid = 0;

always @ (posedge CLOCK_50)
	if(count == 16'd0) SPI_byte = DAC_val[15:8];
	else if(count == 16'd550) SPI_byte = DAC_val[7:0];

// ************************************* DPPL Phase Detector ************************************* //

always @ (posedge clk_200) ref_clk_shft = {ref_clk_shft[18:0],ref_clk};

always @ (posedge clk_200)
	if(!reset || !key_reset) pps_reset = 1'b1;
	else if(pps_posedge) pps_reset = 1'b0;

always @ (posedge clk_200) 
	begin
	pps_shft[1] <= pps_shft[0];
	pps_shft[0] <= RECV_pps;
	end

assign pps_posedge = pps_shft[0] && ~pps_shft[1]; 

// Ref Clock Timing Array
assign ref_posedge[0] = ~ref_clk_shft[0] && ref_clk_shft[1];
assign ref_posedge[1] = ~ref_clk_shft[1] && ref_clk_shft[2];
assign ref_posedge[2] = ~ref_clk_shft[2] && ref_clk_shft[3];
assign ref_posedge[3] = ~ref_clk_shft[3] && ref_clk_shft[4];
assign ref_posedge[4] = ~ref_clk_shft[4] && ref_clk_shft[5];
assign ref_posedge[5] = ~ref_clk_shft[5] && ref_clk_shft[6];
assign ref_posedge[6] = ~ref_clk_shft[6] && ref_clk_shft[7];
assign ref_posedge[7] = ~ref_clk_shft[7] && ref_clk_shft[8];
assign ref_posedge[8] = ~ref_clk_shft[8] && ref_clk_shft[9];
assign ref_posedge[9] = ~ref_clk_shft[9] && ref_clk_shft[10];
assign ref_posedge[10] = ~ref_clk_shft[10] && ref_clk_shft[11];
assign ref_posedge[11] = ~ref_clk_shft[11] && ref_clk_shft[12];
assign ref_posedge[12] = ~ref_clk_shft[12] && ref_clk_shft[13];
assign ref_posedge[13] = ~ref_clk_shft[13] && ref_clk_shft[14];
assign ref_posedge[14] = ~ref_clk_shft[14] && ref_clk_shft[15];
assign ref_posedge[15] = ~ref_clk_shft[15] && ref_clk_shft[16];
assign ref_posedge[16] = ~ref_clk_shft[16] && ref_clk_shft[17];
assign ref_posedge[17] = ~ref_clk_shft[17] && ref_clk_shft[18];
assign ref_posedge[18] = ~ref_clk_shft[18] && ref_clk_shft[19];

always @ *
	if(SW[16]) sw_reset = count_reset;
	else sw_reset = clk_reset;
	
always @ (posedge ref_clk)
	if(clk_count == 32'd9_999_999) begin
		count_reset = 1'b1;
		end
	else 
		begin
		count_reset = 1'b0;
		end

always @ (posedge ref_clk)
//	if(!reset || !key_reset) clk_count = 32'b0;
	if(sw_reset || pps_reset) begin
		if(SW[16]) clk_count = 32'b0;
		else clk_count = 32'b1; 
		end	
	else clk_count = clk_count + 32'b1;

always @ (negedge ref_clk)
//	if(!reset || !key_reset) clk_count_neg = 32'b0;
	if(sw_reset || pps_reset) begin
		if(SW[16]) clk_count_neg = 32'b0;
		else clk_count_neg = 32'b1; 
		end	
	else clk_count_neg = clk_count_neg + 32'b1;

always @ (posedge ref_clk)
	if(clk_count == 9_999_999) recov_pps = 1'b1;
	else recov_pps = 1'b0;
// Asynchronus to Synchronus Reset Logic
always @ (posedge ref_clk)
	begin
		flag_last = flag;
		flag = RECV_pps;
		if(flag && !flag_last && !SW[6]) clk_reset = 1'b1;
		else clk_reset = 1'b0;
	end
	
always @ (posedge clk_200)
	 if(pps_posedge) ref_posedge_hold = ref_posedge;

always @ (posedge clk_200)
	if(pps_posedge) data_rdy = 1'b1;
	else data_rdy = 1'b0;

always @ (posedge clk_200)
		if(!reset || !key_reset) phase_err = 0;
		else 
			case(ref_posedge_hold)
			19'b000_0000_0000_0000_0000: phase_err = -9;
			19'b000_0000_0000_0000_0001: phase_err = 10;
			19'b000_0000_0000_0000_0010: phase_err = 9;
			19'b000_0000_0000_0000_0100: phase_err = 8;
			19'b000_0000_0000_0000_1000: phase_err = 7;
			19'b000_0000_0000_0001_0000: phase_err = 6;
			19'b000_0000_0000_0010_0000: phase_err = 5;
			19'b000_0000_0000_0100_0000: phase_err = 4;
			19'b000_0000_0000_1000_0000: phase_err = 3;
			19'b000_0000_0001_0000_0000: phase_err = 2;
			19'b000_0000_0010_0000_0000: phase_err = 1;
			19'b000_0000_0100_0000_0000: phase_err = 0;
			19'b000_0000_1000_0000_0000: phase_err = -1;
			19'b000_0001_0000_0000_0000: phase_err = -2;
			19'b000_0010_0000_0000_0000: phase_err = -3;
			19'b000_0100_0000_0000_0000: phase_err = -4;
			19'b000_1000_0000_0000_0000: phase_err = -5;
			19'b001_0000_0000_0000_0000: phase_err = -6;
			19'b010_0000_0000_0000_0000: phase_err = -7;
			19'b100_0000_0000_0000_0000: phase_err = -8;
			endcase

reg int_rdy;
parameter pid_p = 32'd1;
parameter pid_i = 32'd1;
reg signed [31:0] pd_shift[7:0];

assign locked = ref_posedge[0] && pps_posedge;

// ************************************* DPPL PID Controller ************************************* //
always @ (posedge clk_200)
	if(!reset || !key_reset) clk_err_lst = 32'b0;
	else if(pps_posedge) begin
		if(clk_err > 500 || clk_err < -500) clk_err_lst = clk_err_lst;
		else clk_err_lst = clk_err;
	end

always @ (posedge clk_200)
	if(!reset || !key_reset) clk_err = 32'b0;
	else if(data_rdy) 
	begin
		if(!locked) 
			begin
				if(clk_count_neg < 10_000_000 && clk_count_neg > 100_000) clk_err = (10_000_000 - clk_count_neg);
				else if(clk_count_neg == 10_000_000) clk_err = 0;
				else clk_err = -1*clk_count_neg - 1'b1;
			end
		else clk_err = clk_err;
	end

always @ (posedge clk_200)
	if(!reset || !key_reset) begin
			pd_shift[7] <= 32'b0;
			pd_shift[6] <= 32'b0;
			pd_shift[5] <= 32'b0;
			pd_shift[4] <= 32'b0;
			pd_shift[3] <= 32'b0;
			pd_shift[2] <= 32'b0;
			pd_shift[1] <= 32'b0;
			pd_shift[0] <= 32'b0;
			int <= 32'b0;
		end
	else if(data_rdy)
		begin
			pd_shift[7] <= pd_shift[6];
			pd_shift[6] <= pd_shift[5];
			pd_shift[5] <= pd_shift[4];
			pd_shift[4] <= pd_shift[3];
			pd_shift[3] <= pd_shift[2];
			pd_shift[2] <= pd_shift[1];
			pd_shift[1] <= pd_shift[0];
			if(phase_err > 10 || phase_err < -10) pd_shift[0] <= pd_shift[0];
			else pd_shift[0] <= phase_err;
//			if(phase_err > 10 || phase_err < -9) begin
//				if(clk_err > 50 || clk_err < -50) pd_shift[0] <= pd_shift[0];
//				else pd_shift[0] <= (clk_err*32'sd20) + phase_err;
//				end
//			else begin
//				if(clk_err > 50 || clk_err < -50) pd_shift[0] <= phase_err + (clk_err_lst*32'sd20);
//				else pd_shift[0] <= (clk_err*32'sd20) + phase_err;
//			end
			int <= pd_shift[7] + pd_shift[6] + pd_shift[5] + pd_shift[4] + pd_shift[3] + pd_shift[2] + pd_shift[1] + pd_shift[0];
			int_rdy <= 1'b1;
		end
	else int_rdy = 1'b0;
	
always @ (posedge clk_200)
	if(!reset || !key_reset)	prop_err = 0;
	else if(data_rdy) begin
		if(phase_err > 10 || phase_err < -10) begin
				if(clk_err > 500 || clk_err < -500) prop_err = prop_err;
				else prop_err = (clk_err*32'sd20) + pd_shift[0];
				end
			else begin
				if(clk_err > 500 || clk_err < -500) prop_err = phase_err + (clk_err_lst*32'sd20);
				else prop_err = (clk_err*32'sd20) + phase_err;
			end
		end
		
reg pid_rdy;
always @ (posedge clk_200)
	if(!reset || !key_reset) pid_out = 32'b0;
	else if(int_rdy) pid_out = prop_err + {int[15],int[15],int[15],int[15],int[15:4]};
		
always @ (posedge clk_200)
	if(int_rdy) pid_rdy <= 1'b1;
	else pid_rdy <= 1'b0;
	
always @ (posedge clk_200)
	if(!reset || !key_reset) DAC_val = 16'h9E23;
	else if(pid_rdy) begin
		if(pid_out > 1000 || pid_out < -1000)begin
			if(clk_err > 100) DAC_val = DAC_val+ pid_out;
			else DAC_val = DAC_val;
		end
		else DAC_val = DAC_val + pid_out;
	end

//always @ (posedge clk_200)
//	if(!reset || !key_reset) DAC_val = 16'h9E23;
//	else if(pid_rdy) DAC_val = DAC_val + pid_out;
	
always @ (posedge clk_200)
	if(pid_rdy) begin
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
	.reg127(prop_err[15:0]),
	.reg126(pid_out),
	.reg125(DAC_val),
	.reg124(int),
	.reg0(w_reset)
);
endmodule
