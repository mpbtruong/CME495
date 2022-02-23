
`include "uart_globals.svh"

/**
 * Monitor control uart.
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
    output reg[$clog2(`MONITOR_STATES_NUM)-1:0] state, // monitor state machine state

    output reg[8*`NUM_CMD_BYTES-1:0]      cmd,       // command from controller
    output reg                            cmd_rw,    // MSB bit of command read/write command
    output reg[8*`NUM_CMD_BYTES-2:0]      cmd_id,    // command id
    output reg[8*`NUM_CMD_DATA_BYTES-1:0] data_size, // number of bytes to read or write



    input  wire clk50, 
    // input  wire reset,
    // uart
    input  wire uart_rxd, // receiver
    output wire uart_txd, // transmitter
    input  wire uart_rts, // request to send (FPGA is slave)
    output wire uart_cts, // clear to send (FPGA is slave)
    // gpio
    output reg  gpio_1,  // uart_rxd
    output reg  gpio_2,  // uart_cts
    output reg  gpio_3,  // uart_txd
    output reg  gpio_4,  // uart_rts
    output reg  gpio_5,  // baud rate rx 115200 (112.5 khz)
    output reg  gpio_6,  // baud rate tx (16 oversampling)
    output reg  gpio_7,  // clk50
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
// rx
reg                     rx_enable; // allow receive transactions
reg[`NUM_DATA_BITS-1:0] rx_byte;   // data bits from an rx transaction
reg                     rx_done;   // rx transaction is done
reg                     rx_busy;   // rx is busy
reg                     rx_error;  // rx has error
// tx
reg                     tx_enable; // allow transmit transactions
reg                     tx_write;  // start a transactions
reg[`NUM_DATA_BITS-1:0] tx_byte;   // data bits to transmit
reg                     tx_done;   // tx transaction is done
reg                     tx_busy;   // tx is busy
reg                     tx_error;  // tx has error

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
    // rx_enable <= SW[17];
    // LEDR[17]  <= SW[17];
    // tx
    // tx_enable <= SW[15];
    // LEDR[15]  <= SW[15];
    tx_write  <= ~KEY[2];
    LEDG[4]   <= ~KEY[2];
    tx_byte   <= SW[7:0]; // use switches as input for tx_byte
    LEDG[3]   <= tx_done;
    LEDG[2]   <= tx_busy;
    LEDG[1]   <= tx_error;
    // flow control
    // uart_cts <= KEY[3];
end

// gpio ////////////////////////////////////////////////////////////////////////
// always @(*) begin
//     gpio_1  <= uart_rxd;
//     gpio_2  <= uart_cts;
//     gpio_3  <= uart_txd;
//     gpio_4  <= uart_rts;
//     gpio_5  <= baud_rx;
//     gpio_6  <= baud_tx;
//     gpio_7  <= clk50;
// end

// uart instantiations /////////////////////////////////////////////////////////
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

// monitor declarations ////////////////////////////////////////////////////////


// monitor helper logic ////////////////////////////////////////////////////////
always @(*) begin
    // assign uart control signals
    rx_enable <= ~reset;
    tx_enable <= ~reset;
    // command signals
    {cmd_rw, cmd_id} <= cmd; // split cmd into r/w and id.
    // uart_cts  <= rx_busy;
end

// monitor command state machine logic /////////////////////////////////////////
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
    // tell controler not ready to receive
    uart_cts <= 1;
    // initialize helper signals
    cmd       <= 0;
    data_size <= 0;
endtask
task MONITOR_STATE_IDLE();
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
        // uart_cts <= 0;       // clear controller to send number of packet bytes
        cmd      <= rx_byte; // read the command
        state    <= `MONITOR_STATE_DATA_BYTES;
    end else begin
        // not done receiving command yet
        // uart_cts <= 1; 
    end
endtask
task MONITOR_STATE_DATA_BYTES();
    // check if the number of data bytes has been sent
    if (rx_done) begin
        // received number of data bytes
        data_size <= rx_byte; // read the command
        // go to read or write state
        if (cmd_rw) begin
            state    <= `MONITOR_STATE_WRITE;
            // uart_cts <= 0; // writing data so controller not clear to send
        end else begin
            state    <= `MONITOR_STATE_READ;
            // uart_cts <= 1; // reading data so controller clear to send
        end
    end else begin
        // not done receiving number of data bytes yet
        // uart_cts <= 1; 
    end
endtask
task MONITOR_STATE_WRITE();

endtask
task MONITOR_STATE_READ();

endtask

endmodule