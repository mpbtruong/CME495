
`include "uart_globals.svh"

/**
 * Top level monitor/controller using receiver and transmitter uart modules.
 *
 * baud_rate = 115200 (112.5 khz)
 * bit_time = 1s / 115200 bits 
 *          = 8.681us / bit
 * 1 start bit, 8 data bits, 1 even parity bit, 1 stop bit -> 11 bits
 * packet_time = 8.681us * 11
 *             = 95.5us
 *             = (8.681 + 69.448 + 8.681 + 8.681) us
 * packet_time_10 = 86.81 
 */
module monitor_top(
    input  wire clk50, 
    // input  wire reset,
    // uart
    input  wire uart_rxd, // receiver
    output wire uart_txd, // transmitter
    input  wire uart_rts, // request to send (FPGA is slave)
    output wire uart_cts, // clear to send (FPGA is slave)
    // registers
    output reg[`REG0_BITS-1:0]   reg0, //
    output reg[`REG1_BITS-1:0]   reg1, //
    output reg[`REG2_BITS-1:0]   reg2, //
    output reg[`REG3_BITS-1:0]   reg3, //
    output reg[`REG4_BITS-1:0]   reg4, //
    // I/O
    input  reg[17:0] SW,
    input  reg[3:0]  KEY,
    output reg[17:0] LEDR,
    output reg[8:0]  LEDG
);

// declarations ////////////////////////////////////////////////////////////////
reg                     reset;     // sychronous
// baud clks
reg                     baud_tx;   // normal baud rate
reg                     baud_rx;   // baud rate with oversampling
// rx (uart receiver)
reg                     rx_enable; // allow receive transactions
reg[`NUM_DATA_BITS-1:0] rx_byte;   // data bits from an rx transaction
reg                     rx_done;   // rx transaction is done
reg                     rx_busy;   // rx is busy
reg                     rx_error;  // rx has error
// tx (uart transmitter)
reg                     tx_enable; // allow transmit transactions
reg                     tx_write;  // start a transactions
reg[`NUM_DATA_BITS-1:0] tx_byte;   // data bits to transmit
reg                     tx_done;   // tx transaction is done
reg                     tx_busy;   // tx is busy
reg                     tx_error;  // tx has error
// registers
reg                     reg_write; // high if a reg should be written to
// monitor state machine
reg[$clog2(`MONITOR_STATES_NUM)-1:0]    state;            // state machine state
reg[8*`NUM_CMD_BYTES-1:0]               cmd;              // command from controller
reg                                     cmd_rw;           // MSB bit of command read/write command
reg[8*`NUM_CMD_BYTES-2:0]               cmd_id;           // command id
reg[8*`NUM_CMD_DATA_BYTES-1:0]          data_size;        // number of bytes to read or write
reg[8*`MAX_CMD_PAYLOAD_BYTES-1:0]       cmd_data;         // command data
reg[$clog2(`MAX_CMD_PAYLOAD_BYTES)-1:0] cmd_data_idx;     // command data byte index
reg                                     cmd_tx_busy_prev; // delayed tx_busy

// I/O (LEDs, SW, etc.) ////////////////////////////////////////////////////////
always @(*) begin
    // reset
    reset     <= ~KEY[0];
    LEDG[0]   <= ~KEY[0];  // indicater for reset
    // rx
    LEDR[7:0] <= rx_byte; // display the rx_byte 
    LEDG[7]   <= rx_done;
    LEDG[6]   <= rx_busy;
    LEDG[5]   <= rx_error;
    // tx
    LEDG[3]   <= tx_done;
    LEDG[2]   <= tx_busy;
    LEDG[1]   <= tx_error;
end


// uart  ///////////////////////////////////////////////////////////////////////
// create the baud clks from the 50Mhz src clk
baud_generator #(.CLK_FRQ(`CLK_FRQ), .BAUD_RATE(`BAUD_RATE_TX))
baud_gen_tx(
    .clk(clk50),
    .reset(0),
    .baud(baud_tx)
);
baud_generator #(.CLK_FRQ(`CLK_FRQ), .BAUD_RATE(`BAUD_RATE_RX)) 
baud_gen_rx(
    .clk(clk50),
    .reset(0),
    .baud(baud_rx)
);

// create the uart receiver
uart_rx receiver(
    .baud(baud_rx),
    .enable(rx_enable),
    .rx(uart_rxd),
    .data(rx_byte),
    .done(rx_done),
    .busy(rx_busy),
    .error(rx_error)
);
// create the uart transmitter
uart_tx transmitter(
    .baud(baud_tx),
    .enable(tx_enable),
    .write(tx_write),
    .data(tx_byte),
    .tx(uart_txd),
    .done(tx_done),
    .busy(tx_busy),
    .error(tx_error)
);

// monitor /////////////////////////////////////////////////////////////////////
// monitor helper logic ////////////////////////////////////////////////////////
always @(*) begin
    // assign uart control signals
    rx_enable <= ~reset;
    tx_enable <= ~reset;
    // command signals
    {cmd_rw, cmd_id} <= cmd; // split cmd into r/w and id.
end

always @(posedge baud_rx) begin
    // clk in previous tx_busy status
    cmd_tx_busy_prev <= tx_busy;
end

