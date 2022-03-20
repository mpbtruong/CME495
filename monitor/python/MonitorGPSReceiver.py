# Imports ######################################################################
from audioop import add
from Monitor import Monitor
from MonitorConfigUART import ConfigGPSReceiver
from MonitorTest import MonitorGPSReceiverTest

from time import time
from typing import List

import pynmea2
from pynmea2 import NMEASentence

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
    
    NMEA 
        pynmea2 ->
            doc -> 
                https://github.com/Knio/pynmea2
            NMEA attribute names by NMEA sentence type ->
                https://github.com/Knio/pynmea2/blob/master/test/test_types.py
        Sentence Types ->
            https://w3.cs.jmu.edu/bernstdh/web/common/help/nmea-sentences.php
        Raw NMEA Sentence Examples ->
            - $GNRMC,002448.00,A,5208.71026,N,10642.83221,W,0.022,,200222,,,D,V*0F\r\n
            - $GNVTG,,T,,M,0.022,N,0.041,K,D*3D\r\n
            - $GNGGA,002448.00,5208.71026,N,10642.83221,W,2,12,0.55,501.4,M,-22.6,M,,0000*77\r\n
            - $GNGSA,A,3,03,19,06,12,02,14,17,24,44,51,,,1.00,0.55,0.83,1*06\r\n
    """
    # constants ################################################################
    NMEA_FRAME_START_SEQ = b'$'
    NMEA_FRAME_END_SEQ   = b'\n'
    USE_NMEA_CHECKSUM    = True

    # talker ids
    TALKER_ID_GPS     = 'GP' # American
    TALKER_ID_SBAS    = 'GP' # Unknown
    TALKER_ID_GALILEO = 'GA' # European
    TALKER_ID_BEIDOU  = 'GB' # Chinese
    TALKER_ID_GLONASS = 'GL' # Russian
    TALKER_ID_OTHER   = 'GN' # Any combination of GNSS
    TALKER_IDS = [
        TALKER_ID_GPS, TALKER_ID_GALILEO, TALKER_ID_BEIDOU, 
        TALKER_ID_GLONASS, TALKER_ID_OTHER
    ]

    # sentence types (not exhaustive)
    GSA = 'GSA' # GPS DOP and active satellites
    GGA = 'GGA' # Global Positioning System Fix Data
    GSV = 'GSV' # Satellites in view
    GLL = 'GLL' # Geographic position, latitude and longitude (and time)
    SENTENCE_TYPES = [
        GSA, GGA, GSV, GLL
    ]
    # TODO Check what sentence types we want to display on GUI

    # exceptions ###############################################################
    class ReadNMEAFrameError(Exception):
        """
        Raised if reading an NMEA frame fails.
        """
        pass
    class ParseNMEAFrameError(Exception):
        """
        Raised if parsing an NMEA frame fails.
        """
        pass

    # constructor ##############################################################
    def __init__(self):
        """
        Initializes the monitor.

        :param config: configuration for the uart.
        """
        Monitor.__init__(self, ConfigGPSReceiver)

    # methods ##################################################################
    def sentenceToStr(self, sen:NMEASentence)->str:
        """
        """
        strSentence = f'{sen.talker}{sen.sentence_type}: '
        if sen.sentence_type == self.GGA:
            strSentence += f'TIME: {sen.timestamp}, LAT: {sen.lat}'
            strSentence += f', NUM SATS: {sen.num_sats}, ALT: {sen.altitude}'
        # elif sen.sentence_type == self.GSV:
        #     strSentence += f'NUM SATS: {sen.num_sats}'
        elif sen.sentence_type == self.GSA:
            strSentence += f'PDOP: {sen.pdop}, HDOP: {sen.hdop}, VDOP: {sen.vdop}'
        elif sen.sentence_type == self.GLL:
            strSentence += f'TIME: {sen.timestamp}, LAT: {sen.lat}, LON: {sen.lon}, STATUS: {sen.status}'
        else:
            strSentence = f'{sen}'

        # strSentence = f'{sentence}'
        return strSentence
    def readNMEAFramesSelect(self, talkers:List[str], sentence_types:List[str], 
                                   timeout:float=None)->NMEASentence:
        """
        Similar to readNMEAFrameSelect but returns sentence if the read sentence's
        address is in the addresses formed from talkers and sentence_types.

        E.g. if talkers = [GP, GA] and sentence_types = [GSA]
            then sentence is returned if the sentence address is in
            [GPGSA, GAGSA]
        """
        addresses = self.formAddresses(talkers, sentence_types)
        tstart = time()
        while True:
            if (timeout):
                dt = time() - tstart
                if (dt > timeout): raise self.ReadNMEAFrameError(f'Timed out looking for match from {addresses}')
            sentence = self.readNMEAFrame()
            if (self.checkNMEAFrameInAddresses(sentence, addresses)):
                return sentence
    def readNMEAFrameSelect(self, talker:str=None, sentence_type:str=None, 
                                  timeout:float=None)->NMEASentence:
        """
        Read a particular frame of a particular sentence type. Behaves like
        readNMEAFrame if talker and sentence_type are None.
        
        :param talker: talker id to search for (e.g. TALKER_ID_BEIDOU)
        :param sentence_type: sentence type to search for (e.g. GSA)
        :param timeout: None to block forever, 0 to try to read and instantly
            return, or the time in seconds to block for.
        :exceptions:
            ReadUartFail        : if failed to read NMEA frame.
            ParseNMEAFrameError : if failed to parse NMEA frame.
        :return: sentence matching the search criteria.
        """
        tstart = time()
        while True:
            if (timeout):
                dt = time() - tstart
                if (dt > timeout): raise self.ReadNMEAFrameError(f'Timed out looking for {talker}|{sentence_type} match')
            sentence = self.readNMEAFrame()
            if (self.checkNMEAFrameType(sentence, talker, sentence_type)):
                return sentence
    def readNMEAFrame(self, timeout:float=None)->NMEASentence:
        """
        Reads a NMEA frame from the receiver and parses it.

        :param timeout: None to block forever, 0 to try to read and instantly
            return, or the time in seconds to block for.
        :exceptions:
            ReadUartFail        : if failed to read NMEA frame.
            ParseNMEAFrameError : if failed to parse NMEA frame.
        :return: first sentence read.
        """
        # wait until start of frame
        preframe = self.read_uart_until(self.NMEA_FRAME_START_SEQ, timeout)
        # read the frame
        frame = self.read_uart_until(self.NMEA_FRAME_END_SEQ, timeout).decode()
        # parse the frame into a NMEA sentence
        sentence = self.parseNMEAFrame(frame)
        return sentence
    def parseNMEAFrame(self, frame:bytes)->NMEASentence:
        """
        Parses a NMEA frame.

        :param frame: the NMEA frame to parse.
        :return: NMEASentence.
        :exceptions:
            ParseNMEAFrameError: if failed to parse NMEA frame.
        """
        try: return pynmea2.parse(frame, check=self.USE_NMEA_CHECKSUM)
        except ValueError: raise self.ParseNMEAFrameError(f'Failed parsing NMEA frame {frame}')
    
    # helper methods ###########################################################
    @staticmethod
    def formAddresses(talkers:List[str], sentence_types:List[str])->List[str]:
        """
        Returns a list of each element in talkers concatenated with sentence_types.
        """
        addresses = []
        for talker in talkers:
            for sentence_type in sentence_types:
                address = talker + sentence_type
                addresses.append(address)
        return addresses
    @staticmethod
    def checkNMEAFrameInAddresses(sentence:NMEASentence, addresses:List[str])->bool:
        """
        Checks if the sentence's address is in addresses.
        """
        address = sentence.talker + sentence.sentence_type
        return address in addresses
    @staticmethod
    def checkNMEAFrameType(sentence:NMEASentence, 
                           talker:str=None, 
                           sentence_type:str=None)->bool:
        """
        Returns true if the sentence matches talker and/or sentence_type.
        Using None means you do not care about matching.

        :param sentence: the sentence to check
        :param talker: talker id to check for (e.g. TALKER_ID_BEIDOU)
        :param sentence_type: sentence type to check for (e.g. GSA)
        """
        is_talker        = sentence.talker == talker
        is_sentence_type = sentence.sentence_type == sentence_type
        if (talker and sentence_type): 
            return is_talker and is_sentence_type
        elif (talker): 
            return is_talker
        elif (sentence_type): 
            return is_sentence_type
        else: return True # not matching against anything so frame is ok

# Main #########################################################################
def main():
    monitor = MonitorGPSReceiver()
    print(monitor)

    # MonitorGPSReceiver.print_ports()

    mtester = MonitorGPSReceiverTest(monitor)

    # mtester.test_readNMEAFrame()
    # mtester.test_readNMEAFrameSelect()
    mtester.test_readNMEAFramesSelect()

if __name__ == '__main__':
    main()
