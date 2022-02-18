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
                           no_rbytes:int,
                           no_wbytes:int,
                           name:str,
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
            self.cbyte      = self.cmd_cbyte()
            self.no_rbytes  = no_rbytes
            self.no_wbytes  = no_wbytes
            self.rbytes     = None
            self.wbytes     = None
            self.name       = name
        def __str__(self):
            cmd = ''
            cmd += f'Command {self.cid:03} {self.name}\n'
            cmd += f'   rw={self.rw} cbyte={self.cbyte} read_only={self.read_only}\n'
            cmd += f'   no_rbytes={self.no_rbytes} rbytes={self.rbytes}\n'
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
                self.cbyte = self.cmd_cbyte()
        def cmd_cbyte(self)->bytes:
            """
            Sets cbyte, the byte representation of the command.
            
            :raises:
                CommandByteError: if (self.cid > self.MAX_COMMANDS)
            """
            if (self.cid > self.MAX_COMMANDS):
                raise self.CommandByteError(f'Invalid cid: cid={self.cid} MAX_COMMANDS={self.MAX_COMMANDS}')
            rw_bit = 128 if (self.rw == 'r') else 0
            rw_cid_byte = rw_bit | self.cid
            cbyte = int.to_bytes(rw_cid_byte, self.CMD_BYTE_SIZE, self.BYTE_ENDIAN)
            return cbyte

    # constants ################################################################
    # command names
    CMD_1  = 'test_rw_register'
    CMD_2  = 'test_read_register'
    # dictionary of commands
    commands = {
        CMD_1  : Command(cid=1, no_rbytes=3, no_wbytes=3, name=CMD_1),
        CMD_2  : Command(cid=2, no_rbytes=5, no_wbytes=0, name=CMD_2, read_only=True),
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
        # read or write data
        if (cmd.rw == cmd.READ):
            cmd.rbytes = self.read_uart(cmd.no_rbytes, timeout)
            print(f'Read data!')
        elif (cmd.rw == cmd.WRITE):
            self.write_bytes_uart_flow(cmd.wbytes, timeout)
            print(f'Wrote data!')
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
