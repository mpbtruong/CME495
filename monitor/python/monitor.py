# Imports ######################################################################
import serial as serial

import subprocess as subprocess
from typing import List

# Globals ######################################################################


# Library ######################################################################
class Monitor():
    """
    Monitor/controller for communicating with the FPGA using UART RS-232/USB
    cable. 

    Monitors by polling for data. Controls by sending control bits to FPGA
    registers.

    pySerial -> https://pyserial.readthedocs.io/en/latest/pyserial.html
        api -> https://pyserial.readthedocs.io/en/latest/pyserial_api.html
    """
    # constants ################################################################
    BAUD_RATE = 115200
    DATA_BITS = serial.EIGHTBITS
    PARITY = serial.PARITY_NONE
    STOP_BITS = serial.STOPBITS_ONE
    FLOW_CONTROL_RTS_CTS = False

    # constructor ##############################################################
    def __init__(self, port=None, 
                       baudrate=BAUD_RATE,
                       bytesize=DATA_BITS,
                       parity=PARITY,
                       stopbits=STOP_BITS,
                       rtscts=FLOW_CONTROL_RTS_CTS
                       ):
        """
        Setup the UART serial port.
        """
        # uart config
        self.port      = port
        if (port is None): self.assign_port()
        self.baudrate  = baudrate
        self.datasize  = bytesize
        self.parity    = parity
        self.stopbits  = stopbits
        self.rtscts    = rtscts
        # serial uart instance
        self.uart:serial.Serial = serial.Serial(port=self.port,
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
        monitor += f'Monitor port={self.port} baud={self.baudrate} (rts_cts={self.rtscts})\n'
        monitor += f'   databits={self.datasize} parity={self.parity} stopbits={self.stopbits}\n'
        return monitor
    
    # methods ##################################################################
    def test_read_n_bytes(self, read_bytes:int=1):
        """
        Test receiving data.
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
        Test receiving data.
        """
        print(f'Testing test_write_byte byte={byte}')
        try:
            while True:
                self.uart.write(byte)
        except KeyboardInterrupt:
            print('Test stopped')

    def assign_port(self):
        """
        Assign the serial port to the first available port. Raises an
        exception otherwise.
        """
        try:
            self.port = self.list_ports()[0]
        except Exception:
            raise serial.SerialException("No ports found!")

    @staticmethod
    def list_ports()->List[str]:
        """
        Gets a list of currently available serial ports.
        """
        command = 'python -m serial.tools.list_ports'
        process = subprocess.run(command.split(' '), shell=True, 
                                            check=True, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
        stdout = process.stdout.decode()
        ports = [port.strip() for port in stdout.splitlines()]
        return ports

# Main #########################################################################
def main():
    monitor = Monitor()
    print(monitor)
    # monitor.test_read_n_bytes(1)
    monitor.test_write_byte(b'\x63')


if __name__ == '__main__':
    main()
