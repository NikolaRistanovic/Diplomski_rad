import Siggen_driver
import matplotlib.pyplot as plt
import numpy as np
import time

siggen = Siggen_driver.siggen()


for i in range(10):
    freq = (i+1)*1e4
    siggen.setFrequency(freq)
    print(siggen.read())
    print(f"freq set{freq}")
    time.sleep(1)