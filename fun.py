import matplotlib.pyplot as plt
import pandas as pd
import scipy.interpolate as interpolate
import sys
from thermocouples_reference import thermocouples
import minimalmodbus as mm
import os
import pyqtgraph as pg
import time
"""
CJC address is 215
setpoint address is 2
read current val address is 1
measured value address is 202
"""


class Eurotherm(mm.Instrument):
    def __init__(self, port, baudrate=9600, num_dec=3):
        self.num_dec = num_dec
        mm.Instrument.__init__(self, port=port, slaveaddress=1)
        self.serial.baudrate = baudrate
        self.serial.close()
        self.serial.open()
        print(str(port) + ' is open?' + str(self.serial.isOpen()))

    def close_me(self):
        # close serial port
        self.serial.close()
        return print(self.serial.isOpen())

    def open_me(self):
        # open serial port
        self.serial.open()
        return print(self.serial.isOpen())

    def read_val(self, num_dec=3):
        # read current value
        return self.read_register(1, num_dec, signed=True)

    def read_sp(self, num_dec=3):
        # read setpoint val
        return self.read_register(2, num_dec, signed=True)

    def write_sp(self,sp, num_dec=3):
        # write setpoint val
        return self.write_register(2, sp, num_dec, signed=True)

    def read_rt(self,num_dec=2):
        # read CJC temp in C to two decimals
        # if Eurotherm is not in a thermocouple mode it may read 0.0
        return self.read_register(215, 2)


def interp(inputmV, mV_table, T_table):
    """

    :param inputmV: input value to interpolate
    :param mV_table: the two mV values in between the input mV value
    :param T_table: the two Temp values in between the input corresponding mV value
    :return: interpT : interpolated Temperature
    """
    T1, T2 = T_table
    low, high = mV_table

    interpT = T1 + (T2 - T1) * (inputmV - low) / (high - low)

    return interpT

def readCJC(eurotherm_object):
    eurotherm_object.read_register(registeraddress=2, value=mVset, numberOfDecimals=3, signed=True)
def read_table(pathname, name):
    os.chdir(pathname)
    df = pd.read_excel(name)
    return df

if __name__ == "__main__":
    # labview_mV = float(input('input a number: '))
    # print(os.getcwd())
    typeC = thermocouples['C']
    file_path = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest\\'
    fname = 'Type C calibration_corrected.xlsx'
    df = read_table(file_path, fname)

    labview_mV = readCJC()
    # CJC temp in K
    CJC_temp = float(sys.argv[2])

    adjusted_mV = labview_mV + typeC.emf_mVC(CJC_temp)

    temp_df = df.iloc[(df['mV'] - adjusted_mV).abs().argsort()[:2]]

    # print(os.getcwd())
    # imported values from LabView are STRINGS, we need to cast them into floats to use them...



    # print(sys.argv[1])

    temperature = interp(adjusted_mV, temp_df['mV'], temp_df['T'])
    # print('interp temp = {0}\n'.format(round(temperature,2)))
    print('{0}'.format(round(temperature,2)))
    "plot the temperature and save the temperature value in labview"

port = 'COM5'
baudrate = 9600
testme= mm.Instrument(port, 1)
testme.baudrate = baudrate
print(testme.serial.isOpen())
testme.serial.close()
print(testme.serial.isOpen())
print(testme.read_register(2))

# real time plotting. see here:
# https://stackoverflow.com/questions/45046239/python-realtime-plot-using-pyqtgraph?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa



import matplotlib.pyplot as plt
import pandas as pd
import scipy.interpolate as interpolate
import sys
from thermocouples_reference import thermocouples
import minimalmodbus as mm
import os
import pyqtgraph as pg
import time
"""
CJC address is 215
setpoint address is 2
read current val address is 1
measured value address is 202
"""


class Eurotherm(mm.Instrument):
    def __init__(self, port, baudrate=9600, num_dec=3):
        self.num_dec = num_dec
        mm.Instrument.__init__(self, port=port, slaveaddress=1)
        self.serial.baudrate = baudrate
        self.serial.close()
        self.serial.open()
        print(str(port) + ' is open?' + str(self.serial.isOpen()))

    def close_me(self):
        # close serial port
        self.serial.close()
        return print(self.serial.isOpen())

    def open_me(self):
        # open serial port
        self.serial.open()
        return print(self.serial.isOpen())

    def read_val(self, num_dec=3):
        # read current value
        return self.read_register(1, num_dec, signed=True)

    def read_sp(self, num_dec=3):
        # read setpoint val
        return self.read_register(2, num_dec, signed=True)

    def write_sp(self,sp, num_dec=3):
        # write setpoint val
        return self.write_register(2, sp, num_dec, signed=True)

    def read_rt(self,num_dec=2):
        # read CJC temp in C to two decimals
        # if Eurotherm is not in a thermocouple mode it may read 0.0
        return self.read_register(215, 2)






test = Eurotherm('COM4')
asdf = Eurotherm('COM5')
test.close_me()
asdf.close_me()
app = pg.QtGui.QApplication([])
win = pg.GraphicsWindow(title='real time data')
p = win.addPlot(title ='the plot')
curve = p.plot()
temp =[]
rt_temp =[]
while True:
    test.open_me()
    asdf.open_me()
    temp.append(test.read_val())
    rt_temp.append(asdf.read_rt())
    curve.setData(temp)
    pg.QtGui.QApplication.processEvents()
    test.close_me()
    asdf.close_me()
    time.sleep(0.5)

import nidaqmx
from nidaqmx.constants import (
    LineGrouping, TerminalConfiguration)
import numpy as np


mass = 18
volts = mass*0.033333333
sensitivity = 4

for i in range(4):
    with nidaqmx.Task() as mass_task, nidaqmx.Task() as sens_task, nidaqmx.Task() as read_task:
        mass_task.ao_channels.add_ao_voltage_chan("Dev1/ao0", min_val=0.0, max_val=5.0)
        mass_task.write(volts, auto_start=True)

        # with nidaqmx.Task() as sens_task:
        sens_task.do_channels.add_do_chan("/Dev1/port0/line0:3",
                                          line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
        try:
            # print('N Lines 1 Sample Boolean Write: ')
            sens_task.write([False, True, False, False], auto_start=True)
        except nidaqmx.DaqError as e:
            print(e)

    # for i in range(8):
    #     with nidaqmx.Task() as read_task:
        read_task.ai_channels.add_ai_voltage_chan("Dev1/ai" + str(i), terminal_config=TerminalConfiguration.DIFFERENTIAL)
        a = read_task.read(number_of_samples_per_channel=1000)
        b = np.mean(a)
        c = b/(10^sensitivity)*(10**6)
        print(c)
