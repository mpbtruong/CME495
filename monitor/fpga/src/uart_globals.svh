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
 
 /**
 * State machine for monitor command.
 */
 `define MONITOR_STATES_NUM       5
 `define MONITOR_STATE_IDLE       3'b000 // 0 -> 1
 `define MONITOR_STATE_READ_CMD   3'b001 // 1 -> 2
 `define MONITOR_STATE_DATA_BYTES 3'b010 // 2 -> branch to 3 | 4
 `define MONITOR_STATE_WRITE      3'b011 // 3 -> 0
 `define MONITOR_STATE_READ       3'b101 // 4 -> 0

/**
 * Controller command info
 */
 `define CMD_BITS         8
 `define NUM_CMDS         2 ** (`CMD_BITS-1) // 1 R/W bit
 `define CMD_DATA_BITS    8