### read data from a AG051F OWON
import usb.core
import numpy as np

# 0 *IDN? /*Query ID to check the operating state*/
# 1 :CHAN CH1 /*Set current channel as CH1*/
# 2 :FUNC:SINE:LOAD OFF /*Set the load as High Z*/
# 3 :FUNC:SINE:FREQ 20000 /*Set the frequency of the sine wave*/
# 4 :FUNC:SINE:AMPL 2.5 /*Set the amplitude*/
# 5 :FUNC:SINE:OFFS 0.5 /*Set the offset*/
# 6 :CHAN:CH1 ON /*Enable the connector of CH1 at front panel*/

class siggen:

    def __init__(self,verbose=0):
        self.__verbose = verbose
        self.__dev = usb.core.find(idVendor=0x5345, idProduct=0x1234, product="AG051_F")
        if self.__dev is None:
            raise ValueError('Device not found')
        else:
            if verbose >= 2:
                print(self.__dev)
            self.__dev.set_configuration()


    def read(self):
        out = self.__dev.read(0x81,1000,5000).tobytes().decode("utf-8")
        return out

    def write(self,param):
        self.__dev.write(0x3,param)
        return

    def setFrequency(self,Frequency):
        self.write(":FUNC:SINE:FREQ "+str(Frequency))

    def setVoltage(self,Voltage):
        self.write(":FUNC:SINE:AMPL "+str(Voltage))

    def reset(self):
        self.__dev.reset()

    def setChannelState(self,chNo,state):
        if chNo not in (1,2):
            raise ValueError("invalid channel number")

        if state not in ("ON","OFF",0,1):
            raise ValueError("Invalid state for channel")

        if state in (1,"ON"):
            self.write(f":CHAN:CH{chNo} ON")
        else:
            self.write(f":CHAN:CH{chNo} OFF")