from TPD.Eurotherm_Functions import *
from TPD.MassSpec_Functions import *
from TPD.Header_info import header_info, write_data
from TPD.Gui import *
from TPD.Run import runme
from queue import Queue

# TODO set length of data points to 5000 and plot the last 5000 points.
########################################################################################################################
""" User-Defined Parameters: """

"for reading a file use syntax such as: test = pd.read_csv('name1.csv', header=0, sep='\t')"
rootdir, uti1, controlObj, controlObj2, typeC, start_path = header_info()
# os.chdir(rootdir)

save_path = 'C:\\Users\\Administrator\\Dropbox (Princeton)\\IR Chamber\\Mo(100)'

project_folder = '2018_09_11'
# os.makedirs(project_folder, exist_ok=True)

experiment_name = 'TPD_Test_Buttons.csv'


# list_of_masses = [1.95734, 11.6511, 17.6364, 27.8653, 30.9313, 40, 44.06, 60.5124]  # ,4.1, 12.3, 28.12, 32.5]
list_of_masses = [] #, 17.6364, 27.8015, 31.9593, 44.06] #,4.1, 12.3, 28.12, 32.5]
# list_of_masses = [1.95734, 11.7006, 15.625, 17.6364, 27.8015, 41.038] #, 17.6364, 27.8015, 31.9593, 44.06] #,4.1, 12.3, 28.12, 32.5]
# list_of_masses = [1.95734, 17.76, 27.94] #,4.1, 12.3, 28.12, 32.5]
assert list_of_masses is not None, 'list shouldnt be None type'

number_of_masses = len(list_of_masses)
list_of_sensitivities = [2]*number_of_masses
# list_of_sensitivities = []
# list_of_sensitivities = [1]+[2]*(number_of_masses-1)

heating_rate = 4    # K/s corresponds to ~4k/s, for 10.7 it was ~5.5k/s, its about double

mV_T_table = interp_mV_to_Temp_func(start_path)

start_temp = np.round(read_temp(
                    controlObj.read_val(), typeC.emf_mVC(controlObj2.read_rt()), mV_T_table), 2)
end_temp = 360
hold_time = 15 # seconds to hold temperature when HOLD button presseed
cooldownsecs = 30

########################################################################################################################

assert len(list_of_masses) == number_of_masses, 'lengths do not match up'
assert len(list_of_sensitivities) == number_of_masses, 'lengths do not match up'
assert len(list_of_masses) == len(set(list_of_masses)), 'you have duplicate masses being monitored'
# todo add assert to make sure temp range is within available params
""" Check time to loop through masses: """
# Initial UTI looping
mean_set = loop__time(number_of_masses, list_of_masses, list_of_sensitivities)

""" Determine setpoint increment """
sendFreq = 0.06
alpha = 0
temp_set_incr = heating_rate * sendFreq  # setpoint increment assuming each loop takes "mean_set" seconds
# temp_set_incr = heating_rate * sendFreq*1.75   # setpoint increment assuming each loop takes "mean_set" seconds
temp_setpoints = np.arange(start_temp, end_temp+1, temp_set_incr)

"""setpoint frequency"""
mv_setpoints, interpd = interp_Temp_to_mV_func(temp_setpoints, controlObj2, start_path)

n = int(np.ceil(mean_set/sendFreq))
setpoint_sending = [mv_setpoints[i:i+n] for i in range(0, len(mv_setpoints),n)]

# curves, T_read_curve, T_set_curve, app, win1, win2, button = initialize_gui(number_of_masses, list_of_masses)
curves, T_read_curve, T_set_curve,  app, win1, win2, button, button_hold, button_hold_off, stop_button, hold_button, hold_off_button = initialize_gui(number_of_masses, list_of_masses, controlObj, controlObj2)

T_array = np.array([])
time_array = np.array([])

# initialize dictionary of empty arrays
mass_signals = {}
for i in list_of_masses:
    mass_signals["mass{0}".format(i)] = np.array([])

# num_freq = 1
iter_freq = 0
temp_plot_arr = np.array([])
# this needs to be the max temperature or allowed to cut short if needed, also allow for the threading
# TODO increase frequency that setpoints are sent, maybe this fixes the tracking issue at higher temperatures.
# for i in range(50):
print('len of setpoints is: '+str(len(mv_setpoints)))

# queue = Queue()
alpha_iter = 0

T_array, cum_time, start_alpha, time_array, mass_signals = runme(iter_freq, mv_setpoints, time_array,list_of_masses, list_of_sensitivities, sendFreq, alpha, alpha_iter,
          n, temp_plot_arr, T_array, mass_signals, setpoint_sending, temp_setpoints, curves, T_set_curve, T_read_curve,
          controlObj, controlObj2, uti1,app, win1, win2, button, button_hold, button_hold_off, stop_button, hold_button, hold_off_button, save_path,
          project_folder, experiment_name, hold_time)

last_setpoint(mv_setpoints, interpd, controlObj, controlObj2)
pg.QtGui.QApplication.processEvents()

controlObj.write_sp(-2.9)

cooldown(cooldownsecs, T_array, time_array, T_read_curve, controlObj, controlObj2)
pg.QtGui.QApplication.processEvents()

controlObj.close_me()
controlObj2.close_me()

os.chdir(save_path)
os.makedirs(project_folder, exist_ok=True)
write_data(project_folder, experiment_name, cum_time, T_array, mass_signals)
