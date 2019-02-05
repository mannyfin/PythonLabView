import os
import minimalmodbus as mm
import numpy as np
from scipy import interpolate
import pandas as pd
import time
import pyqtgraph as pg
from thermocouples_reference import thermocouples
import pickle


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

    def read_val(self, num_dec=3, signed=True):
        # read current value
        return self.read_register(1, num_dec, signed=signed)

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

    def read_output(self, num_dec=1, signed=False):
        # read percent of output power to power supply
        return self.read_register(4, num_dec, signed=signed)

    def set_output(self, output, num_dec=1, signed=False):
        # set manual output power value to control power supply
        if self.read_register(273, numberOfDecimals=0, signed=False) == 0:
            self.write_register(273, 1, numberOfDecimals=0, signed=False)
        return self.write_register(3, output, numberOfDecimals=num_dec, signed=signed)


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


def thread_send_mV_setpoint(iter_freq_, mv_setpoints_,setpoint_sending, sendFreq, alpha, controlObj, child_thread):
    # alpha_iter = 0
    # test, keep alpha at 1
    alpha = 0
    iteration = 0
    length = len(setpoint_sending)
    # iter_freq_ = 1
    while child_thread.isAlive() and iteration < (length):
        # start_alpha = time.time()
        currentTime = time.time()
        # Write new setpoint for temperature
        # adjust send freq

        try:
            # if iter_freq_ < len(mv_setpoints_):
            #     # controlObj.write_sp(mv_setpoints_[iter_freq_])
            controlObj.write_sp(setpoint_sending[iteration])
                # time.sleep(alpha * sendFreq)
                # TODO might insert the sleep here
                # iter_freq_ += 1
            # else:
            #     # controlObj.write_sp(mv_setpoints_[0])
            #     controlObj.write_sp(setpoint_sending[iteration])


        except (IndexError, OSError) as e:
            # print(e)
            # probably wrote past the last mv setpoint, so just go back to first setpoint....
            # this is also a safety in case theres a brief communication error
            try:
                time.sleep(0.01)
                controlObj.close_me()
                controlObj.open_me()
                # if iter_freq_ < len(mv_setpoints_):
                    # controlObj.write_sp(mv_setpoints_[iter_freq_])
                controlObj.write_sp(setpoint_sending[iteration])
                    # iter_freq_ += 1
                # else:
                #     controlObj.write_sp(mv_setpoints_[0])
            except (ValueError, OSError) as e:
                print(e)
                try:
                    time.sleep(0.01)
                    controlObj.close_me()
                    controlObj.open_me()
                    # if iter_freq_ < len(mv_setpoints_):
                    #     controlObj.write_sp(mv_setpoints_[iter_freq_])
                    # controlObj.write_sp(setpoint_sending[iteration])
                    #     iter_freq_ += 1
                    # else:
                    #     controlObj.close_me()
                    #     controlObj.open_me()
                    #     controlObj.write_sp(mv_setpoints_[0])
                    #
                finally:
                    controlObj.close_me()
                    controlObj.open_me()
                    # controlObj.write_sp(mv_setpoints_[0])
                    controlObj.write_sp(setpoint_sending[iteration])
                    print('give up1')
        except (ValueError, OSError) as e:
            # print(e)
            try:
                time.sleep(0.01)
                controlObj.close_me()
                controlObj.open_me()
                controlObj.write_sp(setpoint_sending[iteration])
                # if iter_freq_ < len(mv_setpoints_):
                #     controlObj.write_sp(mv_setpoints_[iter_freq_])
                #     iter_freq_ += 1
                # else:
                #     controlObj.write_sp(mv_setpoints_[0])
            except (ValueError, OSError) as e:
                print(e)
                try:
                    time.sleep(0.01)
                    controlObj.close_me()
                    controlObj.open_me()
                    controlObj.write_sp(setpoint_sending[iteration])
                    # if iter_freq_ < len(mv_setpoints_):
                    #     controlObj.write_sp(mv_setpoints_[iter_freq_])
                    #     iter_freq_ += 1
                    # else:
                    #     controlObj.close_me()
                    #     controlObj.open_me()
                    #     controlObj.write_sp(mv_setpoints_[0])
                finally:
                    # controlObj.close_me()
                    # controlObj.open_me()
                    # controlObj.write_sp(mv_setpoints_[0])
                    print('give up2')
        iteration+=1
        iter_freq_+=1
        if time.time()-currentTime < sendFreq:
            time.sleep(currentTime+sendFreq-time.time())
    #     print('in loop')
    #     print(iter_freq_)
    # print(iter_freq_)
    return iter_freq_


