import pandas as pd
import os
from scipy import interpolate
import numpy as np
import sys
from thermocouples_reference import thermocouples
import minimalmodbus as mm
import time
import matplotlib.pyplot as plt
import pyqtgraph as pg
"""
1. Define input temperature and heating rate
2. Define how frequently to send new setpoint in seconds.

3a. Make array of setpoints (mV) based on frequency all the way to the highest T, say 2000 K
3b. Or make array of setpoints(mV) up to some pre-defined stop temperature
-Interpolate points in 3a/b as necessary.

4. Send these setpoints at the desired frequency

5. Read output
"""


class Eurotherm(mm.Instrument):
    def __init__(self, port, baudrate=9600, num_dec=3):
        self.num_dec = num_dec
        mm.Instrument.__init__(self, port=port, slaveaddress=1)
        self.serial.baudrate = baudrate
        self.serial.close()
        self.serial.open()
        # print(str(port) + ' is open?' + str(self.serial.isOpen()))

    def close_me(self):
        # close serial port

        # print(self.serial.isOpen())
        return self.serial.close()

    def open_me(self):
        # open serial port
        # print(self.serial.isOpen())
        return self.serial.open()


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


def interp_setpoints(low_T, high_T,df, heatingRate=7., sendFreq=0.5,log_style=False,scalar=1 ):
    """
    Make sure the column names are 'Temp' and 'mV'
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

    if log_style is False:

        """
        this is the "new" way based on the heating rate
        """
        # x_new is a linspace from low_T to high_T and the number of setpoints
        interp_T = np.arange(low_T, high_T, heatingRate*sendFreq)

        print('From {0} data points, you selected {1} setpoints!'.format(num_data, len(interp_T)))

    elif log_style is True:
        # num_setpoints = scalar *(highT-lowT)/ log10(number of datapoints between highT and lowT)
        num_setpoints = scalar*int(np.round((high_T-low_T)/np.log10(num_data),))
        """
        this is the "old" way based on the number of setpoints
        """
        # x_new is a linspace from low_T to high_T and the number of setpoints
        interp_T = np.linspace(low_T, high_T, num=num_setpoints)

        print('From {0} data points, you selected {1} setpoints!'.format(num_data, num_setpoints))

        # just in case the scalar is set too high
        if num_setpoints > len(df[df['Temp'].between(low_T, high_T)]):
            raise ValueError('Too many setpoints expected. Adjust scalar or increase temperature range')

    # I create a function f, that I will interpolate values from
    interp_fcn = interpolate.interp1d(x=df['Temp'].values, y=df['mV'].values)

    # y_new contains the mV of the interpolated T's
    interp_mV = interp_fcn(interp_T)

    # all you need to do is return y_new back into LabView
    return interp_mV


def interp_table(df):
    """
    At the end of this function, the user inputs the mV into the interpolation function and the it gives the Temp
    :param df: use mv and Temp values to create an interpolation function
    :return: interpolation function
    """
    interp_mV_function = interpolate.interp1d(x=df['mV'].values, y = df['Temp'].values)

    return interp_mV_function


def read_temp(input_mV, room_temp_mV, interp_mV_fcn):
    """
    Reads input mV and room temperature mV, then adds them together and interpolates on the table to find the Temp
    Outputs the temperature in Kelvin

    ex1.
    read_temp(0, 0.41, df)
    output: 303 #Kelvin
    ex2.
    read_temp(Eurotherm1.read_val(), Eurotherm2.read_rt(), df)

    :param input_mV: Eurotherm.read_val()
    :param room_temp_mV: Eurotherm.read_rt()
    :param table: df containing mV and Temp as column names
    :return: Temperature in Kelvin
    """

    total_mV = input_mV + room_temp_mV

    return interp_mV_fcn(total_mV)


def read_table(pathname, name):
    os.chdir(pathname)
    # df_ = pd.read_excel(name, names=['Temp','mV'])
    df_ = pd.read_csv(name, names=['Temp','mV'])
    return df_

"Read in calibration Table"
file_path = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest\\'
# fname = 'Type C calibration_corrected.xlsx'
fname = 'Type C calibration_corrected.csv'
# df = pd.read_csv('Type C calibration_corrected.csv', names=['Temp', 'mV'])
df = read_table(file_path, fname)

# create interpolated table for quickly converting mV to Temp
mV_T_table = interp_table(df)

if __name__ == "__main__":
    "Create obj for reading and writing temperature to Eurotherm"
    port1 = 'COM4'
    controlObj = Eurotherm(port1)
    "Create obj for reading Room temperature from Eurotherm"
    port2 = 'COM5'
    controlObj2 = Eurotherm(port2)


    "For reading in Room Temp to correct Temp reading"
    typeC = thermocouples['C']
    # TODO add room temp compensation

    "1."
    # start_T = 273 # will vary based on input temperature from eurotherm
    # start_T = 273.15+ controlObj2.read_rt() # will vary based on input temperature from eurotherm

    # this is the current temperature
    start_T = np.round(read_temp(
                    controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)
    end_T = 500
    heatingRate = 3 # heating rate in Kelvin per second
    "2."
    # tested down to 0.01 seconds, but it increases the amount of errors. Also total time increases as sendFreq decreases
    sendFreq = 0.3
    # alpha to shorten the send frequency such that the overall heating rate is the same.
    alpha = 0.70
    T_array = np.array([])
    time_array = np.array([])
    mv_iter=0

    "3b."
    # mVsetpoints = interp_setpoints(start_T, end_T, df, heatingRate=heatingRate, sendFreq=sendFreq)
    # subtract away room temperature...these are the values that will be sent to the Eurotherm
    mVsetpoints = interp_setpoints(start_T, end_T, df, heatingRate=heatingRate, sendFreq=sendFreq) - typeC.emf_mVC(controlObj2.read_rt())
    # print(mVsetpoints)
    "4. Send setpoints"
    j=0

    # read the current temperature on the Eurotherm
    # print('The temperature is:')
    # print(np.round(read_temp(controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2))
    # np.round(read_temp(controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)

    app = pg.QtGui.QApplication([])
    win = pg.GraphicsWindow(title='real time data')
    p = win.addPlot(title ='the plot', labels={'left':('Temperature (K)'), 'bottom':('Time(s)')})

    curve = p.plot()
    curve2 = p.plot()


    while j < 1:
        print('iteration ' + str(j))
        start = time.time()
        # time_array = np.append(time_array, start)
        for i in mVsetpoints:
            # We might briefly lose contact with the instrument, so we try sending the setpoint. if it fails, try it again
            # mV iter is just to make it easier to plot the mv setpoints
            start_alpha = time.time()
            mv_iter+=1
            try:
                print(time.time())
                controlObj.write_sp(i)
                # this alpha will try to snap the total time down to the proper rate
                time.sleep(alpha*sendFreq)

                # append temperature to array
                T_array = np.append(T_array, (np.round(read_temp(
                    controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)))
                #  append to time array
                time_array = np.append(time_array, time.time())
                # assume time_array - start is a good enough approx for the time elapsed
                curve.setData(x=time_array-start, y=T_array, pen='r')
                curve2.setData(x=time_array-start,
                               y=read_temp(mVsetpoints[:mv_iter],typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), pen='b')
                pg.QtGui.QApplication.processEvents()

                " changing alpha stuff below doesnt work, and it makes the response nonlinear. Best to keep alpha constant"
                # if mv_iter%40==0:
                # if difference between current temp and setpoint is less, then begin adjusting alpha every iteration
                # if len(time_array)>15:
                #     if (T_array[-1] - read_temp(i,typeC.emf_mVC(controlObj2.read_rt()),mV_T_table))<10:
                #         end_time = (time_array[-10] - start_alpha)
                #         alpha = alpha * (T_array[-10] - T_array[-1]) / (end_time * heatingRate)
                #         if alpha <0.1 or alpha > 2:
                #             alpha = 0.8
                #         print('alpha: '+str(alpha))
                # print(controlObj.read_sp())
                # print(controlObj.read_val())
            except (ValueError, OSError) as e:
                print(e)
                # still try to send it again
                try:
                    time.sleep(0.02)
                    controlObj.close_me()
                    controlObj.open_me()
                    controlObj.write_sp(i)


                    # append temperature to array
                    T_array = np.append(T_array, (np.round(read_temp(
                        controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)))
                    #  append to time array
                    time_array = np.append(time_array, time.time())
                except (ValueError, OSError) as e:
                    print(e)
                    time.sleep(0.1)
                    controlObj.close_me()
                    controlObj.open_me()
                    # still try to send it again for another time
                    controlObj.write_sp(i)

                    # append temperature to array
                    T_array = np.append(T_array, (np.round(read_temp(
                        controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)))
                    #  append to time array
                    time_array = np.append(time_array, time.time())
          # TODO: Handle ValueError from sending setpoints too rapidly or OSError
        end_time = (time.time()-start)
        print(end_time)
        # alpha = alpha*(end_T - start_T)/(end_time*heatingRate)
        # TODO adjust alpha inside the loop instead of after every iteration
        print('alpha: '+str(alpha))
        j+=1

    # for safety, set final setpoint back to beginning
    controlObj.write_sp(mVsetpoints[0])

    # read the temperature for cooldown for desired secs
    cooldown_time = 5
    freq = 0.25
    for i in range(int(cooldown_time/freq)):
        try:
            time.sleep(freq)
            #  append to time array

            T_array = np.append(T_array, (np.round(read_temp(
                controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)))
            # I moved the time array below the T_array in case the T_array gives an error, then the time array isnt read.
            time_array = np.append(time_array, time.time())
            curve.setData(x=time_array - start, y=T_array, pen='r')
            pg.QtGui.QApplication.processEvents()
        except (ValueError, OSError) as e:
            print(e)
            # still try to send it again
            try:
                time.sleep(0.02)
                controlObj.close_me()
                controlObj.open_me()
                controlObj.write_sp(i)
                #  append to time array


                # append temperature to array
                T_array = np.append(T_array, (np.round(read_temp(
                    controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)))
                time_array = np.append(time_array, time.time())

            except:
                try:
                    time.sleep(0.02)
                    controlObj.close_me()
                    controlObj.open_me()
                    controlObj.write_sp(i)
                    #  append to time array

                    # append temperature to array
                    T_array = np.append(T_array, (np.round(read_temp(
                        controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)))
                    time_array = np.append(time_array, time.time())
                except:
                    print('blah')


    # close ports
    try:
        controlObj.close_me()
        controlObj2.close_me()
    except:
        print('the ports were closed already!')

    # clean up time array
    time_arr = np.cumsum(np.diff(time_array))

    fig, ax = plt.subplots()
    plt.plot(time_arr, T_array[1:])
    plt.xlabel('time (s)')
    plt.ylabel('Temperature (K)')
    plt.title('Plot of Temp(K) vs. time(s)')
    plt.show()
    print('hi')


