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
	output reg dummy_1,dummy_2,dummy_3,	
	output reg [20:0] ref_clk_shft,
	output reg [16:0] pps_shft,
	output wire [19:0] ref_posedge,
	output reg [19:0] ref_posedge_hold,
	output wire [15:0] pps_posedge,
	output reg signed [24:0] clk_count,
	output reg signed [24:0] clk_count_neg,
	output reg signed [15:0] clk_err,
	output reg signed [15:0] clk_err_lst,
	output reg signed [15:0] total_error,
	output reg signed [15:0] err_change,
	output reg signed [15:0] phase_err,
	output reg signed [31:0] int_sum,
	output reg signed [15:0] smpl_count,
	output reg [3:0] dac_rdy,
	output wire locked,
	output reg pps_reset,
	output reg err_dir,

	
	output reg recov_pps,
	output reg signed [15:0] pid_out,
	output reg signed [15:0] int,
	output reg clk_err_dir,
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

always @ (posedge clk_200) ref_clk_shft = {ref_clk_shft[19:0],ref_clk};

always @ (posedge clk_200) pps_shft = {pps_shft[15:0],RECV_pps};

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
	if(SW[16]) sw_reset = count_reset;
	else sw_reset = clk_reset;
	
always @ (posedge ref_clk)
	if(clk_count == 24'd9_999_999) begin
		count_reset = 1'b1;
		end
	else 
		begin
		count_reset = 1'b0;
		end

// PPS Edge Detection
assign pps_posedge[0] = pps_shft[0] && ~pps_shft[1]; 
assign pps_posedge[1] = pps_shft[1] && ~pps_shft[2]; 
assign pps_posedge[2] = pps_shft[2] && ~pps_shft[3]; 
assign pps_posedge[3] = pps_shft[3] && ~pps_shft[4]; 
assign pps_posedge[4] = pps_shft[4] && ~pps_shft[5]; 
assign pps_posedge[5] = pps_shft[5] && ~pps_shft[6]; 
assign pps_posedge[6] = pps_shft[6] && ~pps_shft[7];
assign pps_posedge[7] = pps_shft[7] && ~pps_shft[8];
assign pps_posedge[8] = pps_shft[8] && ~pps_shft[9];
assign pps_posedge[9] = pps_shft[9] && ~pps_shft[10];
assign pps_posedge[10] = pps_shft[10] && ~pps_shft[11];
assign pps_posedge[11] = pps_shft[11] && ~pps_shft[12];
assign pps_posedge[12] = pps_shft[12] && ~pps_shft[13];
assign pps_posedge[13] = pps_shft[13] && ~pps_shft[14];
assign pps_posedge[14] = pps_shft[14] && ~pps_shft[15];
assign pps_posedge[15] = pps_shft[15] && ~pps_shft[16];                
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
assign ref_posedge[19] = ~ref_clk_shft[19] && ref_clk_shft[20];
always @ (posedge clk_200)
	if(!reset || !key_reset) ref_posedge_hold = 1'b0;
	else if(pps_posedge[0]) ref_posedge_hold = ref_posedge;


// ************************************* DPLL Ref Clock Counters ************************************* //

always @ (posedge ref_clk)
//	if(!reset || !key_reset) clk_count = 16'b0;
	if(sw_reset || pps_reset) begin
		clk_count <= 25'b0;
	end
	else clk_count = clk_count + 25'b1;

always @ (negedge ref_clk)
//	if(!reset || !key_reset) clk_count_neg = 16'b0;
	if(sw_reset || pps_reset) begin
		clk_count_neg <= 25'b0;
	end	
	else clk_count_neg = clk_count_neg + 25'b1;

always @ (posedge ref_clk)
	if(clk_count == 25'd10_000_000) recov_pps = 1'b1;
	else recov_pps = 1'b0;

// ************************************* DPPL Error Detection ************************************* //
always @ (posedge clk_200)
		if(!reset || !key_reset) phase_err = 0;
		else
			if(pps_posedge[1]) begin
				case(ref_posedge_hold)
					20'b0000_0000_0000_0000_0001: phase_err = 10;
					20'b0000_0000_0000_0000_0010: phase_err = 9;
					20'b0000_0000_0000_0000_0100: phase_err = 8;
					20'b0000_0000_0000_0000_1000: phase_err = 7;
					20'b0000_0000_0000_0001_0000: phase_err = 6;
					20'b0000_0000_0000_0010_0000: phase_err = 5;
					20'b0000_0000_0000_0100_0000: phase_err = 4;
					20'b0000_0000_0000_1000_0000: phase_err = 3;
					20'b0000_0000_0001_0000_0000: phase_err = 2;
					20'b0000_0000_0010_0000_0000: phase_err = 1;
					20'b0000_0000_0100_0000_0000: phase_err = 0;
					20'b0000_0000_1000_0000_0000: phase_err = -1;
					20'b0000_0001_0000_0000_0000: phase_err = -2;
					20'b0000_0010_0000_0000_0000: phase_err = -3;
					20'b0000_0100_0000_0000_0000: phase_err = -4;
					20'b0000_1000_0000_0000_0000: phase_err = -5;
					20'b0001_0000_0000_0000_0000: phase_err = -6;
					20'b0010_0000_0000_0000_0000: phase_err = -7;
					20'b0100_0000_0000_0000_0000: phase_err = -8;
					20'b1000_0000_0000_0000_0000: phase_err = -9;
				endcase
			end

//always @ (posedge clk_200)
//	if(!reset || !key_reset) clk_err = 16'b0;
//	else if(pps_posedge[1]) 
//	begin
//		if(!locked) 
//			begin
//				if(clk_count_neg < 10_000_000 && clk_count_neg > 5_000_000) clk_err <= (10_000_000 - clk_count_neg);
//				else if(clk_count_neg == 10_000_000) clk_err <= 0;
//				else clk_err <= -1*clk_count_neg;
//			end
//		else clk_err <= clk_err;
//		if(clk_err >= 0) err_dir <= 1'b1;
//		else err_dir <= 1'b0;
//	end
always @ (posedge clk_200)
	if(!reset || !key_reset) clk_err = 16'b0;
	else if(pps_posedge[1]) 
	begin
		if(!locked) 
			begin
				if(clk_count_neg == 0) clk_err <= 0;
				else if(clk_count_neg == 10_000_000) clk_err <= 1;
				else if(clk_count_neg < 10_000_000 && clk_count_neg > 5_000_000) clk_err <= (10_000_000 - clk_count_neg) + 1'b1;
				else clk_err <= -1*clk_count_neg;
			end
		else clk_err <= clk_err;
		if(clk_err >= 0) err_dir <= 1'b1;
		else err_dir <= 1'b0;
	end
	
reg signed [15:0] err_hold_1,err_hold_2;

// always @ (posedge clk_200)
// 	if(!reset || !key_reset) err_hold_1 = 16'b0;
// 	else if(pps_posedge[2])
// 			if(phase_err > 10 || phase_err < -9) begin
// 				if(clk_err > 50 || clk_err < -50) err_hold_1 = pd_shift[0];
// 				else err_hold_1 = (clk_err*16'sd20) + phase_err;
// 				end
// 			else begin
// 				if(clk_err > 50 || clk_err < -50) err_hold_1 = phase_err + (clk_err_lst*16'sd20);
// 				else err_hold_1 = (clk_err*16'sd20) + phase_err;
// 			end

always @ (posedge clk_200)
	if(!reset || !key_reset) err_hold_1 = 16'b0;
	else if(pps_posedge[2]) begin
		if(clk_err > 200 || clk_err < -200) err_hold_1 = err_hold_1;
		else err_hold_1 = clk_err;
	end

always @ (posedge clk_200)
	if(!reset || !key_reset) begin
		err_hold_2 <= 16'b0;
		err_change <= 16'b0;
	end
	else if(pps_posedge[3])begin
		err_change <= err_hold_2 - err_hold_1;
		if(err_change > 8 || err_change < -8) err_hold_2 <= err_hold_2;
		else err_hold_2 <= err_hold_1;
	end

always @ (posedge clk_200)
	if(!reset || !key_reset) total_error = 16'b0;
	else if(pps_posedge[4]) begin
		if(err_hold_2 > 200 || err_hold_2 < -200) total_error = total_error;
		else if(phase_err == 10) begin
				if(err_dir == 1'b1) total_error <= (err_hold_2*16'sd20) + 16'sd10;
				else total_error <= (err_hold_2*16'sd20) + 16'sd10;
			end
			else total_error <= (err_hold_2*16'sd20) + phase_err;
		end

// Combinational Locked Detector
assign locked = ref_posedge[0] && pps_posedge[0];

// ************************************* DPLL PID Controller ************************************* //

always @ (posedge clk_200)
	if(!reset || !key_reset) begin
		int_sum <= 32'b0;
		smpl_count <= 16'b0;
	end
	else if(pps_posedge[6]) begin
		int_sum <= int_sum + total_error;
		smpl_count <= smpl_count +1'b1;
	end
	
always @ (posedge clk_200)
	if(!reset || !key_reset)pid_out <= 16'b0;
	else if(pps_posedge[7]) begin 
//	   pid_out <= {total_error[15],total_error[15:1]} + {total_error[15],total_error[15],total_error[15:2]} + {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:8]};// + {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:11]};
		pid_out <= total_error + {total_error[15],total_error[15],total_error[15:2]} + {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:8]} + {int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15],int[15:10]};
	end   

always @ (posedge clk_200)
	if(!reset || !key_reset) DAC_val = DAC_reset;
	else if(pps_posedge[8]) DAC_val = DAC_val + pid_out;

always @ (posedge clk_200)
	if(pps_posedge[9]) begin
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
	.reg127(total_error[15:0]),
	.reg126(pid_out),
	.reg125(DAC_val),
	// .reg124(int),
	.reg124(int_sum),
	.reg0(w_reset)
);

endmodule