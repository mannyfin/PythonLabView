"""
This file does automatic calibration of Type C W/Re against a Type K Ch/Al therocouple

In iTools: mV40; Linear; mV; Display High/Low = Range High/Low = 40/-3
"""

from TPD.Eurotherm_Functions import *
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


""" Create Eurotherm instances """
"Create obj for reading and writing temperature to Eurotherm -- Type C"
port1 = 'COM4'
controlObj = Eurotherm(port1)
"Create obj for reading Room temperature from Eurotherm -- Type K"
port2 = 'COM5'
controlObj2 = Eurotherm(port2)

"For reading in Room Temp to correct Temp reading"
# typeC = thermocouples['C']

mV = np.array([])
typeK = np.array([])
i=0
back_to_the_future = 1985
start_time = time.time()
while back_to_the_future == 1985:
    # mV = np.append(mV,controlObj.read_val())
    # typeK = np.append(typeK, controlObj2.read_val(num_dec=2))
    try:
        time.sleep(0.2)
        # print(controlObj.read_val(), controlObj2.read_val(num_dec=1))
        print("%.3f" % (time.time()-start_time), controlObj2.read_val(num_dec=1), controlObj2.read_output())
    # i+=1
    # if i == 750:
    #     controlObj.close_me()
    #     controlObj2.close_me()
    #     break
    except:
        back_to_the_future = 1985

print(mV)
print(typeK)
df = pd.DataFrame([typeK, mV]).T
df.columns = ['Temperature', 'mV']

plt.plot(df.Temperature.values, df.mV.values)
plt.xlabel('Temperature (K)')
plt.ylabel('mV from Type C')
plt.show()


