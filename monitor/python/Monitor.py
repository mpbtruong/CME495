# Imports ######################################################################
from MonitorConfigUART import *
from MonitorTest import MonitorTest

import serial
from serial.tools import list_ports as serial_list_ports

from typing import Literal

# Globals ######################################################################


# Library ######################################################################
class Monitor():
    """
    Monitor/controller for communicating with a serial device (e.g. FPGA) using 
    the UART protocol (e.g. using a RS-232/USB cable). 

    Capable of writing to and reading from the device. Class should be extended
    to implement a packet structure for monitoring/controlling the device.

    pySerial
        doc -> 
            https://pyserial.readthedocs.io/en/latest/pyserial.html
        api -> 
            https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        ListPortInfo -> 
            https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
    
    Attributes:
        For the following attributes refer to the pySerial documentation:
            baudrate      : baud rate of the uart.
            datasize      : number of uart data bits.
            parity        : specify type of uart parity bit
            rtscts        : specify if using RTS (Reqest to Send) / CTS 
                            (Clear to Send) flow control.
            write_timeout : timeout for trying to write.
            read_timeout  : timeout for trying to read.
        device_vid : vendor ID of the serial device.
        device_pid : product ID of the serial device.
    """
    # constants ################################################################

    # exceptions ###############################################################
    class PortAssignError(Exception):
        """
        Raised when assigning a UART port fails.
        """
        pass
    class CreateUartError(Exception):
        """
        Raised when initializing the uart for communication fails.
        """
        pass
    class DestroyUartError(Exception):
        """
        Raised when stopping the uart communication channel fails.
        """
        pass

    # constructor ##############################################################
    def __init__(self, config:ConfigUART):
        """
        Setup the UART serial port.

        :param config: configuration for the uart.
        :raises:
            PortAssignError: if unable to find the serial device with
                device_vid and device_pid.
        """
        # uart config
        self.config = config
        # uart port
        self.port = None
        self.assign_port(device_vid=self.config.device_vid, 
                         device_pid=self.config.device_pid)
        # serial uart instance
        self.uart:serial.Serial = None
        self.create_uart()

    def __str__(self)->str:
        """
        Returns a string representation of the monitor.
        """
        monitor = ''
        if (self.uart):
            monitor += f'Monitor port=\'{self.port.description}\'\n'
            monitor += f'   baud={self.config.baudrate} | databits={self.config.datasize} parity={self.config.parity} stopbits={self.config.stopbits} | rts_cts={self.config.rtscts}\n'
            monitor += f'   timeouts: write={self.config.write_timeout} read={self.config.read_timeout}\n'
            monitor += f'   WARNING: ensure system OS device driver settings match\n'
        else:
            monitor += f'Monitor uart not created'
        return monitor
    
    # methods ##################################################################
    # initialization ###########################################################
    def create_uart(self):
        """
        Initializes the uart for communication.

        :raises: 
            CreateUartError: if self.uart is not None
        """
        if (self.uart is not None): 
            raise self.CreateUartError("Tried creating uart when already exists")
        self.uart = serial.Serial(port=self.port.device,
                                  baudrate=self.config.baudrate,
                                  bytesize=self.config.datasize,
                                  parity=self.config.parity,
                                  stopbits=self.config.stopbits,
                                  rtscts=self.config.rtscts,
                                  timeout=self.config.read_timeout,
                                  write_timeout=self.config.write_timeout
                                  )
        self.setRTS(False) # only reqest to send when want to write
    def close_uart(self):
        """
        Stop the communication channel with the serial device.

        :raises: 
            DestroyUartError: if self.uart is None
        """
        if (self.uart is None):
            raise self.DestroyUartError("Tried to destroy uart when did not exist")
        self.uart.close()
        self.uart = None
    def uart_open(self)->bool:
        """
        Returns True if the uart port is open for communication.
        """
        return self.uart.is_open() if (self.uart is not None) else False

    # communication ############################################################
    # flow control I/O #########################################################
    def setRTS(self, request_to_send:bool):
        """
        Sets the uart RTS (Reqest to Send) signal to ask the slave device.

        :param request_to_send: True to request to send data (logic 0).
        """
        self.uart.setRTS(request_to_send)
    def readRTS(self)->bool:
        """
        Reads the uart RTS (Reqest to Send) status. Mostly just a debug tool.
        """
        return self.uart.rts
    def readCTS(self)->bool:
        """
        Reads the uart CTS (Clear to Send) status from the slave device.
        """
        return self.uart.getCTS()
    def write_byte_uart_flow(self, data:bytes)->bool:
        """
        Write a byte to the uart with flow control. Blocks until data written.

        :param data: the byte to write
        :return: True if write was successful.
        """
        return self.write_uart(data, timeout=None, flow_control=True)
        
    # base I/O #################################################################
    def flush_uart(self):
        """
        Flush the uart.
        """
        self.uart.flush()
    def write_uart(self, data:bytes, timeout:float=None, flow_control=False)->bool:
        """
        Write bytes to the uart. If timeout is set, the write attempt
        will only persist for timeout seconds.
        
        :param data: data to write to uart.
        :param timeout: None to block forever, 0 to try to write and instantly
            return, or the time in seconds to block for.
        :param flow_control: True if using flow control.
        :return: True if write was successful.
        """
        if (not data): raise ValueError("data is empty byte string")
        # set timeout
        self.uart.write_timeout = timeout
        if (flow_control):
            # request to send data
            self.setRTS(True)
            # wait until cleared to send data
            while (not self.readCTS()): pass
        # disable request to send
        if (flow_control): self.setRTS(False)
        # write to the uart
        bytes_written = self.uart.write(data)
        self.flush_uart()
        # success status
        return True if (bytes_written != 0) else False
    def read_uart(self, num_bytes:int, timeout:float=None)->bytes:
        """
        Read num_bytes from uart, blocking until read.

        :param num_bytes: number of bytes to read.
        """
        if (not num_bytes): raise ValueError("num_bytes None or 0")
        # set timeout
        # self.uart.timeout = timeout
        # read data
        data = self.uart.read(size=num_bytes)
        print(data, type(data))
        return data
    
    # ports ####################################################################
    def assign_port(self, device_vid:int, device_pid:int):
        """
        Assign the serial port that has device_vid and device_pid. Raises 
        an exception otherwise.

        :param device_vid: the desired serial device's vendor ID.
        :param device_pid: the desired serial device's product ID.
        :return: ListPortInfo of serial port.
        """
        ports = self.list_ports()
        for port in ports:
            if ((port.vid == device_vid) and (port.pid == device_pid)):
                self.port = port
                break
        else: raise self.PortAssignError("Port with device_vid and device_pid not found")
    @classmethod
    def list_ports(cls):
        """
        Gets a list of currently available serial ports.

        :return: List[ListPortInfo]
        """
        ports = serial_list_ports.comports()
        return ports
    @classmethod
    def print_ports(cls):
        """
        Prints the list of currently available serial ports (ListPortInfo).
        """
        ports = cls.list_ports()
        if (ports):
            print(f'Available serial ports:')
            for port in ports:
                print(f'   - device {port.device} | description {port.description} | hwid {port.hwid}')
        else: print('No serial ports found')

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
            name      : friendly name of the command
        """
        # constants ############################################################
        # command info
        MAX_COMMANDS  = 128
        BYTE_ENDIAN   = 'big'  # order to send bytes
        CMD_BYTE_SIZE = 1      # size of command
        WRITE_CMD     = 1      # MSB of command byte
        READ_CMD      = 0      # MSB of command byte

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
    

    # constructor ##############################################################
    def __init__(self, config:ConfigFPGA=None):
        """
        Initializes the monitor.

        :param config: configuration for the uart.
        """
        monitor_config = config if (config is None) else ConfigFPGA()
        Monitor.__init__(self, monitor_config)
    
    # methods ##################################################################
    def get_command(self, name:str)->Command:
        """
        Returns a FPGA command given its name.
        """
        return self.commands[name]
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
    monitor_fpga = MonitorFPGA(config=ConfigFPGA())
    print(monitor_fpga)
    
    monitor_fpga.print_commands()

    mtester = MonitorTest(monitor_fpga)
    # mtester.test_read_n_bytes(1)
    # mtester.test_write_bytes_prompt()
    # mtester.test_write_byte_nums_0_to_255(delay=1, input_write_stall=True)
    # mtester.test_rts_cts()
    mtester.test_write_byte_uart_flow()

    # mtester.test_write_byte(b'\xFF')
    # mtester.test_write_read_byte(b'\xAF')
    # mtester.test_write_byte_prompt()


if __name__ == '__main__':
    main()
