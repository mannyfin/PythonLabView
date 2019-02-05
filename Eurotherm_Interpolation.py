import sys
import pandas as pd
import os
from thermocouples_reference import thermocouples

def interp(inputmV,mV_table, T_table):
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

if __name__ == "__main__":
    # labview_mV = float(input('input a number: '))
    # print(os.getcwd())
    typeC = thermocouples['C']
    os.chdir('C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest\\')
    df = pd.read_excel('Type C calibration_corrected.xlsx')
    labview_mV = float(sys.argv[1])
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