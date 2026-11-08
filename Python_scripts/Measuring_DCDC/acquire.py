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
siggen = Siggen_driver.siggen()
siggen.reset()
print("Initiated equpment")

values = np.zeros(98)

for i in range(98):
    siggen.setDuty(i+1)
    print(siggen.read())
    time.sleep(0.5)
    voltage = osc.getAvg(1)[:-1]
    print(voltage)
    values[i] = np.float16(voltage)

    time.sleep(0.5)



filename = input("Filename to save : ")
np.save('saves/'+filename+'.npy',values)
print(f"saved file {filename}\n\n")

plt.plot(values)
plt.show()

