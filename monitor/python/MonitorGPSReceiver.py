# Imports ######################################################################
from Monitor import Monitor
from MonitorConfigUART import ConfigGPSReceiver
from MonitorTest import MonitorGPSReceiverTest

import pynmea2 as nmea

# Globals ######################################################################


# Library ######################################################################
class MonitorGPSReceiver(Monitor):
    """
    Builds on Monitor to implement an API for reading GPS data from the U-blox
    GPS Receiver.

    U-blox GPS Receiver
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
            https://www.u-blox.com/sites/default/files/products/documents/u-blox8-M8_ReceiverDescrProtSpec_UBX-13003221.pdf#page=259&zoom=100,0,0
    
    NMEA Python
        pynmea2 ->
            https://github.com/Knio/pynmea2
    """
    # constants ################################################################

    # constructor ##############################################################
    def __init__(self):
        """
        Initializes the monitor.

        :param config: configuration for the uart.
        """
        Monitor.__init__(self, ConfigGPSReceiver)

    # methods ##################################################################
    def readNMEA(self, timeout:float=None):
        """
        """
        pass
    def parseNMEA():
        """
        """
        pass


# Main #########################################################################
def main():
    monitor = MonitorGPSReceiver()
    print(monitor)

    # MonitorGPSReceiver.print_ports()

    mtester = MonitorGPSReceiverTest(monitor)

if __name__ == '__main__':
    main()
