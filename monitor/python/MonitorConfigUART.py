# Imports ######################################################################
import serial

# Globals ######################################################################


# Library ######################################################################
# uart config ##################################################################
class ConfigUART():
    """
    Configuration for the serial port for UART.
    """
    # constants ################################################################
    TIMEOUT_BLOCKING     = None # blocks forever
    TIMEOUT_NON_BLOCKING = 0    # returns immediately
    # attributes ###############################################################
    baudrate      = None
    datasize      = serial.EIGHTBITS
    parity        = None
    stopbits      = serial.STOPBITS_ONE
    rtscts        = False
    write_timeout = TIMEOUT_BLOCKING
    read_timeout  = TIMEOUT_BLOCKING
    device_vid    = None
    device_pid    = None

class ConfigFPGA(ConfigUART):
    """
    Configuration for FPGA.
    """
    baudrate      = 115200
    parity        = serial.PARITY_EVEN
    device_vid    = 1659
    device_pid    = 8963

class ConfigGPSReceiver(ConfigUART):
    """
    Configuration for U-blox GPS Receiver.
    """
    baudrate      = 38400
    parity        = serial.PARITY_NONE
    device_vid    = 5446
    device_pid    = 425


# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()
