from send_multiple_setpoints import Eurotherm, read_temp
import pickle
import numpy as np
from thermocouples_reference import thermocouples
import os
"""
pickle interpolation table function?
this way, we dont need to read the table every time
"""
rootdir = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest'
os.chdir(rootdir)


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