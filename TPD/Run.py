"""

"""
import time
import numpy as np
from threading import Thread
from TPD.MassSpec_Functions import thread_read_masses
from TPD.Eurotherm_Functions import thread_send_mV_setpoint,read_Temp_value
# from TPD.Gui import emergency_stop
from TPD.Header_info import write_data, header_info
import pyqtgraph as pg
from queue import Queue
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from pyqtgraph.Qt import QtCore, QtGui


def runme(iter_freq, mv_setpoints, time_array,list_of_masses, list_of_sensitivities, sendFreq, alpha, alpha_iter,
          n, temp_plot_arr, T_array, mass_signals, setpoint_sending, temp_setpoints, curves, T_set_curve, T_read_curve,
          controlObj, controlObj2, uti1, app, win1, win2, button, button_hold, button_hold_off, stop_button, hold_button, hold_off_button, save_path,
          project_folder, experiment_name, hold_time=30):

    def emergency_stop():
        # stop increasing the temp and send a safe setpoint
        # controlObj.write_sp(0.0)
        # TODO add save data

        # from TPD.Main import cum_time, T_array, mass_signals

        controlObj.write_sp(-2.9)
        controlObj.close_me()
        controlObj2.close_me()
        time.sleep(1)
        # quit()

        os.chdir(save_path)
        os.makedirs(project_folder, exist_ok=True)
        write_data(project_folder, experiment_name, cum_time, T_array, mass_signals)

        sys.exit()

    def hold_off():
        time.sleep(hold_time)
        controlObj.write_sp(-2.9)
        controlObj.close_me()
        controlObj2.close_me()
        time.sleep(1)
        # quit()

        os.chdir(save_path)
        os.makedirs(project_folder, exist_ok=True)
        write_data(project_folder, experiment_name, cum_time, T_array, mass_signals)

        sys.exit()

    def hold_temperature():
        time.sleep(hold_time)




    button.clicked.connect(emergency_stop)
    button_hold.clicked.connect(hold_temperature)
    button_hold_off.clicked.connect(hold_off)

    cum_time = 0

    # proxy = QtGui.QGraphicsProxyWidget()
    # button = QtGui.QPushButton('STOP')
    # proxy.setWidget(button)
    # stop_button = win2.addItem(proxy)
    # button.clicked.connect(emergency_stop(controlObj))

    queue = Queue()
    # while iter_freq < len(mv_setpoints):
    while alpha_iter < len(setpoint_sending):
        start_alpha = time.time()
        # append current time to the array.
        time_array = np.append(time_array, time.time())
        # Read time and temperature data
        cum_time = np.cumsum(np.concatenate(([0], np.diff(time_array))))

        t = Thread(target=thread_read_masses, args=(uti1, list_of_masses, list_of_sensitivities, queue))
        # t = Thread(target=thread_read_masses, args=(list_of_masses, list_of_sensitivities, mass_signals))
        # cProfile.run('t.start()')
        t.start()
        # t = cProfile.run('thread_profile(list_of_masses, list_of_sensitivities, queue)')
        # print(setpoint_sending[alpha_iter])
        iter_freq = thread_send_mV_setpoint(iter_freq, mv_setpoints, setpoint_sending[alpha_iter], sendFreq, alpha,
                                            controlObj, t)
        t.join()
        response = queue.get()
        # print(alpha_iter)
        alpha_iter += 1

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

        try:
            T_set_curve.setData(x=cum_time[:len(temp_plot_arr)], y=temp_plot_arr, pen='r', name='setpoint')
        except:
            T_set_curve.setData(x=cum_time, y=temp_plot_arr[:len(cum_time)], pen='r', name='setpoint')
        # TODO read_Temp_value is a duplicate of Eurotherm.read_temp() fcn
        T_array = np.append(T_array, read_Temp_value(controlObj, controlObj2))
        T_read_curve.setData(x=cum_time, y=T_array, pen='g', name='readout')

        # TODO add masses

        if len(list_of_masses) > 0 and not None:
            for i, j, k in zip(response, list_of_masses, curves):
                mass_signals['mass' + str(j)] = np.append(mass_signals['mass' + str(j)], i)
                if alpha_iter % 4 == 0:
                    k.setData(x=T_array, y=mass_signals['mass{0}'.format(str(j))], pen='g')
                    # pg.QtGui.QApplication.processEvents()
        # for mass, mass_plot in zip(list_of_masses, curves):
        #     mass_plot.setData(x=T_array, y=mass_signals['mass{0}'.format(mass)], pen='g')

        # T_set_curve.setData(x=cum_time,y=temp_plot_arr[:len(cum_time)], pen='r',name='setpoint')
        if alpha_iter % 4 == 0:
            pg.QtGui.QApplication.processEvents()
        # uncomment if you want to see some cooldown
        if iter_freq == len(mv_setpoints):
            break

        print('total iter time = ' + str(time.time() - start_alpha))

    return T_array, cum_time, start_alpha, time_array, mass_signals
