import sys
sys.path.append("..")

import numpy as np
import matplotlib.pyplot as plt
import DCD_DAQ
import Siggen_driver
import time
import matplotlib

matplotlib.use("qt5agg")




print("Starting script........")
osc = DCD_DAQ.osciloscope()
osc.reset()
print("Initiated equpment")

data = np.zeros((10,1000))

sampleNo = 0



while True:

    input("Fire?")
    samplesRaw = osc.getSamples()[0]
    samples = (samplesRaw *5/2048 - osc.getChannelData(1).position)*osc.getChannelData(1).scale
    plt.plot(samples)
    plt.show()

    text = input("Continue?[Y/N/R] : ")
    match text:
        case "Y" | "" | "y":
            data[sampleNo] = samples
            print("Saved sample",sampleNo)
            sampleNo += 1
            continue 
        case "N" | "n"    :
            break
        case "R" | "r"  :
            print("Data thrown out...")
            continue
        case _:
            print("Error invalid letter")



filename = input("Filename to save : ")
np.save('saves/'+filename+'.npy',data[:sampleNo])
print(f"saved file {filename}\n\n")

# plt.plot(values)
# plt.show()

