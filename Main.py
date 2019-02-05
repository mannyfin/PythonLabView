import Call_UTI
from send_multiple_setpoints import *
from read_Temp_value import *
import numpy as np
import pandas as pd
import os
import sys
from threading import Thread
from ctypes import *
import time
import subprocess
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import math
from thermocouples_reference import thermocouples
import itertools
# from initial_UTI import *

"""
THIS IS THE UNTHREADED VERSION


1. start reading the masses cycle through 1-2 times (check)
2. take the average time to cycle = total time to write setpoints (check)
3. start the 'official' program
4. read temperature, and masses and write while reading the masses
a. assume that the time to read the temperature = 0

do read mass 2 times:
get the cycle time


for asdfa:
do read mass and write sp(cycle time) use threads
thread1.join()
thread2.join()
do read value
"""

########################################################################################################################


class UTI_QMS():
    def __init__(self,path, dll='scan_single_mass.dll'):
        self.path = path
        self.dll = dll
        os.chdir(self.path)
        self.LabVIEWQMS = cdll.LoadLibrary(self.dll)
        self.LabVIEWQMS.Read_Mass_Spec.argtype = [c_int32, c_double]
        self.LabVIEWQMS.Read_Mass_Spec.restype = c_double

    def read_mass(self, _mass_, sensitivity):
        _signal_ = self.LabVIEWQMS.Read_Mass_Spec(c_int32(sensitivity), c_double(_mass_))
        # return [signal, mass, sensitivity]
        return _signal_
########################################################################################################################
#
rootdir = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest'
dlldir = 'C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_single_mass'
""" Create UTI instance """
uti1 = UTI_QMS(path=dlldir)

""" Create Eurotherm instances """
"Create obj for reading and writing temperature to Eurotherm"
port1 = 'COM4'
controlObj = Eurotherm(port1)
"Create obj for reading Room temperature from Eurotherm"
port2 = 'COM5'
controlObj2 = Eurotherm(port2)

"For reading in Room Temp to correct Temp reading"
typeC = thermocouples['C']

########################################################################################################################
""" User-Defined Parameters: """
os.chdir(rootdir)
project_folder = 'project_name'
os.makedirs(project_folder, exist_ok=True)
experiment_name ='name1.csv'
number_of_masses = 8
list_of_masses = [4.1, 12.3, 18.0, 28.1, 32.4, 38.6, 43.5, 45.7]
list_of_sensitivities = [4, 4, 4, 4, 4, 4, 4, 4]
heating_rate = 7    # K/s
os.chdir(rootdir)
with open('interp_mV_to_Temp_func.pickle', 'rb') as f:
    mV_T_table = pickle.load(f)
