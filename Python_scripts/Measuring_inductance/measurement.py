import numpy as np
import matplotlib.pyplot as plt
import DCD_DAQ
import Siggen_driver
import time
import matplotlib

matplotlib.use("qt5agg")

fig1 =plt.figure(1)
axs = fig1.subplots(2,1)

def calcImpedance(V1,V2,R):
    I = (V1-V2)/R

    Vfft = np.fft.rfft(V2,norm='forward')*2
    indexV = np.argmax(np.abs(Vfft))
    axs[0].plot(Vfft)
    axs[0].axvline(indexV,color='r')
    axs[0].set_title("Voltage")

    Ifft = np.fft.rfft(I,norm='forward')*2
    indexI = np.argmax(np.abs(Ifft))
    axs[1].plot(Ifft)
    axs[1].axvline(indexI,color='r')
    axs[1].set_title("current")

    

    print(f"Voltage : {np.abs(Vfft[indexV])}V, Current : {np.abs(Ifft[indexI])}A")
    impedance = Vfft[indexV]/Ifft[indexI]
    return impedance


print("Starting script........")
osc = DCD_DAQ.osciloscope()
siggen = Siggen_driver.siggen()
print("Initiated equpment")
time.sleep(2)
siggen.reset()
print("Reset the signal generator")
print("Starting in 2s")
time.sleep(2)

data = np.zeros((2,50),dtype=complex)

plt.ion()

for exp in range(1,6):
    for freq in range(1,10):
        frequency = freq*(10**exp)

        print(f"Starting new : frequency {freq}e{exp}")

        siggen.setFrequency(frequency)
        print("Signal gen response" + siggen.read())
        osc.setTimebase(1/frequency)
        time.sleep(2)

        data[0,(exp-1)*9+freq-1] = frequency

        samples = osc.getSamples()

        samplesPadded = np.zeros_like(samples,dtype=float)

        samplesPadded[0] = samples[0] *5/2048*osc.getChannelData(1).scale
        samplesPadded[1] = samples[1] *5/2048*osc.getChannelData(2).scale

        filename = f"smol_core2/samples{freq}e{exp}.npy"
        np.save(filename,samplesPadded)
        print(f"saved file {filename}\n\n")

        time.sleep(2)

print(data)