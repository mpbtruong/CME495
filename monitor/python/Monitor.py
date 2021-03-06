# Imports ######################################################################
from MonitorConfigUART import *
from MonitorTest import MonitorTest

import serial
from serial.tools import list_ports as serial_list_ports

from typing import List
from time import time

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
    class ReadUartFail(Exception):
        """
        Raised when an attempt to read the uart does not result in expected data.
        """
        pass
    class WriteUartFail(Exception):
        """
        Raised when an attempt to write to the uart fails.
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
        # serial uart instance
        self.uart:serial.Serial = None
        # connect to a port for uart communication
        self.connect_uart()

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
    def is_connected(self):
        """
        Returns True if uart is connected, False otherwise
        """
        return self.uart is not None

    def connect_uart(self):
        """
        Connects to a port for uart communication
        """
        try:
            self.assign_port(device_vid=self.config.device_vid, 
                        device_pid=self.config.device_pid)
            self.create_uart()
        except self.PortAssignError:
            print("could not connect")

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
        return self.uart.is_open if (self.uart is not None) else False

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
    def write_byte_uart_flow(self, data:bytes, timeout:float=None):
        """
        Write a byte to the uart with flow control. Blocks until data is written.

        :param data: the byte to write
        :param timeout: None to block forever, 0 to try to write and instantly
            return, or the time in seconds to block for.
        :exceptions:
            WriteUartFail: flow control timeout waiting for CTS from device.
            WriteUartFail: data failed to write.
        """
        return self.write_uart(data, timeout=timeout, flow_control=True)
    def write_bytes_uart_flow(self, data:bytes, timeout:float=None, big_endian:bool=True)->bool:
        """
        Write a set of bytes to the uart with flow control one at a time. 
        Blocks until data is written.

        :param data: the bytes to write.
        :param timeout: None to block forever, 0 to try to write and instantly
            return, or the time in seconds to block for.
        :param big_endian: data is sent in reverse if not big_endian.
            e.g. if data = [\x00, \x01]
                big_endian     : write in order \x00\x01
                not big_endian : write in order \x01\x00
        :exceptions:
            WriteUartFail: flow control timeout waiting for CTS from device.
            WriteUartFail: data failed to write.
        """
        wbytes = self.bytes_to_bytelist(data)
        if (not big_endian): wbytes = wbytes[::-1] # reverse byte order
        for wbyte in wbytes:
            self.write_uart(wbyte, timeout=timeout, flow_control=True)
        
    # base I/O #################################################################
    def flush_uart(self):
        """
        Flush the uart.
        """
        self.uart.flush()
    def flush_write_buffer_uart(self):
        """
        Flush the uart's write buffer.
        """
        self.uart.reset_output_buffer()
    def flush_read_buffer_uart(self):
        """
        Flush the uart's read buffer.
        """
        self.uart.reset_input_buffer()
    def flush_buffers_uart(self):
        """
        Flushes the uart's read and write buffers.
        """
        self.flush_read_buffer_uart()
        self.flush_write_buffer_uart()
    def write_uart(self, data:bytes, timeout:float=None, flow_control=False):
        """
        Write bytes to the uart. If timeout is set, the write attempt
        will only persist for timeout seconds.
        
        :param data: data to write to uart.
        :param timeout: None to block forever, 0 to try to write and instantly
            return, or the time in seconds to block for.
        :param flow_control: True if using flow control.
        :exceptions:
            WriteUartFail: flow control timeout waiting for CTS from device.
            WriteUartFail: data failed to write.
        """
        if (not data): raise ValueError("data is empty byte string")
        # set timeout
        self.uart.write_timeout = timeout
        if (flow_control):
            # request to send data
            self.setRTS(True)
            # wait until cleared to send data or timeout
            if (timeout): tstart = time()
            while (not self.readCTS()):
                if (timeout):
                    dt = time() - tstart
                    if (dt > timeout): raise self.WriteUartFail("Timed out before CTS low")
        # disable request to send
        if (flow_control): self.setRTS(False)
        # write to the uart
        bytes_written = self.uart.write(data)
        self.flush_uart()
        # success status
        if (bytes_written == 0): raise self.WriteUartFail("Failed to write bytes")
    def read_uart(self, num_bytes:int, timeout:float=None)->bytes:
        """
        Read num_bytes from uart, blocking until read.

        :param num_bytes: number of bytes to read.
        :param timeout: None to block forever, 0 to try to read and instantly
            return, or the time in seconds to block for.
        :exceptions:
            ValueError   : num_bytes None or 0
            ReadUartFail : failed to read uart data
        """
        if (not num_bytes): raise ValueError("num_bytes None or 0")
        # set timeout
        self.uart.timeout = timeout
        # read data
        data = self.uart.read(size=num_bytes)
        # check if read failed
        if (isinstance(data, str)): 
            raise self.ReadUartFail("Data read fail, got string not bytes")
        return data
    def read_uart_until(self, pattern:bytes, timeout:float=None, size=None):
        """
        Read from the uart until a bytestring pattern is found.

        :param pattern: a bytestring to read until (e.g. b'$abc').
        :param timeout: None to block forever, 0 to try to read and instantly
            return, or the time in seconds to block for.
        :exceptions:
            ReadUartFail : failed to read uart data
        """
        # set timeout
        self.uart.timeout = timeout
        # read data
        data = self.uart.read_until(pattern, size)
        # check if read failed
        if (isinstance(data, str)): 
            raise self.ReadUartFail("Data read fail, got string not bytes")
        return data
    def read_uart_line(self, timeout:float=None):
        """
        Read from the uart until a newline is found.

        :param timeout: None to block forever, 0 to try to read and instantly
            return, or the time in seconds to block for.
        :exceptions:
            ReadUartFail : failed to read uart data
        """
        # set timeout
        self.uart.timeout = timeout
        # read data
        data = self.uart.readline()
        # check if read failed
        if (isinstance(data, str)): 
            raise self.ReadUartFail("Data read fail, got string not bytes")
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
                print(f'   - device {port.device} | description {port.description} | hwid {port.hwid} | vid:pid={port.vid}:{port.pid}')
        else: print('No serial ports found')

    # utility methods ##########################################################
    @staticmethod
    def bytes_to_bytelist(data:bytes)->List[bytes]:
        """
        Converts a bytes string to a list of bytes.

        :param data: b'\x00\x01'
        :return: [b'\x00', b'\x01']
        """
        return [b'%c' % byte for byte in data]


# Main #########################################################################
def main():
    monitor = Monitor(config=ConfigFPGA())
    print(monitor)

    mtester = MonitorTest(monitor)
    
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
