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
    PARITY = serial.PARITY_NONE
    STOP_BITS = serial.STOPBITS_ONE
    FLOW_CONTROL_RTS_CTS = False

    USB_TO_SERIAL_HWID='USB VID:PID=067B:2303 SER= LOCATION=1-5'

    # constructor ##############################################################
    def __init__(self, baudrate=BAUD_RATE,
                       bytesize=DATA_BITS,
                       parity=PARITY,
                       stopbits=STOP_BITS,
                       rtscts=FLOW_CONTROL_RTS_CTS
                       ):
        """
        Setup the UART serial port.
        """
        # uart config
        self.port      = self.assign_port(device_hwid=self.USB_TO_SERIAL_HWID)
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
        return monitor
    
    # methods ##################################################################
    def assign_port(self, device_hwid):
        """
        Assign the serial port to the first available port. Raises an
        exception otherwise.

        :return: ListPortInfo of serial port.
        """
        try:
            ports = self.list_ports()
            for port in ports:
                if (port.hwid == device_hwid): return port   
        except Exception:
            raise serial.SerialException("No ports found!")

    @staticmethod
    def list_ports():
        """
        Gets a list of currently available serial ports.

        :return: List[ListPortInfo]
        """
        ports = serial_list_ports.comports()
        # for port in ports:
        #     print(f'{port.device} | {port.description} | {port.hwid}')
        return ports

    # test cases ###############################################################
    def test_read_n_bytes(self, read_bytes:int=1):
        """
        Test receiving n bytes of data.
        """
        print(f'Test test_read_n_bytes read_bytes={read_bytes}')
        try:
            while True:
                data = self.uart.read(size=read_bytes)
                print(data)
        except KeyboardInterrupt:
            print('Test stopped')
    
    def test_write_byte(self, byte:bytes):
        """
        Test writing a byte.
        """
        print(f'Testing test_write_byte byte={format(int.from_bytes(byte, "big"), "08b")}')
        try:
            while True:
                self.uart.write(byte)
        except KeyboardInterrupt:
            print('Test stopped')
    def test_write_read_byte(self, byte:bytes):
        """
        Test writing and reading the same byte.
        """
        print(f'Testing test_write_read_byte byte={format(int.from_bytes(byte, "big"), "08b")}')
        try:
            while True:
                self.uart.write(byte)
                data = self.uart.read(size=1)
                print(data)
        except KeyboardInterrupt:
            print('Test stopped')
    def test_write_byte_nums_0_to_255(self, delay:float=1):
        """
        Test writing 0 to 255.
        """
        print(f'Testing test_write_byte_nums_0_to_255')
        try:
            while True:
                for i in range(1, 255+1):
                    num = int.to_bytes(i, 1, "big")
                    print(f'Writing {i:03} {format(i, "08b")} {num}')
                    self.uart.write(num)
                    sleep(delay)
        except KeyboardInterrupt:
            print('Test stopped')
# Main #########################################################################
def main():
    monitor = Monitor()
    print(monitor)
    # monitor.test_read_n_bytes(1)
    # monitor.test_write_byte(b'\xFF')
    # monitor.test_write_byte_nums_0_to_255()
    # monitor.test_write_read_byte(b'\xAF')


if __name__ == '__main__':
    main()
