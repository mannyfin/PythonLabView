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
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import numpy as np
import math
from thermocouples_reference import thermocouples
import itertools
from initial_UTI import UTI_QMS, loop__time
from queue import Queue
import cProfile

"""
THIS IS THE THREADED VERSION

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



def thread_send_mV_setpoint(iter_freq_, mv_setpoints_,setpoint_sending, sendFreq, alpha, child_thread):
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
                    print('give up')
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
                    print('give up')
        iteration+=1
        iter_freq_+=1
        if time.time()-currentTime < sendFreq:
            time.sleep(currentTime+sendFreq-time.time())
    #     print('in loop')
    #     print(iter_freq_)
    # print(iter_freq_)
    return iter_freq_


def thread_read_masses(masses, sensitivities, queue):
    """
    calls initial_UTI script for reading mass signals. Passes array of masses and sensitivities
    :param masses:
    :param sensitivities:
    :param mass_signals_:
    :param queue: queue for appending results
    :return:
    """
    # with UTI_QMS() as uti2:
    #     signals = uti2.read_mass(len(masses), sensitivities, masses)
    signals = uti1.read_mass(len(masses), sensitivities, masses)
    queue.put(signals)
    # return signals


def emergency_stop():
    # stop increasing the temp and send a safe setpoint
    # controlObj.write_sp(0.0)
    controlObj.write_sp(-2.9)
    time.sleep(1)
    quit()


def cooldown(secs, T_array, time_array):
    time_init = time.time()
    time_elapsed = 0
    while time_elapsed <= secs:
        time_array = np.append(time_array, time.time())
        cum_time = np.cumsum(np.concatenate(([0], np.diff(time_array))))
        T_array = np.append(T_array, read_Temp_value(controlObj, controlObj2))
        T_read_curve.setData(x=cum_time, y=T_array, pen='b', name='readout')
        time_elapsed = time.time() - time_init
        pg.QtGui.QApplication.processEvents()

# class UTI_QMS():
#     def __init__(self,path, dll='scan_single_mass.dll'):
#         self.path = path
#         self.dll = dll
#         os.chdir(self.path)
#         self.LabVIEWQMS = cdll.LoadLibrary(self.dll)
#         self.LabVIEWQMS.Read_Mass_Spec.argtype = [c_int32, c_double]
#         self.LabVIEWQMS.Read_Mass_Spec.restype = c_double
#
#     def read_mass(self, _mass_, sensitivity):
#         _signal_ = self.LabVIEWQMS.Read_Mass_Spec(c_int32(sensitivity), c_double(_mass_))
#         # return [signal, mass, sensitivity]
#         return _signal_
########################################################################################################################

rootdir = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest'
# dlldir = 'C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_single_mass'

dlldir2 = 'C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_multiple_masses750'
dll2= 'scan_multiple_masses750.dll'
""" Create UTI instance """
# uti1 = UTI_QMS(path=dlldir2, dll=dll2)
uti1 = UTI_QMS(path=dlldir2, dll=dll2)

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

"for reading a file use syntax such as: test = pd.read_csv('name1.csv', header=0, sep='\t')"

os.chdir(rootdir)
project_folder = 'project_name'
os.makedirs(project_folder, exist_ok=True)
experiment_name ='cooling to about -1.2mV heating rate 5k per sec 8 masses.csv'
# TODO vary masses and see how that affects response
list_of_masses = [1.95734, 11.6511, 17.6364, 27.8653, 30.9313, 40, 44.06, 60.5124] #,4.1, 12.3, 28.12, 32.5]
# list_of_masses = [1.95734, 17.6364, 27.8653, 44.06] #,4.1, 12.3, 28.12, 32.5]
# list_of_masses = [17.76, 27.94, 44.06, 1.979] #,4.1, 12.3, 28.12, 32.5]
number_of_masses = len(list_of_masses)
list_of_sensitivities = [2]*number_of_masses
# try 2*heating rate...for 4 masses
heating_rate = 5.6    # K/s corresponds to ~4k/s, for 10.7 it was ~5.5k/s, its about double
cooldownsecs = 40
os.chdir(rootdir)
with open('interp_mV_to_Temp_func.pickle', 'rb') as f:
    mV_T_table = pickle.load(f)
start_temp = np.round(read_temp(
                    controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)
end_temp = 1000

assert len(list_of_masses) == number_of_masses, 'lengths do not match up'
assert len(list_of_sensitivities) == number_of_masses, 'lengths do not match up'
assert len(list_of_masses) == len(set(list_of_masses)), 'you have duplicate masses being monitored'

########################################################################################################################

""" Check time to loop through masses: """
# Initial UTI looping
mean_set = loop__time(number_of_masses, list_of_masses, list_of_sensitivities)


""" Determine setpoint increment """
# multiple = 2 # how many times per second to change the setpoint
# temp_set_incr = heating_rate * mean_set/multiple     # setpoint increment assuming each loop takes "mean_set" seconds

sendFreq = 0.06
alpha = 0
# heating_rate = desired_heating_rate * 1.8
# rate_adjust = 1.9
# temp_set_incr = heating_rate * data_freq * rate_adjust    # setpoint increment assuming each loop takes "mean_set" seconds
temp_set_incr = heating_rate * sendFreq  # setpoint increment assuming each loop takes "mean_set" seconds
# temp_set_incr = heating_rate * sendFreq*1.75   # setpoint increment assuming each loop takes "mean_set" seconds
temp_setpoints = np.arange(start_temp, end_temp+1, temp_set_incr)
# making the list of setpoint values to be sent at each loop iteration


os.chdir(rootdir)
with open('interp_Temp_to_mV_func.pickle','rb') as interpdvalues:
    interpd = pickle.load(interpdvalues)
    # These are the mV that will be sent to the Eurotherm
    mv_setpoints = interpd(temp_setpoints - controlObj2.read_rt())

n = int(np.ceil(mean_set/sendFreq))
setpoint_sending = [mv_setpoints[i:i+n] for i in range(0, len(mv_setpoints),n)]
""" Set up multiple plot windows for TPD """
app = pg.QtGui.QApplication([])
win1 = pg.GraphicsWindow(title="QMS Signal Plots")
win1.setGeometry(800,75,710, 970/4*math.ceil(number_of_masses/2))
# win1.resize(710, 970/4*math.ceil(number_of_masses/2))
win2 = pg.GraphicsWindow(title="Temperature Plot")
win2.setGeometry(250,250, 420, 400)


proxy = QtGui.QGraphicsProxyWidget()
button = QtGui.QPushButton('STOP')
proxy.setWidget(button)

Tplot = win2.addPlot(title="Temperature (K)", labels={'bottom': 'Time(s)', 'left': 'Temperature (K)'})
Tplot.addLegend()
Tplot.showGrid(x=True, y=True, alpha=1)

stop_button = win2.addItem(proxy)
button.clicked.connect(emergency_stop)

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

# num_freq = 1
iter_freq = 0
temp_plot_arr = np.array([])
# this needs to be the max temperature or allowed to cut short if needed, also allow for the threading
# TODO increase frequency that setpoints are sent, maybe this fixes the tracking issue at higher temperatures.
# for i in range(50):
print('len of setpoints is: '+str(len(mv_setpoints)))

queue = Queue()
alpha_iter = 0


def runme(iter_freq, mv_setpoints, time_array,list_of_masses, list_of_sensitivities, queue, sendFreq, alpha, alpha_iter, n, temp_plot_arr, T_array, mass_signals):
    cum_time = 0
    # while iter_freq < len(mv_setpoints):
    while alpha_iter < len(setpoint_sending):
        start_alpha = time.time()
        # append current time to the array.
        time_array = np.append(time_array, time.time())
        # Read time and temperature data
        cum_time = np.cumsum(np.concatenate(([0], np.diff(time_array))))

        t = Thread(target=thread_read_masses, args=(list_of_masses, list_of_sensitivities, queue))
        # t = Thread(target=thread_read_masses, args=(list_of_masses, list_of_sensitivities, mass_signals))
        # cProfile.run('t.start()')
        t.start()
        # t = cProfile.run('thread_profile(list_of_masses, list_of_sensitivities, queue)')
        # print(setpoint_sending[alpha_iter])
        iter_freq = thread_send_mV_setpoint(iter_freq, mv_setpoints, setpoint_sending[alpha_iter], sendFreq, alpha, t)
        t.join()
        response = queue.get()
        # print(alpha_iter)
        alpha_iter += 1
        # print('alpha iter ' + str(alpha_iter))
        # print('alpha iter*n  ' + str(alpha_iter*n))
        # results.append(response)

        # Write new setpoint for temperature
        # try:
        #     # controlObj.write_sp(mv_setpoints[iter_freq])
        #     if iter_freq <= len(temp_setpoints) and iter_freq != 0:
        #         # temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[multiple*i])
        #         temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[iter_freq])
        #     else:
        #         temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[0])
        # except IndexError as e:
        #     print(e)
        #     controlObj.write_sp(mv_setpoints[0])

        try:
            # controlObj.write_sp(mv_setpoints[iter_freq])
            if alpha_iter*n <= len(temp_setpoints) and alpha_iter != 0:
                # temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[multiple*i])
                temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[iter_freq])
            else:
                temp_plot_arr = np.append(temp_plot_arr, temp_setpoints[0])
        except IndexError as e:
            print(e)
            controlObj.write_sp(mv_setpoints[0])
        # T_set_curve.setData(x=cum_time,y=temp_setpoints[:2*i+1:2], pen='r',name='setpoint')
        # T_set_curve.setData(x=cum_time, y=temp_plot_arr[:2*len(cum_time):2], pen='r', name='setpoint')

        try:
            T_set_curve.setData(x=cum_time[:len(temp_plot_arr)], y=temp_plot_arr, pen='r', name='setpoint')
        except:
            T_set_curve.setData(x=cum_time, y=temp_plot_arr[:len(cum_time)], pen='r', name='setpoint')
        # TODO read_Temp_value is a duplicate of Eurotherm.read_temp() fcn
        T_array = np.append(T_array, read_Temp_value(controlObj, controlObj2))
        T_read_curve.setData(x=cum_time, y=T_array, pen='b', name='readout')

        # TODO add masses
        for i, j, k in zip(response, list_of_masses, curves):
            mass_signals['mass' + str(j)] = np.append(mass_signals['mass' + str(j)], i)
            if alpha_iter % 4 == 0:
                k.setData(x=T_array, y=mass_signals['mass{0}'.format(str(j))], pen='g')
                pg.QtGui.QApplication.processEvents()
        # for mass, mass_plot in zip(list_of_masses, curves):
        #     mass_plot.setData(x=T_array, y=mass_signals['mass{0}'.format(mass)], pen='g')

        # T_set_curve.setData(x=cum_time,y=temp_plot_arr[:len(cum_time)], pen='r',name='setpoint')

        # uncomment if you want to see some cooldown
        if iter_freq == len(mv_setpoints):
            break

        print('total iter time = ' + str(time.time() - start_alpha))

    return T_array, cum_time, start_alpha, time_array

# cProfile.run('runme(iter_freq, mv_setpoints, time_array,list_of_masses, list_of_sensitivities, queue, sendFreq, alpha, alpha_iter,temp_plot_arr, T_array, mass_signals)')
# include changing setpoints in stuff above
T_array, cum_time, start_alpha, time_array=runme(iter_freq, mv_setpoints, time_array,list_of_masses, list_of_sensitivities, queue, sendFreq, alpha, alpha_iter, n, temp_plot_arr, T_array, mass_signals)
# at the very end, go back to initial mV setpoint
last_sp = mv_setpoints[0] - interpd(controlObj2.read_rt()+273.15)
try:
    controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt()+273.15))
except ValueError:
    try:
        controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt() + 273.15))
    except ValueError:
        try:
            controlObj.write_sp(mv_setpoints[0] - interpd(controlObj2.read_rt() + 273.15))
        except ValueError:
            print("Can't go to initial setpoint. Change in iTools")

"""
read current value and add to plot, also include setpoint curve here too
"""
# T_array = np.append(T_array, read_Temp_value())
# T_read_curve.setData(x=cum_time, y=T_array)
pg.QtGui.QApplication.processEvents()

cooldown(cooldownsecs, T_array, time_array)
pg.QtGui.QApplication.processEvents()

controlObj.close_me()
controlObj2.close_me()

os.chdir(project_folder)

time_Temp_arr = np.vstack((cum_time, T_array))
combined_data = pd.concat([pd.DataFrame(time_Temp_arr).T, pd.DataFrame.from_dict(mass_signals)], axis=1)
combined_data.rename(columns={0: 'Time(s)', 1: 'Temp(K)'}, inplace=True)

# save experiment
combined_data.to_csv(experiment_name, index=False, sep='\t')

# cooldown(cooldownsecs, T_array, time_array)
# pg.QtGui.QApplication.processEvents()

# gradT = np.gradient(combined_data['Temp(K)'],0.8)
delta_time = combined_data['Time(s)'].diff()
delta_time.dropna(inplace=True)
delta_temp = combined_data['Temp(K)'].diff()
delta_temp.dropna(inplace=True)
gradT = delta_temp.divide(delta_time)
fig, ax = plt.subplots()
ax.plot(combined_data['Time(s)'].loc[1:], gradT)
plt.xlabel('Time (sec)')
plt.ylabel('Heating Rate (K/sec)')
print('mean heating rate: '+str(gradT.loc[25:].mean()))
plt.show()

print('hi')
# # test = pd.read_csv(experiment_name, header=0, sep='\t')
# gradT = np.gradient(combined_data['Temp(K)'],1.1)
# fig, ax = plt.subplots()
# ax.plot(combined_data['Time(s)'], gradT)
# plt.show()


if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()  # Start QApplication event loop ***
