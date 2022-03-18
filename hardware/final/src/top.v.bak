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
	
	output reg [15:0] DAC_val,
	output reg [15:0] count,
	output reg [7:0] SPI_byte,
	output reg valid,
	
	output reg [19:0] ref_clk_shft,
	output reg [1:0] pps_shft,
	output wire [18:0] ref_posedge,
	output reg [18:0] ref_posedge_hold,
	output wire pps_posedge,
	output reg [31:0] clk_count,
	output reg signed [15:0] phase_err,
	
	output reg signed [15:0] pid_out,
	output reg signed [31:0] phase_accum,
	output reg signed [15:0] int,
	
	output reg debug_clk
);

reg ref_clk;
reg reset;
initial DAC_val = 16'h9E23;
(* noprune *) reg [15:0] phase [0:99];

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
		LEDR[5:1] = 4'b1001;
		reset = SW[17];
		ref_clk = SMA_CLKIN;
		clk_200 = wclk_200;
	end
	
// ************************************* DAC SPI Control ************************************* //
always @ (posedge CLOCK_50)
	count = count + 1'b1;

always @ (posedge CLOCK_50)
	if(count == 16'd0 || count == 16'd550) valid = 1;
	else valid = 0;

always @ (posedge CLOCK_50)
	if(count == 16'd0) SPI_byte = DAC_val[15:8];
	else if(count == 16'd550) SPI_byte = DAC_val[7:0];

// ************************************* DPPL Phase Detector ************************************* //

always @ (posedge clk_200) ref_clk_shft = {ref_clk_shft[18:0],ref_clk};

always @ (posedge clk_200) 
	begin
	pps_shft[1] <= pps_shft[0];
	pps_shft[0] <= RECV_pps;
	end

assign pps_posedge = pps_shft[0] && ~pps_shft[1]; 

//assign ref_posedge = {ref_clk_shft[18:0] ~&& ref_clk_shft[19:1]};
assign ref_posedge[0] = ref_clk_shft[0] && ~ref_clk_shft[1];
assign ref_posedge[1] = ref_clk_shft[1] && ~ref_clk_shft[2];
assign ref_posedge[2] = ref_clk_shft[2] && ~ref_clk_shft[3];
assign ref_posedge[3] = ref_clk_shft[3] && ~ref_clk_shft[4];
assign ref_posedge[4] = ref_clk_shft[4] && ~ref_clk_shft[5];
assign ref_posedge[5] = ref_clk_shft[5] && ~ref_clk_shft[6];
assign ref_posedge[6] = ref_clk_shft[6] && ~ref_clk_shft[7];
assign ref_posedge[7] = ref_clk_shft[7] && ~ref_clk_shft[8];
assign ref_posedge[8] = ref_clk_shft[8] && ~ref_clk_shft[9];
assign ref_posedge[9] = ref_clk_shft[9] && ~ref_clk_shft[10];
assign ref_posedge[10] = ref_clk_shft[10] && ~ref_clk_shft[11];
assign ref_posedge[11] = ref_clk_shft[11] && ~ref_clk_shft[12];
assign ref_posedge[12] = ref_clk_shft[12] && ~ref_clk_shft[13];
assign ref_posedge[13] = ref_clk_shft[13] && ~ref_clk_shft[14];
assign ref_posedge[14] = ref_clk_shft[14] && ~ref_clk_shft[15];
assign ref_posedge[15] = ref_clk_shft[15] && ~ref_clk_shft[16];
assign ref_posedge[16] = ref_clk_shft[16] && ~ref_clk_shft[17];
assign ref_posedge[17] = ref_clk_shft[17] && ~ref_clk_shft[18];
assign ref_posedge[18] = ref_clk_shft[18] && ~ref_clk_shft[19];


always@*
	debug_clk <= clk_200;

reg data_rdy;
always @ (posedge clk_200)
	 if(pps_posedge) ref_posedge_hold = ref_posedge;

always @ (posedge clk_200)
	if(pps_posedge) data_rdy = 1'b1;
	else data_rdy = 1'b0;

always @ (posedge clk_200)
		case(ref_posedge_hold)
		19'b000_0000_0000_0000_0000: phase_err = 1;
		19'b000_0000_0000_0000_0001: phase_err = 0;
		19'b000_0000_0000_0000_0010: phase_err = -1;
		19'b000_0000_0000_0000_0100: phase_err = -2;
		19'b000_0000_0000_0000_1000: phase_err = -3;
		19'b000_0000_0000_0001_0000: phase_err = -4;
		19'b000_0000_0000_0010_0000: phase_err = -5;
		19'b000_0000_0000_0100_0000: phase_err = -6;
		19'b000_0000_0000_1000_0000: phase_err = -7;
		19'b000_0000_0001_0000_0000: phase_err = -8;
		19'b000_0000_0010_0000_0000: phase_err = -9;
		19'b000_0000_0100_0000_0000: phase_err = 10;
		19'b000_0000_1000_0000_0000: phase_err = 9;
		19'b000_0001_0000_0000_0000: phase_err = 8;
		19'b000_0010_0000_0000_0000: phase_err = 7;
		19'b000_0100_0000_0000_0000: phase_err = 6;
		19'b000_1000_0000_0000_0000: phase_err = 5;
		19'b001_0000_0000_0000_0000: phase_err = 4;
		19'b010_0000_0000_0000_0000: phase_err = 3;
		19'b100_0000_0000_0000_0000: phase_err = 2;
		endcase

reg int_rdy;
parameter pid_p = 32'd1;
parameter pid_i = 32'd1;
reg signed [31:0] pd_shift[7:0];

always @ (posedge clk_200)
	if(data_rdy)
		begin
			pd_shift[7] <= pd_shift[6];
			pd_shift[6] <= pd_shift[5];
			pd_shift[5] <= pd_shift[4];
			pd_shift[4] <= pd_shift[3];
			pd_shift[3] <= pd_shift[2];
			pd_shift[2] <= pd_shift[1];
			pd_shift[1] <= pd_shift[0];
			if(phase_err > 100 || phase_err < -100) pd_shift[0] <= 0;
			else pd_shift[0] <= phase_err;
			int <= pd_shift[7] + pd_shift[6] + pd_shift[5] + pd_shift[4] + pd_shift[3] + pd_shift[2] + pd_shift[1] + pd_shift[0];
			int_rdy <= 1'b1;
		end
	else int_rdy = 1'b0;
	
reg pid_rdy;
always @ (posedge clk_200)
	if(int_rdy) 
	begin
		pid_out <= pid_p * phase_err + {int[15],int[15],int[15],int[15],int[15:4]};
		pid_rdy <=1'b1;
	end
	else pid_rdy <= 1'b0;

always @ (posedge clk_200)
	if(pid_rdy) DAC_val = DAC_val + pid_out;
	
integer i;
always@(posedge clk_200) begin
    if(pid_rdy) begin
       for(i = 99; i > 0; i=i-1) begin
          phase[i] <= phase[i-1];
       end
       phase[0] <= pid_out;
    end
end
	
PPL_200MHz p1(
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

endmodule