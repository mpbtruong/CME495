# Imports ######################################################################
from Monitor import Monitor
from MonitorConfigUART import ConfigFPGA
from MonitorTest import MonitorFPGATest


# Globals ######################################################################


# Library ######################################################################
class MonitorFPGA(Monitor):
    """
    Builds on Monitor to implement an API for writing to and reading from
    the FPGA with the use of commands.
    """
    # FPGA command class #######################################################
    class Command():
        """
        Represents a command used to communicate with the FPGA.

        Attributes:
            cid       : command id in range [1, 128]
            rw        : last read/write status of the command (r or w).
            read_only : True if command is read only
            no_rbytes : number of bytes to read
            no_wbytes : number of data bytes to write
            rbytes    : read bytes from executing the command
            wbytes    : bytes to write to the FPGA
            name      : friendly name of the command
        """
        # constants ############################################################
        # command info
        MAX_COMMANDS  = 128
        BYTE_ENDIAN   = 'big'  # order to send bytes
        CMD_BYTE_SIZE = 1      # size of command
        WRITE     = 'w'    # representation for write command
        READ      = 'r'    # representation for read command

        RW_BYTE_INFO_SIZE = 1 # bytes to represent number of bytes to R/W

        # exceptions ###########################################################
        class CommandByteError(Exception):
            """
            Raised if cid is invalid.
            """
            pass
        class CommandRWError(Exception):
            """
            Raised if rw is invalid.
            """
            pass
        class ExecuteCommandError(Exception):
            """
            Raised if the state of a command is invalid when executed.
            """
            pass

        # constructor ##########################################################
        def __init__(self, cid:int, 
                           name:str,
                           no_rwbytes:int=None,
                           no_rbytes:int=None,
                           no_wbytes:int=None,
                           read_only:bool=False,
                           ):
            """
            Initializes a command.

            :raises:
                CommandByteError: if (self.cid > self.MAX_COMMANDS)
            """
            self.cid        = cid
            self.rw         = None
            self.read_only  = read_only
            self.cbyte      = self.calc_cbyte()
            self.no_rbytes  = no_rbytes if (no_rbytes is not None) else no_rwbytes
            self.no_wbytes  = no_wbytes if (no_wbytes is not None) else no_rwbytes
            self.rbytes     = None
            self.wbytes     = None
            self.name       = name
        def __str__(self):
            cmd = ''
            cmd += f'Command {self.cid:03} {self.name}\n'
            cmd += f'   rw={self.rw} cbyte={self.cbyte} read_only={self.read_only}\n'
            cmd += f'   no_rbytes={self.no_rbytes} rbytes={self.rbytes}\n'
            if (not self.read_only):
                cmd += f'   no_wbytes={self.no_wbytes} wbytes={self.wbytes}\n'
            return cmd
        # methods ##############################################################
        def setRW(self, rw:str):
            """
            Sets the command to write or read.

            :param rw: Command.READ or Command.WRITE
            :raises:
                CommandRWError: if (rw != self.READ or rw != self.WRITE)
            """
            if (rw != self.READ and rw != self.WRITE):
                raise self.CommandRWError(f'Set rw invalid rw={rw}')
            else:
                self.rw = rw
                # update cbyte to change RW bit
                self.cbyte = self.calc_cbyte()
        def calc_cbyte(self)->bytes:
            """
            Calculates cbyte, the byte representation of the command.
            
            :raises:
                CommandByteError: if (self.cid > self.MAX_COMMANDS)
            """
            if (self.cid > self.MAX_COMMANDS):
                raise self.CommandByteError(f'Invalid cid: cid={self.cid} MAX_COMMANDS={self.MAX_COMMANDS}')
            rw_bit = 128 if (self.rw == 'w') else 0
            rw_cid_byte = rw_bit | self.cid
            cbyte = int.to_bytes(rw_cid_byte, self.CMD_BYTE_SIZE, self.BYTE_ENDIAN)
            return cbyte
        def rw_no_bytes(self, i_no_bytes:int)->bytes:
            """
            Represents no_rbytes and no_wbytes as byte(s).

            :param i_no_bytes: no_rbytes or no_wbytes
            :return: i_no_bytes as byte string.
            """
            return self.int_to_byte(i_no_bytes, self.RW_BYTE_INFO_SIZE)
        def int_to_byte(self, aint:int, no_bytes:int)->bytes:
            """
            Convert an int to bytes.

            :param aint: a number to convert.
            :param no_bytes: number of bytes to represent aint as.
            :return: byte representation of aint.
            """
            return int.to_bytes(aint, no_bytes, self.BYTE_ENDIAN)

    # constants ################################################################
    # command names
    CMD_0  = 'reg0_'
    CMD_1  = 'reg1_'
    CMD_2  = 'reg2_'
    CMD_3  = 'reg3_'
    CMD_4  = 'reg4_'
    # dictionary of commands
    commands = {
        CMD_0  : Command(cid=0, no_rwbytes=0, name=CMD_0),
        CMD_1  : Command(cid=1, no_rwbytes=1, name=CMD_1),
        CMD_2  : Command(cid=2, no_rwbytes=2, name=CMD_2),
        CMD_3  : Command(cid=3, no_rwbytes=3, name=CMD_3),
        CMD_4  : Command(cid=4, no_rwbytes=4, name=CMD_4),
        # CMD_x  : Command(cid=x, no_rwbytes=2, name=CMD_x, read_only=True),
    }
    commands_by_id = {cmd.cid:cmd for cmd in commands.values()}
    

    # constructor ##############################################################
    def __init__(self):
        """
        Initializes the monitor.

        :param config: configuration for the uart.
        """
        Monitor.__init__(self, ConfigFPGA)
    
    # methods ##################################################################
    def execute_command(self, cmd:Command, rw:str, timeout:float=None):
        """
        Executes an FPGA command. Onus is on the caller to ensure the command
        is in a valid state to be executed.

        :param cmd: the command to execute.
        :param rw: Command.READ or Command.WRITE
        :param timeout: None to block forever, 0 to try to R/W for and instantly
            return, or the time in seconds to block for.
        :pre-conditions: 
            cmd.rw     : set to r for read or w for write
            cmd.wbytes : holds data to write if write command.
        :post-conditions: 
            cmd.rbytes : has read data from FPGA if read command.
        """
        # check state
        if (cmd.read_only and rw == cmd.WRITE):
            raise self.ExecuteCommandError('Tried to write a read only command')
        if (rw == cmd.WRITE and cmd.no_wbytes != len(cmd.wbytes)):
            raise self.ExecuteCommandError('Length of wbytes != no_wbytes')
        # set command to read or write
        cmd.setRW(rw)
        # tell the FPGA what command
        self.write_byte_uart_flow(cmd.cbyte, timeout)
        print(f'Wrote command {cmd.cbyte}!')
        # tell the FPGA how many bytes of data to R/W
        i_no_bytes = cmd.no_rbytes if (cmd.rw == cmd.READ) else cmd.no_wbytes
        no_bytes = cmd.rw_no_bytes(i_no_bytes)
        self.write_byte_uart_flow(no_bytes, timeout)
        print(f'Wrote ({cmd.rw}) command data info {i_no_bytes} {no_bytes}!')
        # read or write data
        if (cmd.rw == cmd.READ):
            cmd.rbytes = self.read_uart(cmd.no_rbytes, timeout)
            print(f'Read data!')
        elif (cmd.rw == cmd.WRITE):
            self.write_bytes_uart_flow(cmd.wbytes, timeout, big_endian=False)
            print(f'Wrote data!')
    
    # utility helper methods ###################################################
    def get_command(self, name:str)->Command:
        """
        Returns a FPGA command given its name.
        """
        return self.commands[name]
    def get_command_by_id(self, cid:int)->Command:
        """
        Returns a FPGA command given its name.
        """
        return self.commands_by_id[cid]
    def print_commands(self):
        """
        Print string representations of the commands.
        """
        print(f'Commands:')
        for cmd in self.commands.values():
            print(f'- {cmd}', end='')
        print()

# Main #########################################################################
def main():
    monitor = MonitorFPGA()
    print(monitor)
    monitor.print_commands()

    mtester = MonitorFPGATest(monitor)

    # mtester.test_write_byte_uart_flow()
    mtester.test_execute_command()


if __name__ == '__main__':
    main()
