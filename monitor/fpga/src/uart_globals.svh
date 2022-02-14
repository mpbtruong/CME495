/**
 * State machine states for the uart.
 */
`define STATES_NUM        4
`define STATE_IDLE        2'b00
`define STATE_DATA_BITS   2'b01
`define STATE_PARITY_BIT  2'b10
`define STATE_STOP_BIT    2'b11

/**
 * Uart config information.
 */
`define CLK_FRQ        50_000_000
`define OVERSAMPLING   16
`define BAUD_RATE_TX   115_200
`define BAUD_RATE_RX   `BAUD_RATE_TX * `OVERSAMPLING
`define NUM_DATA_BITS  8
`define NUM_PARITY_BIT 1

// select parity type
`define PARITY_EVEN    0
// `define PARITY_ODD     1
 