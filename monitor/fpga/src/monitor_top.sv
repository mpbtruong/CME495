
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
    rx_enable <= SW[17];
    LEDR[17]  <= SW[17];
    // tx
    tx_enable <= SW[15];
    LEDR[15]  <= SW[15];
    tx_write  <= ~KEY[2];
    LEDG[4]   <= ~KEY[2];
    tx_byte   <= SW[7:0]; // use switches as input for tx_byte
    LEDG[3]   <= tx_done;
    LEDG[2]   <= tx_busy;
    LEDG[1]   <= tx_error;
    // flow control
    uart_cts <= KEY[3];
end

// gpio ////////////////////////////////////////////////////////////////////////
always @(*) begin
    gpio_1  <= uart_rxd;
    gpio_2  <= uart_cts;
    gpio_3  <= uart_txd;
    gpio_4  <= uart_rts;
    gpio_5  <= baud_rx;
    gpio_6  <= baud_tx;
    gpio_7  <= clk50;
end

// instantiations //////////////////////////////////////////////////////////////
// create the baud clks from the 50Mhz src clk
baud_generator #(.CLK_FRQ(`CLK_FRQ), .BAUD_RATE(`BAUD_RATE_TX))
baud_gen_tx(
    .clk(clk50),
    .reset(reset),
    .baud(baud_tx)
);
baud_generator #(.CLK_FRQ(`CLK_FRQ), .BAUD_RATE(`BAUD_RATE_RX)) 
baud_gen_rx(
    .clk(clk50),
    .reset(reset),
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

endmodule