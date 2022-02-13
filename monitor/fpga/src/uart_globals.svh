/**
 * State machine states for the uart.
 */
`define STATE_START_BIT   3'b000
`define STATE_DATA_BITS   3'b001
`define STATE_PARITY_BIT  3'b010
`define STATE_STOP_BIT    3'b011
`define STATE_RESET       3'b100
`define STATE_IDLE        3'b001

/**
 * Uart config information.
 */
`define CLK_FRQ        50_000_000
`define OVERSAMPLING   16
`define BAUD_RATE_TX   115_200
`define BAUD_RATE_RX   `BAUD_RATE_TX * `OVERSAMPLING
`define NUM_DATA_BITS  8
 