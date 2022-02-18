# Imports ######################################################################
from Monitor import Monitor
from MonitorConfigUART import ConfigFPGA
from MonitorTest import MonitorFPGATest

from typing import Literal


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
            rw        : r or w if command is read or write
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
        WRITE_CMD     = 'w'    # representation for write command
        READ_CMD      = 'r'    # representation for read command

        # exceptions ###########################################################
        class CommandByteError(Exception):
            """
            Raised if cid is invalid.
            """
            pass

        # constructor ##########################################################
        def __init__(self, cid:int, 
                           rw:Literal['r', 'w'],
                           no_rbytes:int,
                           no_wbytes:int,
                           name:str
                           ):
            """
            Initializes a command.

            :raises:
                CommandByteError: if (self.cid > self.MAX_COMMANDS)
            """
            self.cid        = cid
            self.rw         = rw
            self.cbyte      = self.cmd_byte()
            self.no_rbytes  = no_rbytes
            self.no_wbytes  = no_wbytes
            self.rbytes     = None
            self.wbytes     = None
            self.name       = name
        def __str__(self):
            cmd = ''
            cmd += f'Command {self.name} cid={self.cid:03} rw={self.rw} cbyte={self.cbyte}\n'
            cmd += f'   no_rbytes={self.no_rbytes} no_wbytes={self.no_wbytes}\n'
            return cmd
        # methods ##############################################################
        def cmd_byte(self)->bytes:
            """
            Returns the byte representation of the command.
            
            :raises:
                CommandByteError: if (self.cid > self.MAX_COMMANDS)
            """
            if (self.cid > self.MAX_COMMANDS):
                raise self.CommandByteError(f'cid={self.cid} MAX_COMMANDS={self.MAX_COMMANDS}')
            rw_bit = 128 if (self.rw == 'r') else 0
            rw_cid_byte = rw_bit | self.cid
            cbyte = int.to_bytes(rw_cid_byte, self.CMD_BYTE_SIZE, self.BYTE_ENDIAN)
            return cbyte

    # constants ################################################################
    # command names
    CMD_1  = 'test_read'
    CMD_2  = 'test_write'
    # dictionary of commands
    commands = {
        CMD_1  : Command(cid=1, rw='r', no_rbytes=3, no_wbytes=0, name=CMD_1),
        CMD_2  : Command(cid=2, rw='w', no_rbytes=0, no_wbytes=4, name=CMD_2),
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
    def execute_command(self, cmd:Command):
        """
        Executes an FPGA command. Onus is on the caller to ensure

        :param cmd: the command to execute.
        :pre-condition: cmd.wbytes holds data to write if write command
        :post-condition: cmd.rbytes has read data from FPGA if read command.
        """
        # tell the FPGA what command
        self.write_byte_uart_flow(cmd.cbyte)
        # read or write data
        if (cmd.rw == cmd.READ_CMD):
            cmd.rbytes = self.read_uart(cmd.no_rbytes)
        elif (cmd.rw == cmd.WRITE_CMD):
            self.write_bytes_uart_flow(cmd.wbytes)
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
            print(f'  - {cmd}', end='')
        print()

# Main #########################################################################
def main():
    monitor = MonitorFPGA()
    print(monitor)
    monitor.print_commands()

    mtester = MonitorFPGATest(monitor)

    mtester.test_execute_command()


if __name__ == '__main__':
    main()
