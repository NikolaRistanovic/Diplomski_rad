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
siggen = Siggen_driver.siggen()
print("Initiated equpment")




print(f"Starting new : frequency 1kHz")



samples = osc.getSamples()

samplesPadded = np.zeros_like(samples,dtype=float)

samplesPadded[0] = (samples[0] *5/2048 - osc.getChannelData(1).position)*osc.getChannelData(1).scale
samplesPadded[1] = (samples[1] *5/2048 - osc.getChannelData(2).position)*osc.getChannelData(2).scale

timebase = (np.arange(len(samplesPadded[0])) - len(samplesPadded[0])//2)/osc.sampleRate

# filename = f"savesRandom/IsatMeasurement.npy"
# np.save(filename,samplesPadded)
# print(f"saved file {filename}\n\n")

Resistance = 0.1

voltage = samplesPadded[1]
Vload = samplesPadded[0] - samplesPadded[1]
current = Vload/Resistance
power = voltage*current
Pload = Vload*current
avgI = np.average(current)
avgP = np.average(power)
avgPload = np.average(Pload)

# osc.printJsonHeader()

fig, axs = plt.subplots(4,1,sharex=True)
plt.suptitle("IRLZ44N spec 100kHz,3V3 with driver,12V 100ohm")
axs[0].set_title("Vds")
axs[0].plot(timebase,voltage,label="voltage")
axs[0].grid()
axs[1].set_title("Id avg="+str(np.round(avgI*1000,2))+'mA')
axs[1].plot(timebase,current,label="current")
axs[1].grid()
axs[2].set_title("Pds, avg="+str(np.round(avgP*1000,2))+'mW')
axs[2].plot(timebase,voltage*current,label="power")
axs[2].grid()
axs[3].set_title("Pload, avg="+str(np.round(avgPload*1000,2))+'mW')
axs[3].plot(timebase,Vload*current,label="power")
axs[3].grid()
fig.tight_layout()
plt.show()

# plt.plot(voltage,current)
# plt.xlabel("voltage V")
# plt.ylabel("current A")
# plt.show()

