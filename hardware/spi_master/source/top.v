module top(
	// FPGA I/O
	input wire CLOCK_50,
	input wire [17:0] SW,
	input wire [5:0] KEY,
	output reg [17:0] LEDR,
	output reg [7:0] LEDG,

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
	output reg [31:0] clk_count,
	output reg clk_reset,
	output reg signed [15:0] phase_err,
	output reg phase_dir,
	output reg flag,flag_last,
	output reg [15:0] DAC_val,
	output reg signed [15:0] int,
	output reg signed [15:0] pid_out,
	output reg signed [31:0] phase_accum,
	output wire locked,
	output reg recov_pps
);

wire sys_clk;
wire wclk_200;
reg ref_clk;
reg reset;
reg valid;
reg [15:0] count;

reg [7:0] SPI_byte;

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
		LEDR[17:1] = 17'b10010110100110110;
		DAC_val = SW[15:0];
		reset = SW[17];
		ref_clk = SMA_CLKIN;
		clk_200 = wclk_200;
	end

reg tx_start;
// ************************************* DAC SPI Control ************************************* //
//always @ (posedge CLOCK_50)
//	if(data_rdy) tx_start = 1'b1;
//	else if(count >=1400) tx_start = 1'b0;

//always @ (posedge CLOCK_50)
//	if(data_rdy) count = 16'b0;
//	else if(tx_start) count = count + 1'b1;
always @ (posedge CLOCK_50)
	count = count + 1'b1;

always @ (posedge CLOCK_50)
	if(count == 16'd0 || count == 16'd550) valid = 1;
	else valid = 0;

always @ (posedge CLOCK_50)
	if(count == 16'd0) SPI_byte = DAC_val[15:8];
	else if(count == 16'd550) SPI_byte = DAC_val[7:0];


// ************************************* DPPL Phase Detector ************************************* //
// 9E23
// Phase Accumulator
always @ (posedge ref_clk)
	if(clk_reset) clk_count = 32'b1;
	else clk_count = clk_count + 32'b1;

always @ (posedge ref_clk)
	if(clk_count == 10_000_000) recov_pps = 1'b1;
	else recov_pps = 1'b0;

// Asynchronus to Synchronus Reset Logic
always @ (posedge ref_clk)
	begin
		flag_last = flag;
		flag = RECV_pps;
		if(flag && !flag_last) clk_reset = 1'b1;
		else clk_reset = 1'b0;
	end

// Phase Error Calculation
always @ (posedge RECV_pps)
	phase_err <= 10_000_000 - clk_count;

always @ (posedge RECV_pps)
	if(clk_count > 10_000_000) phase_dir = 1'b0;
	else phase_dir = 1'b1;

reg ref_clk_in, ref_clk_out;
reg pps_clk_in, pps_clk_out;

wire ref_posedge, pps_posedge;

always @ (posedge clk_200)
	begin
		ref_clk_in = ref_clk;
		pps_clk_in = RECV_pps;
	end

always @ (posedge clk_200)
	begin
		ref_clk_out = ref_clk_in;
		pps_clk_out = pps_clk_in;
	end

assign ref_posedge = (~ref_clk_out && ref_clk_in);
assign pps_posedge = (~pps_clk_out && pps_clk_in);

assign locked = ref_posedge && pps_posedge;


// ************************************* DPPL PID/Filter ************************************* //

parameter pid_p = 32'd1;
parameter pid_i = 32'd1;
reg int_rdy;
reg signed [31:0] pd_shift[9:0];

always @ (posedge ref_clk)
	if(clk_reset) 
		begin
			pd_shift[9] <= pd_shift[8];
			pd_shift[8] <= pd_shift[7];
			pd_shift[7] <= pd_shift[6];
			pd_shift[6] <= pd_shift[5];
			pd_shift[5] <= pd_shift[4];
			pd_shift[4] <= pd_shift[3];
			pd_shift[3] <= pd_shift[2];
			pd_shift[2] <= pd_shift[1];
			pd_shift[1] <= pd_shift[0];
			if(phase_err > 100 || phase_err < -100 && !locked) pd_shift[0] <= 0;
			else pd_shift[0] <= phase_err;
			int <= pd_shift[9] + pd_shift[8] + pd_shift[7] + pd_shift[6] + pd_shift[5] + pd_shift[4] + pd_shift[3] + pd_shift[2] + pd_shift[1] + pd_shift[0];
			int_rdy <= 1'b1;
		end
	else int_rdy = 1'b0;

always @ (posedge ref_clk)
	if(int_rdy) pid_out = pid_p * phase_err + pid_i * int;

//always @ (posedge ref_clk)
//	if(int_rdy) data_rdy = 1'b1;
//	else data_rdy = 1'b0;

always @ (posedge ref_clk)
	if(!KEY[0]) phase_accum = 0;
	else if(int_rdy) phase_accum = phase_accum + pd_shift[0];

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

PLL_200 p1(
	.inclk0(CLOCK_50),
	.c0(wclk_200)
	);
endmodule  