def cooldown(secs, T_array, time_array, T_read_curve, controlObj, controlObj2):
    time_init = time.time()
    time_elapsed = 0
    while time_elapsed <= secs:
        time_array = np.append(time_array, time.time())
        cum_time = np.cumsum(np.concatenate(([0], np.diff(time_array))))
        T_array = np.append(T_array, read_Temp_value(controlObj, controlObj2))
        T_read_curve.setData(x=cum_time, y=T_array, pen='g', name='readout')
        time_elapsed = time.time() - time_init
        pg.QtGui.QApplication.processEvents()


def read_Temp_value(obj1, obj2):
    # rootdir = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest'
    # os.chdir(rootdir)
    # read Eurotherm value
    # port1 = 'COM4'
    # read room temp
    # port2 = 'COM5'
    # define eurotherms and thermocouple, and pickle
    # obj1 = Eurotherm(port1)
    # obj2 = Eurotherm(port2)
    typeC = thermocouples['C']
    with open('interp_mV_to_Temp_func.pickle', 'rb') as f:
        mV_T_table = pickle.load(f)

    # Need to return this value back to the main.py file
    try:
        return np.round(read_temp(obj1.read_val(), typeC.emf_mVC(obj2.read_rt()), mV_T_table), 2)

    except OSError:
        # do it again....
        obj1.close_me()
        obj2.close_me()
        obj1.open_me()
        obj2.open_me()

        return np.round(read_temp(obj1.read_val(), typeC.emf_mVC(obj2.read_rt()), mV_T_table), 2)

    except ValueError:
        obj1.close_me()
        obj2.close_me()
        obj1.open_me()
        obj2.open_me()

        return np.round(read_temp(obj1.read_val(), typeC.emf_mVC(obj2.read_rt()), mV_T_table), 2)


def interp_mV_to_Temp_func(start_path):
    assert type(start_path) is str, "start path must be a string"

    try:
        os.chdir(start_path + '\\TPD')
    except FileNotFoundError:
        print('path doesnt exist or is incorrect')
        quit(1)
    with open('interp_mV_to_Temp_func.pickle', 'rb') as f:
        mV_T_table = pickle.load(f)
    return mV_T_table


def interp_Temp_to_mV_func(temp_setpoints, controlObj2, start_path):
    assert type(start_path) is str, "start path must be a string"

    try:
        os.chdir(start_path + '\\TPD')
    except FileNotFoundError:
        print('path doesnt exist or is incorrect')
        quit(1)

    with open('interp_Temp_to_mV_func.pickle', 'rb') as interpdvalues:
        interpd = pickle.load(interpdvalues)
        # These are the mV that will be sent to the Eurotherm
        mv_setpoints = interpd(temp_setpoints - controlObj2.read_rt())

        return mv_setpoints, interpd


def last_setpoint(mv_setpoints, interpd, controlObj, controlObj2):
    # at the very end, go back to initial mV setpoint
    last_sp = mv_setpoints[0] - interpd(controlObj2.read_rt() + 273.15)
    try:
        controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt() + 273.15))
    except ValueError:
        try:
            controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt() + 273.15))
        except ValueError:
            try:
                controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt() + 273.15))
            except ValueError:
                print("Can't go to initial setpoint. Change in iTools")
