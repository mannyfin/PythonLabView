from TPD.Eurotherm_Functions import *
from TPD.MassSpec_Functions import *
import matplotlib.pyplot as plt


def header_info():
    """
    Feel free to adjust paths as necessary
    :return:
    """
    rootdir = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest'
    # dlldir = 'C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_single_mass'
    start_path = 'C:\\Users\\Administrator\\Desktop\\PythonProjects\\LabViewtest\\'
    dlldir2 = 'C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_multiple_masses750'
    dll2 = 'scan_multiple_masses750.dll'
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

    return rootdir, uti1, controlObj, controlObj2, typeC, start_path


def write_data(project_folder,experiment_name, cum_time, T_array, mass_signals):
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
    print('mean heating rate: ' + str(gradT.loc[25:].mean()))
    # plt.show()

    print('hi')
    return plt.show()