start_temp = np.round(read_temp(
                    controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)
end_temp = 700

assert len(list_of_masses) == number_of_masses, 'lengths do not match up'
assert len(list_of_sensitivities) == number_of_masses, 'lengths do not match up'

########################################################################################################################
#
""" Check time to loop through masses: """
no_of_loops = 3
single_read_times = []
set_read_times = []
for i in range(no_of_loops):
    start_set = time.time()
    for j in range(number_of_masses):
        start_single = time.time()
        signal = uti1.read_mass(list_of_masses[j], list_of_sensitivities[j])
        end_single = time.time() - start_single
        single_read_times.append(end_single)
    end_set = time.time() - start_set
    set_read_times.append(end_set)

mean_single = np.mean(single_read_times)
""" This should be the time taken each loop to write setpoints """
mean_set = np.mean(set_read_times)
print("Average single read time is:   {0}".format(np.round(mean_single, 4)))
print("Average set read time is:   {0}".format(np.round(mean_set, 4)))


# Initial UTI looping
# mean_single, mean_set = loop__time(number_of_masses, list_of_masses, list_of_sensitivities)


""" Determine setpoint increment """
multiple = 4 # how many times per second to change the setpoint
temp_set_incr = heating_rate * mean_set/multiple     # setpoint increment assuming each loop takes "mean_set" seconds
temp_setpoints = np.arange(start_temp, end_temp+1, temp_set_incr)
# making the list of setpoint values to be sent at each loop iteration
os.chdir(rootdir)
with open('interp_Temp_to_mV_func.pickle','rb') as interpdvalues:
    interpd = pickle.load(interpdvalues)
    # These are the mV that will be sent to the Eurotherm
    mv_setpoints = interpd(temp_setpoints - controlObj2.read_rt())

""" Set up multiple plot windows for TPD """
app = pg.QtGui.QApplication([])
win1 = pg.GraphicsWindow(title="QMS Signal Plots")
win1.resize(710, 970/4*math.ceil(number_of_masses/2))
win2 = pg.GraphicsWindow(title="Temperature Plot")
win2.resize(420, 400)

Tplot = win2.addPlot(title="Temperature (K)", labels={'bottom': 'Time(s)', 'left': 'Temperature (K)'})
Tplot.addLegend()
plots = []
for j in range(int(math.ceil(number_of_masses/2))):
    plots.append([win1.addPlot(title="m/e = {0}".format(list_of_masses[2*j+i]), labels={'bottom': 'Temperature(K)',
                                                                                        'left': 'Signal (a.u.)'})
                  for i in range(2) if 2*j+i < number_of_masses])
    win1.nextRow()

plots = list(itertools.chain.from_iterable(plots))

curves = [plots[k].plot() for k in range(number_of_masses)]

T_read_curve = Tplot.plot(name='readout')
T_set_curve = Tplot.plot(name='setpoint')

pg.QtGui.QApplication.processEvents()

""" Main script loops for TPD """

"""
Basic structure of measurement loop:
for asdfa:
do read mass and write sp(cycle time) use threads
thread1.join()
thread2.join()
do read value

"""

T_array = np.array([])
time_array = np.array([])

# Make mass spec signals a dictionary of np.arrays so we can append to and manipulate each individually
# initialize dictionary of empty arrays
mass_signals = {}
for i in list_of_masses:
    mass_signals["mass{0}".format(i)] = np.array([])


""" 
This will need to be threaded, below
"""

num_freq = 1
iter_freq = 0
temp_plot_arr = np.array([])
# this needs to be the max temperature or allowed to cut short if needed, also allow for the threading
# TODO increase frequency that setpoints are sent, maybe this fixes the tracking issue at higher temperatures.
# for i in range(50):
print('len of setpoints is: '+str(len(mv_setpoints)))
for i, v, in enumerate(mv_setpoints):
    # for i in range(len(temp_setpoints)):
    #     line below may be useful at times for debugging
    currentTime = time.time()
    # append current time to the array.
    time_array = np.append(time_array, time.time())
    # Read time and temperature data
    cum_time = np.cumsum(np.concatenate(([0], np.diff(time_array))))
    T_array = np.append(T_array, read_Temp_value())
    T_read_curve.setData(x=cum_time, y=T_array, pen='b', name='readout')
    # Write new setpoint for temperature
    try:
        # controlObj.write_sp(mv_setpoints[iter_freq])
        if iter_freq <= len(temp_setpoints) and iter_freq != 0:
            temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[multiple*i])
        else:
            temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[0])
    except IndexError as e:
        print(e)
        controlObj.write_sp(mv_setpoints[0])
    # T_set_curve.setData(x=cum_time,y=temp_setpoints[:2*i+1:2], pen='r',name='setpoint')
    # T_set_curve.setData(x=cum_time, y=temp_plot_arr[:2*len(cum_time):2], pen='r', name='setpoint')
    T_set_curve.setData(x=cum_time, y=temp_plot_arr, pen='r', name='setpoint')

    # for j in range(number_of_masses):

    for mass, sens, mass_plot in zip(list_of_masses, list_of_sensitivities, curves):
        # np.append(mass_signals["mass{0}".format(list_of_masses[j])], uti1.read_mass(list_of_masses[j],list_of_sensitivities[j]))
        mass_signals['mass{0}'.format(mass)] = np.append(mass_signals['mass{0}'.format(mass)], uti1.read_mass(mass, list_of_sensitivities[sens]))
        mass_plot.setData(x=T_array, y=mass_signals['mass{0}'.format(mass)], pen='g')
        if num_freq%2 == 0:
            try:
                if iter_freq < len(mv_setpoints):
                    controlObj.write_sp(mv_setpoints[iter_freq])
                    iter_freq+=1
                else:
                    controlObj.write_sp(mv_setpoints[0])

            except (IndexError, OSError) as e:
                print(e)
                # probably wrote past the last mv setpoint, so just go back to first setpoint....
                # this is also a safety in case theres a brief communication error
                try:
                    time.sleep(0.01)
                    controlObj.close_me()
                    controlObj.open_me()
                    if iter_freq < len(mv_setpoints):
                        controlObj.write_sp(mv_setpoints[iter_freq])
                        iter_freq += 1
                    else:
                        controlObj.write_sp(mv_setpoints[0])
                except (ValueError, OSError) as e:
                    print(e)
                    try:
                        time.sleep(0.01)
                        controlObj.close_me()
                        controlObj.open_me()
                        if iter_freq < len(mv_setpoints):
                            controlObj.write_sp(mv_setpoints[iter_freq])
                            iter_freq += 1
                        else:
                            controlObj.write_sp(mv_setpoints[0])
                    finally:
                        controlObj.close_me()
                        controlObj.open_me()
                        controlObj.write_sp(mv_setpoints[0])
                        print('give up')
            except (ValueError, OSError) as e:
                print(e)
                try:
                    time.sleep(0.01)
                    controlObj.close_me()
                    controlObj.open_me()
                    if iter_freq < len(mv_setpoints):
                        controlObj.write_sp(mv_setpoints[iter_freq])
                        iter_freq += 1
                    else:
                        controlObj.write_sp(mv_setpoints[0])
                except (ValueError, OSError) as e:
                    print(e)
                    try:
                        time.sleep(0.01)
                        controlObj.close_me()
                        controlObj.open_me()
                        if iter_freq < len(mv_setpoints):
                            controlObj.write_sp(mv_setpoints[iter_freq])
                            iter_freq += 1
                        else:
                            controlObj.write_sp(mv_setpoints[0])
                    finally:
                        controlObj.close_me()
                        controlObj.open_me()
                        controlObj.write_sp(mv_setpoints[0])
                        print('give up')

        num_freq+=1
    # update the plots after going through all the masses


    # T_set_curve.setData(x=cum_time,y=temp_plot_arr[:len(cum_time)], pen='r',name='setpoint')
    pg.QtGui.QApplication.processEvents()

    # uncomment if you want to see some cooldown
    if iter_freq == len(mv_setpoints):
        break
# include changing setpoints in stuff above

# at the very end, go back to initial mV setpoint
controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt()+273.15))

"""
read current value and add to plot, also include setpoint curve here too
"""
# T_array = np.append(T_array, read_Temp_value())
# T_read_curve.setData(x=cum_time, y=T_array)
pg.QtGui.QApplication.processEvents()

controlObj.close_me()
controlObj2.close_me()

os.chdir(project_folder)

time_Temp_arr = np.vstack((cum_time, T_array))
combined_data = pd.concat([pd.DataFrame(time_Temp_arr).T, pd.DataFrame.from_dict(mass_signals)], axis=1)
combined_data.rename(columns={0:'Time(s)', 1:'Temp(K)'}, inplace=True)

# save experiment
combined_data.to_csv(experiment_name, index=False, sep='\t')

print('hi')

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()  # Start QApplication event loop ***