// monitor state machine ///////////////////////////////////////////////////////
always @ (posedge baud_rx) begin
    if (reset) begin
        MONITOR_RESET();
    end else begin
        case (state) 
            `MONITOR_STATE_IDLE       : MONITOR_STATE_IDLE();
            `MONITOR_STATE_READ_CMD   : MONITOR_STATE_READ_CMD();
            `MONITOR_STATE_DATA_BYTES : MONITOR_STATE_DATA_BYTES();
            `MONITOR_STATE_WRITE      : MONITOR_STATE_WRITE();
            `MONITOR_STATE_READ       : MONITOR_STATE_READ();
            default : state <= `MONITOR_STATE_IDLE;
        endcase
    end
end

// monitor states //////////////////////////////////////////////////////////////
task MONITOR_RESET();
    // start idling for command
    state <= `MONITOR_STATE_IDLE;
    // initialize uart_tx inputs
    tx_write <= 0;
    tx_byte  <= 0;
    // tell controler not ready to receive
    uart_cts <= 1;
    // initialize helper signals
    cmd          <= 0;
    data_size    <= 0;
    cmd_data     <= 0;
    cmd_data_idx <= 0;
    reg_write    <= 0; // disable reg write
endtask
task MONITOR_STATE_IDLE();
    reg_write    <= 0; // disable reg write
    // check if controller is requesting to start a command
    if (!uart_rts && !rx_busy) begin
        // requesting to send command and not busy
        state    <= `MONITOR_STATE_READ_CMD; // proceed to read the command
        uart_cts <= 0;                       // allow controller to send the command
    end else begin
        uart_cts <= 1;
    end
endtask
task MONITOR_STATE_READ_CMD();
    // check if the command has been sent
    if (rx_done) begin
        // received the command
        cmd      <= rx_byte; // read the command
        state    <= `MONITOR_STATE_DATA_BYTES;
    end
endtask
task MONITOR_STATE_DATA_BYTES();
    // check if the number of data bytes has been sent
    if (rx_done) begin
        // received number of data bytes
        data_size    <= rx_byte; // read the command
        cmd_data_idx <= 0;       // reset byte index for command data
        // go to read or write state
        if (cmd_rw) begin
            state    <= `MONITOR_STATE_WRITE;
            // clear command data buffer for new data
            cmd_data <= 0;
        end else begin
            state    <= `MONITOR_STATE_READ;
            // set cmd_data to the right reg for reading
            case (cmd_id)
                `REG0 : cmd_data <= reg0;
                `REG1 : cmd_data <= reg1;
                `REG2 : cmd_data <= reg2;
                `REG3 : cmd_data <= reg3;
                `REG4 : cmd_data <= reg4;
                default: cmd_data <= 0;
            endcase
        end
    end
endtask
task MONITOR_STATE_WRITE();
    // read all of bytes being written from the controller
    if (rx_done) begin
        // new byte done being read
        cmd_data[8*cmd_data_idx +: 8] <= rx_byte; // read in the byte
        cmd_data_idx <= cmd_data_idx + 1;         // increment byte index
        // check if done
        if (cmd_data_idx == data_size-1) begin
            // done reading write data
            state     <= `MONITOR_STATE_IDLE;
            reg_write <= 1; // enable reg write
        end
    end
endtask
task MONITOR_STATE_READ();
    // write all the register bytes to the controller
    // set the next byte to write
    tx_byte <= cmd_data[8*cmd_data_idx +: 8];
    // check if done writing byte
    if (tx_done && cmd_tx_busy_prev) begin
        cmd_data_idx <= cmd_data_idx + 1; // increment byte index
        // check if done
        if (cmd_data_idx == data_size-1) begin
            // done reading write data
            state <= `MONITOR_STATE_IDLE;
            tx_write <= 0; // done writing data to controller
        end else begin
            tx_write <= 1; // write the next byte
        end
    end else begin
        tx_write <= 1; // write first byte
    end
endtask

// registers ///////////////////////////////////////////////////////////////////
// instances ///////////////////////////////////////////////////////////////////
// register 0
register #(.DATA_BITS(`REG0_BITS), .RESET_VALUE(`REG0_RESET)) 
inst_reg0(
    .clk(baud_rx),
    .reset(reset),
    .write(reg_write && (cmd_id == `REG0)),
    .data_in(cmd_data),
    .data(reg0)
);
// register 1
register #(.DATA_BITS(`REG1_BITS), .RESET_VALUE(`REG1_RESET)) 
inst_reg1(
    .clk(baud_rx),
    .reset(reset),
    .write(reg_write && (cmd_id == `REG1)),
    .data_in(cmd_data),
    .data(reg1)
);
// register 2
register #(.DATA_BITS(`REG2_BITS), .RESET_VALUE(`REG2_RESET)) 
inst_reg2(
    .clk(baud_rx),
    .reset(reset),
    .write(reg_write && (cmd_id == `REG2)),
    .data_in(cmd_data),
    .data(reg2)
);
// register 3
register #(.DATA_BITS(`REG3_BITS), .RESET_VALUE(`REG3_RESET)) 
inst_reg3(
    .clk(baud_rx),
    .reset(reset),
    .write(reg_write && (cmd_id == `REG3)),
    .data_in(cmd_data),
    .data(reg3)
);
// register 4
register #(.DATA_BITS(`REG4_BITS), .RESET_VALUE(`REG4_RESET)) 
inst_reg4(
    .clk(baud_rx),
    .reset(reset),
    .write(reg_write && (cmd_id == `REG4)),
    .data_in(cmd_data),
    .data(reg4)
);


endmodule