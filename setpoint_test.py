import sys
import pandas as pd
import numpy as np
import os
from scipy import interpolate
import minimalmodbus as mm
import time
import winsound

def interp_setpoints(low_T, high_T,df,scalar=1, ):
    """
    :param low_T: input low T, should be within range on the df Table
    :param high_T: input high T, should be within range on the df Table
    :param df: Table of values for the Type C thermocouple, but could be any table in principle
    :param scalar: scalar to multiply by the number of calculated setpoints, will raise an error if num_setpoints >
    number of datapoints.
    :return: interpolated mV values for the LabView program
    """

    assert low_T < high_T, 'low T is not lower than high T!'
    assert low_T >= df['Temp'].min(), 'low T is lower than on the calibration table'
    assert high_T <= df['Temp'].max(), 'high T is higher than on the calibration table'

    # calculate the length of the data between lowT and highT
    num_data = len(df[df['Temp'].between(low_T, high_T)])

    # num_setpoints = scalar *(highT-lowT)/ log10(number of datapoints between highT and lowT)
    num_setpoints = scalar*int(np.round((high_T-low_T)/np.log10(num_data),))

    print('From {0} data points, you selected {1} setpoints!'.format(num_data, num_setpoints))

    # just in case the scalar is set too high
    if num_setpoints > len(df[df['Temp'].between(low_T, high_T)]):
        raise ValueError('Too many setpoints expected. Adjust scalar or increase temperature range')

    # I create a function f, that I will interpolate values from
    interp_fcn = interpolate.interp1d(x=df['Temp'].values, y=df['mV'].values)
    # x_new is a linspace from low_T to high_T and the number of setpoints
    interp_T = np.linspace(low_T, high_T, num=num_setpoints)
    # y_new contains the mV of the interpolated T's
    interp_mV = interp_fcn(interp_T)

    # all you need to do is return y_new back into LabView
    return interp_mV
    # see here for ref:
    # https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.interpolate.interp1d.html#scipy.interpolate.interp1d


if __name__ == '__main__':
    # change the working directory to the one below
    os.chdir('C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest\\')
    # input temperature ranges from Labview
    # low_T = float(sys.argv[1])
    # high_T = float(sys.argv[2])

    # for testing...comment these two lines out for Labview
    low_T = 100
    high_T = 200

    # scalar to multiply by to adjust the number of setpoints desired
    scalar = 1
    # read in the csv file
    df = pd.read_csv('Type C calibration_corrected.csv', names=['Temp', 'mV'])
    interpmV = interp_setpoints(low_T, high_T, df, scalar)

    print("you've been interp'd!")


# connect to eurotherm --may not need this for the program if you are going to write to the device in LabView
port = 'COM4'
baudrate = 9600
eurotherm = mm.Instrument(port, 1)
eurotherm.serial.baudrate = baudrate

# -(2**16 - eurotherm.read_register(2))/1000
# i = 10

# def __enter__(self):
#     self.

# with mm.Instrument(port, 1) as eurotherm:
eurotherm.serial.baudrate = baudrate
eurotherm.serial.close()
for _mV_ in interpmV:
    # writing
    eurotherm.serial.open()
    eurotherm.write_register(registeraddress=2, value=_mV_, numberOfDecimals=3, signed=True)
    print(eurotherm.read_register(registeraddress=2, numberOfDecimals=3, signed=True))

# eurotherm.write_register(2,40)
    eurotherm.write_register(registeraddress=2, value=interpmV[0], numberOfDecimals=3, signed=True)
    eurotherm.serial.close()
    winsound.Beep(2500, 50)
    time.sleep(1)

winsound.Beep(500, 500)
eurotherm.serial.close()
print(eurotherm.serial.isOpen())


