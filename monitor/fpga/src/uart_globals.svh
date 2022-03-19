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
 `define MONITOR_STATE_READ       3'b100 // 4 -> 0

/**
 * Controller command info.
 */
 `define NUM_CMD_BYTES          1
 `define NUM_CMDS               2 ** (8*`CMD_BYTES-1) // 1 R/W bit
 `define NUM_CMD_DATA_BYTES     1
 `define MAX_CMD_PAYLOAD_BYTES  4

/**
 * Register info.
 */
 // register 0
 `define REG0        0
 `define REG0_BITS   4
 `define REG0_RESET  8'h0F
 // register 1
 `define REG1        1
 `define REG1_BITS   8
 `define REG1_RESET  8'hFF
 // register 2
 `define REG2        2
 `define REG2_BITS   16
 `define REG2_RESET  16'hf1_f2
 // register 3
 `define REG3        3
 `define REG3_BITS   24
 `define REG3_RESET  24'h06_07_08
 // register 4
 `define REG4        4
 `define REG4_BITS   32
 `define REG4_RESET  32'hAA_BB_CC_DD

// register 124 - integral
 `define REG124      124
 `define REG124_BITS 16
 // register 125 - DAC out
 `define REG125      125
 `define REG125_BITS 16
 // register 126 - PID out
 `define REG126      126
 `define REG126_BITS 16
 // register 127 - phase error
 `define REG127      127
 `define REG127_BITS 16
