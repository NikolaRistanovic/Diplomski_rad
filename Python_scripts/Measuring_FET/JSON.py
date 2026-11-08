import sys
sys.path.append("..")

import DCD_DAQ
import json
import time

osc = DCD_DAQ.osciloscope(-1)


while(True):
    osc.getSamples()

    jsonHeader = osc.getJsonHeader()

    for key in jsonHeader.keys():
        if key != "CHANNEL":
            print(key,":",jsonHeader[key])
        else:
            print(key,":")
            print(jsonHeader[key][0])
            print(jsonHeader[key][1])

    time.sleep(0.5)

    for i in range(len(jsonHeader.keys())+4):
        print("\033[2K\033[A",end='')

    print("\033[2K",end="")


