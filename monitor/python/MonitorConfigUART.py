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
    BAUD_9600            = 9600
    BAUD_115200          = 115200
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
    baudrate      = ConfigUART.BAUD_115200
    parity        = serial.PARITY_EVEN
    device_vid    = 1659
    device_pid    = 8963

class ConfigGPSReceiver(ConfigUART):
    """
    Configuration for U-blox GPS Receiver.
        doc  -> 
            https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf
        uart ->
            https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf#page=51&zoom=100,0,525
        changing protocols ->
            https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf#page=56&zoom=100,0,444
        NMEA protocol ->
            https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf#page=153&zoom=100,0,173
        UART configuration ->
            https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf#page=468&zoom=100,0,626
    """
    baudrate      = ConfigUART.BAUD_9600
    parity        = serial.PARITY_NONE
    device_vid    = None
    device_pid    = None

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()
