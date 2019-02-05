import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from itertools import chain
from TPD.Header_info import header_info, write_data
import math
import time
import sys
import os


# def emergency_stop(controlObj_=controlObj):
#     # stop increasing the temp and send a safe setpoint
#     # controlObj.write_sp(0.0)
#     # TODO add save data
#     controlObj_.write_sp(-2.9)
#     time.sleep(1)
#     quit()

# TODO shouldn't this be a class now?
def initialize_gui(number_of_masses, list_of_masses, controlObj, controlObj2):

    # def emergency_stop():
    #     # stop increasing the temp and send a safe setpoint
    #     # controlObj.write_sp(0.0)
    #     # TODO add save data
    #
    #     # from TPD.Main import cum_time, T_array, mass_signals
    #
    #     controlObj.write_sp(-2.9)
    #     controlObj.close_me()
    #     controlObj2.close_me()
    #     time.sleep(1)
    #     # quit()
    #
    #     # os.chdir(save_path)
    #     # os.makedirs(project_folder, exist_ok=True)
    #     # write_data(project_folder, experiment_name, cum_time, T_array, mass_signals)
    #
    #     sys.exit()
    #
    # def hold_temperature():
    #     # hold_sp = controlObj.read_sp()
    #     # hold_array = [hold_sp]*len(mv_setpoints)
    #     # mv_setpoints = hold_array
    #     # controlObj.write_sp(hold_sp)
    #     time.sleep(hold_time)


    """ Set up multiple plot windows for TPD """
    app = pg.QtGui.QApplication([])
    if len(list_of_masses) > 0 and not None:
        win1 = pg.GraphicsWindow(title="QMS Signal Plots")
        win1.setGeometry(800,75,710, 970/4*math.ceil(number_of_masses/2))

        plots = []
        for j in range(int(math.ceil(number_of_masses / 2))):
            plots.append(
                [win1.addPlot(title="m/e = {0}".format(list_of_masses[2 * j + i]), labels={'bottom': 'Temperature(K)',
                                                                                           'left': 'Signal (a.u.)'})
                 for i in range(2) if 2 * j + i < number_of_masses])
            win1.nextRow()

        plots = list(chain.from_iterable(plots))
        # plots = list(itertools.chain.from_iterable(plots))

        curves = [plots[k].plot() for k in range(number_of_masses)]
    else:
        win1, curves = [],[]
    # win1.resize(710, 970/4*math.ceil(number_of_masses/2))
    win2 = pg.GraphicsWindow(title="Temperature Plot")
    win2.setGeometry(250,250, 420, 400)


    proxy = QtGui.QGraphicsProxyWidget()
    button = QtGui.QPushButton('STOP')
    proxy.setWidget(button)

    proxy_hold = QtGui.QGraphicsProxyWidget()
    button_hold = QtGui.QPushButton('HOLD')
    proxy_hold.setWidget(button_hold)

    proxy_hold_off = QtGui.QGraphicsProxyWidget()
    button_hold_off = QtGui.QPushButton('HOLD --> STOP')
    proxy_hold_off.setWidget(button_hold_off)

    Tplot = win2.addPlot(title="Temperature (K)", labels={'bottom': 'Time(s)', 'left': 'Temperature (K)'})
    Tplot.addLegend()
    Tplot.showGrid(x=True, y=True, alpha=1)

    stop_button = win2.addItem(proxy)
    # button.clicked.connect(emergency_stop)
    hold_button = win2.addItem(proxy_hold)
    # button_hold.clicked.connect(hold_temperature)
    hold_off_button = win2.addItem(proxy_hold_off)

    T_read_curve = Tplot.plot(name='readout')
    T_set_curve = Tplot.plot(name='setpoint')

    pg.QtGui.QApplication.processEvents()

    return curves, T_read_curve, T_set_curve,  app, win1, win2, button, button_hold, button_hold_off, stop_button, hold_button, hold_off_button
