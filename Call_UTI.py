from ctypes import *
import ctypes
import os
import numpy as np
import time
import sys
import pyqtgraph as pg

# if __name__ == "__main__":
def call_uti():
    path0 = 'C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_single_mass'
    dll0 = 'scan_single_mass.dll'

    # change directory path and load the dll library
    os.chdir(path0)
    LabVIEWQMS = cdll.LoadLibrary(dll0)
    # set input and output arg types
    LabVIEWQMS.Read_Mass_Spec.argtype = [c_int32, c_double]
    LabVIEWQMS.Read_Mass_Spec.restype = c_double
    # sensitivity should be between 0 to 7
    """
    sensitivity: [0, 1, 2, 3, 4, 5, 6, 7]
    corresponds: [1e-5, 1e-6, 1e-7, 1e-8, 1e-9, 1e-10, 1e-11, 1e-12]
    """
    sensitivity = 4
    assert (sensitivity >=0 and sensitivity <=7), "sensitivity out of range"
    mass = 17.7
    # call API and assign current reading to signal

    start = time.time()
    signal = LabVIEWQMS.Read_Mass_Spec(c_int32(sensitivity), c_double(mass))
    end = time.time() - start
    print('\n\n\n')

    app = pg.QtGui.QApplication([])
    win = pg.GraphicsWindow(title='real time data')
    p = win.addPlot(title ='the plot', labels={'left':('Mass signal (amu)'), 'bottom':('Time(s)')})

    curve = p.plot()
    curve2 = p.plot()

    mass1 = np.array([])
    mass2 = np.array([])

    # TODO change for loop range to be single iteration
    for j in range(100):
        """check if signal is noisy"""
        for mass in [17.75, 27.9]:

            start = time.time()
            if mass == 17.75:
                mass1 = np.append(mass1,LabVIEWQMS.Read_Mass_Spec( c_int32(sensitivity), c_double(mass)))
                curve.setData(mass1, pen='b')
            else:
                mass2 = np.append(mass2,LabVIEWQMS.Read_Mass_Spec( c_int32(sensitivity), c_double(mass)))
                curve2.setData(mass2, pen='r')
            end = time.time()-start
            pg.QtGui.QApplication.processEvents()
            print('end time is: {0}'.format(end))
            # print("%s sensitity and %s mass gives %s signal" % (sensitivity,mass,np.round(signal,4)))

