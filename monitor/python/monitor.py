# Imports ######################################################################
import serial
from serial.tools import list_ports as serial_list_ports

from typing import List
from time import sleep

# Globals ######################################################################


# Library ######################################################################
class Monitor():
    """
    Monitor/controller for communicating with the FPGA using UART RS-232/USB
    cable. 

    Monitors by polling for data. Controls by sending control bits to FPGA
    registers.

    pySerial
        doc -> 
            https://pyserial.readthedocs.io/en/latest/pyserial.html
        api -> 
            https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        ListPortInfo -> 
            https://pyserial.readthedocs.io/en/latest/tools.html#serial.tools.list_ports.ListPortInfo
    """
    # constants ################################################################
    BAUD_RATE = 115200
    DATA_BITS = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN # EVEN (0-bit -> even # of 1s)
    STOP_BITS = serial.STOPBITS_ONE
    FLOW_CONTROL_RTS_CTS = False

    USB_TO_SERIAL_HWID='USB VID:PID=067B:2303 SER= LOCATION=1-5'
    USB_TO_SERIAL_VID=1659
    USB_TO_SERIAL_PID=8963

    # constructor ##############################################################
    def __init__(self, baudrate=BAUD_RATE,
                       bytesize=DATA_BITS,
                       parity=PARITY,
                       stopbits=STOP_BITS,
                       rtscts=FLOW_CONTROL_RTS_CTS,
                       ):
        """
        Setup the UART serial port.
        """
        # uart config
        try: self.port = self.assign_port(device_vid=self.USB_TO_SERIAL_VID, 
                                          device_pid=self.USB_TO_SERIAL_PID)
        except serial.SerialException:
            print(f'Error: Serial port not found!')
            self.print_ports()
            exit(1)
        self.baudrate  = baudrate
        self.datasize  = bytesize
        self.parity    = parity
        self.stopbits  = stopbits
        self.rtscts    = rtscts
        # serial uart instance
        self.uart:serial.Serial = serial.Serial(port=self.port.device,
                                                baudrate=self.baudrate,
                                                bytesize=self.datasize,
                                                parity=self.parity,
                                                stopbits=self.stopbits,
                                                rtscts=self.rtscts,
                                                )
    def __str__(self)->str:
        """
        Returns a string representation of the monitor.
        """
        monitor = ''
        monitor += f'Monitor port=\'{self.port.description}\'\n'
        monitor += f'   baud={self.baudrate} | databits={self.datasize} parity={self.parity} stopbits={self.stopbits} | rts_cts={self.rtscts}\n'
        monitor += f'   WARNING: ensure system OS device driver settings match\n'
        return monitor
    
    # methods ##################################################################
    def assign_port(self, device_vid:int, device_pid:int):
        """
        Assign the serial port that has device_hwid. Raises an exception 
        otherwise.

        :param device_vid: the desired serial device's vendor ID.
        :param device_pid: the desired serial device's product ID.
        :return: ListPortInfo of serial port.
        """
        ports = self.list_ports()
        for port in ports:
            if ((port.vid == device_vid) and (port.pid == device_pid)): return port   
        raise serial.SerialException("No ports found!")

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
        print(f'Available serial ports:')
        for port in ports:
            print(f'   - device {port.device} | description {port.description} | hwid {port.hwid}')

    # test cases ###############################################################
    def test_loop_wrapper(test_func):
        """
        Returns a wrapper function that turns a test case into an infinite loop.
        """
        def loop_wrapper(*args, **kwargs):
            print(f'Testing {test_func.__name__}')
            try:
                while True:
                    test_func(*args, **kwargs)
            except KeyboardInterrupt:
                print(f'\nTest {test_func.__name__} stopped')
        return loop_wrapper
    @test_loop_wrapper
    def test_read_n_bytes(self, read_bytes:int=1):
        """
        Test receiving n bytes of data.

        :param read_bytes: number of bytes to read at once.
        """
        print(f'Reading {read_bytes} bytes')
        data = self.uart.read(size=read_bytes)
        print(data)
    @test_loop_wrapper
    def test_write_byte(self, byte:bytes):
        """
        Test writing a byte.

        :param byte: byte to write
        """
        print(f'Writing byte {format(int.from_bytes(byte, "big"), "08b")}')
        self.uart.write(byte)
    @test_loop_wrapper
    def test_write_read_byte(self, byte:bytes, 
                                   delay:float=1, 
                                   input_write_stall:bool=False):
        """
        Test writing and reading the same byte.

        :param byte: byte to write
        """
        print(f'Write byte {format(int.from_bytes(byte, "big"), "08b")}')
        self.uart.write(byte)
        data = self.uart.read(size=1)
        print(data)
    @test_loop_wrapper
    def test_write_byte_nums_0_to_255(self, delay:float=1, 
                                            input_write_stall:bool=False):
        """
        Test writing 0 to 255.

        :param delay: if not input_write_stall, delay before writing next.
        :param input_write_stall: if True, require keyboard return before 
            writing next.
        """
        for i in range(1, 255+1):
            num = int.to_bytes(i, 1, "big")
            print(f'Write {i:03} {format(i, "08b")} {num}')
            if (input_write_stall): input(f'Press enter to write')
            else: sleep(delay)
            self.uart.write(num)

# Main #########################################################################
def main():
    monitor = Monitor()
    print(monitor)
    # monitor.test_read_n_bytes(1)
    # monitor.test_write_byte(b'\xFF')
    monitor.test_write_byte_nums_0_to_255(delay=1, input_write_stall=True)
    # monitor.test_write_read_byte(b'\xAF')


if __name__ == '__main__':
    main()
