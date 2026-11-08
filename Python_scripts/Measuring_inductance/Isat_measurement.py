import numpy as np
import matplotlib.pyplot as plt
import DCD_DAQ
import Siggen_driver
import time
import matplotlib

matplotlib.use("qt5agg")




print("Starting script........")
osc = DCD_DAQ.osciloscope()
siggen = Siggen_driver.siggen()
print("Initiated equpment")




print(f"Starting new : frequency 1kHz")



samples = osc.getSamples()

samplesPadded = np.zeros_like(samples,dtype=float)

samplesPadded[0] = samples[0] *5/2048*osc.getChannelData(1).scale
samplesPadded[1] = samples[1] *5/2048*osc.getChannelData(2).scale

filename = f"savesRandom/IsatMeasurement.npy"
np.save(filename,samplesPadded)
print(f"saved file {filename}\n\n")

voltage = samplesPadded[1]
current = (samplesPadded[0] - samplesPadded[1])/1000

osc.printJsonHeader()

fig, axs = plt.subplots(2,1)

axs[0].plot(voltage,label="voltage")
axs[1].plot(current,label="current")
plt.show()

plt.plot(voltage,current)
plt.xlabel("voltage V")
plt.ylabel("current A")
plt.show()

