
module monitor_top(
    input wire clk50, reset,
    // uart
    input  wire uart_rxd, // receiver
    input  wire uart_cts, // clear to send
    output wire uart_txd, // transmitter
    output wire uart_rts, // request to send
    // gpio
    output reg  gpio_1,  // uart_rxd
    output reg  gpio_2,  // clear to send
    output reg  gpio_3,  // transmitter
    output reg  gpio_4,  // request to send
    output reg  gpio_5,  // baud rate 112500 (112.5 khz)
    // I/O
    output wire reset_led
);

// I/O (LEDs, SW, etc.)
always @(*) begin
    reset_led <= ~reset;
end

// gpio
always @(*) begin
    gpio_1  <= uart_rxd;
    gpio_2  <= uart_cts;
    gpio_3  <= uart_txd;
    gpio_4  <= uart_rts;
    gpio_5  <= baud;
end

// create the baud clk from the 50Mhz src clk
reg baud;
baud_generator baud_gen(
    .clk50(clk50),
    .reset(~reset),
    .baud(baud)
);

endmodule