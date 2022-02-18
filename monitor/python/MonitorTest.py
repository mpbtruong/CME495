# Imports ######################################################################
from distutils import command
from time import sleep


# Globals ######################################################################


# Library ######################################################################

# test case loop wrapper #######################################################
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

# test classes #################################################################
class MonitorTest():
    """
    Test class for the Monitor class.
    """
    def __init__(self, monitor):
        """
        Initialize the test class.
        """
        self.monitor = monitor
    
    # test cases ###############################################################
    @test_loop_wrapper
    def test_read_n_bytes(self, read_bytes:int=1):
        """
        Test receiving n bytes of data.

        :param read_bytes: number of bytes to read at once.
        """
        print(f'\nReading {read_bytes} byte(s)')
        data = self.monitor.read_uart(num_bytes=read_bytes)
        i_data = int.from_bytes(data, 'big')
        print(f'Received {i_data} | {format(i_data, "08b")} | {hex(i_data)}')
    @test_loop_wrapper
    def test_write_byte(self, byte:bytes):
        """
        Test writing a byte.

        :param byte: byte to write
        """
        print(f'Writing byte {format(int.from_bytes(byte, "big"), "08b")}')
        self.monitor.write_uart(byte)
    @test_loop_wrapper
    def test_write_read_byte(self, byte:bytes, 
                                   delay:float=1, 
                                   input_write_stall:bool=False):
        """
        Test writing and reading the same byte.

        :param byte: byte to write
        """
        print(f'Write byte {format(int.from_bytes(byte, "big"), "08b")}')
        self.monitor.write_uart(byte)
        data = self.monitor.read_uart(num_bytes=1)
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
        for i in range(0, 255+1):
            num = int.to_bytes(i, 1, "big")
            print(f'\nWrite {i:03} {format(i, "08b")} {hex(i)}')
            if (input_write_stall): input(f'Press enter to write')
            else: sleep(delay)
            self.monitor.write_uart(num)
    @test_loop_wrapper
    def test_write_byte_prompt(self):
        """
        Write a byte given stdin input.

        stdin int    : 0-255
        stdin hex    : a9, ff, B3, etc.
        stdin binary : 10100101, etc
        """
        i_byte_str = input(f'\nEnter byte to write: ')
        try:
            if (len(i_byte_str) == 8):
                # binary
                w_int  = int(i_byte_str, 2)
                w_byte = int.to_bytes(w_int, 1, "big")
            elif (len(i_byte_str) in (1,2)):
                # hex
                w_int  = int(i_byte_str, 16)
                w_byte = int.to_bytes(w_int, 1, "big")
            else: return
        except ValueError: return
        print(f'Writing {w_int} | {format(w_int, "08b")} | {hex(w_int)}')
        self.monitor.write_uart(w_byte)
    @test_loop_wrapper
    def test_write_bytes_prompt(self):
        """
        Write a series of bytes to the uart given hex input.

        stdin: 010203, af BD 09, etc
        """
        i_byte_str = input(f'\nEnter bytes to write (hex): ')
        if (not i_byte_str): return
        try: w_bytes = bytes.fromhex(i_byte_str)
        except ValueError: return
        print(f'Writing 0x{w_bytes.hex().upper()}')
        if (not self.monitor.write_uart(w_bytes)): 
            print('Uart failed to write data')
    @test_loop_wrapper
    def test_rts_cts(self):
        """
        Tests the state of the rts/cts flow control signals.

        stdin: t (to request) or f (stop request) to send (RTS). 
        """
        print(f'\nRTS={self.monitor.readRTS()} CTS={self.monitor.readCTS()}')
        request = input(f'Set RTS state (t/f): ')
        if   (request == 't'): self.monitor.setRTS(True)
        elif (request == 'f'): self.monitor.setRTS(False)
        print(f'RTS={self.monitor.readRTS()} CTS={self.monitor.readCTS()}')
    @test_loop_wrapper
    def test_write_byte_uart_flow(self):
        """
        Tests writing a byte to the uart using flow control RTS/CTS.
        """
        i_byte_str = input(f'\nEnter byte to write (hex): ')
        if (not i_byte_str and len(i_byte_str) != 2): return
        try: w_byte = bytes.fromhex(i_byte_str)
        except ValueError: return
        print(f'Writing 0x{w_byte.hex().upper()}')
        if (not self.monitor.write_byte_uart_flow(w_byte)): 
            print('Uart failed to write data')


class MonitorFPGATest(MonitorTest):
    """
    Test class for the MonitorFPGA class.
    """
    def __init__(self, monitor):
        """
        Initialize the test class.
        """
        MonitorTest.__init__(self, monitor)
    
    # test cases ###############################################################
    @test_loop_wrapper
    def test_execute_command(self):
        """
        Tests executing FPGA commands.

        stdin: 
            - command id (cid) to run.
            - rw status (r or w) to choose read or write.
            - bytes in hex to write if rw = 'w'
        """
        try:
            cid = int(input(f'\nEnter command id to execute: '))
            cmd = self.monitor.get_command_by_id(cid)
        except ValueError: return
        except KeyError: return
        print(cmd)
        rw = input(f'Read or write (r/w): ')
        if (rw not in ['r','w']): return
        try:
            if (rw == 'w'):
                wbytes = bytes.fromhex(input(f'Enter {cmd.no_wbytes} byte(s) to write: '))
                if (len(wbytes) != cmd.no_wbytes): return
                cmd.wbytes = wbytes
        except ValueError: return
        print('Executing command')
        print(cmd)
        self.monitor.execute_command(cmd, rw, timeout=None)
        print(cmd)

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()
