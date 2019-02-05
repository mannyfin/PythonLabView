# from Main import number_of_masses, list_of_masses, list_of_sensitivities
import os
from ctypes import *
import numpy as np
import time

# we can also pass no_of_loops as a parameter in the future


class UTI_QMS:
    def __init__(self, path='C:\\Users\\Administrator\\Desktop\\builds\\scanmass_single\\scan_multiple_masses',
                 dll='scan_multiple_masses.dll'):
        self.path = path
        self.dll = dll
        os.chdir(self.path)
        self.LabVIEWQMS = cdll.LoadLibrary(self.dll)

    def read_mass(self, number_of_masses, sensitivity, mass):
        """
        void Read_Multiple_Mass_Spec(int32_t *NumberOfMasses, int32_t Sensitivity[], double Mass[], double Data[])
        :param number_of_masses: int
        :param sensitivity: arr1
        :param mass: arr2
        :return: Data, array 3
        """
        assert number_of_masses == len(mass), 'number of masses should equal len(mass)'
        assert number_of_masses == len(sensitivity), 'number of masses should equal len(sensitivity)'
        assert len(mass) == len(sensitivity), 'lengths of mass and sensitivity arrays are not the same'

        clength = c_int32(number_of_masses)
        arr1 = (c_int32*number_of_masses)(*sensitivity)
        arr2 = (c_double*number_of_masses)(*mass)
        arr3 = (c_double * number_of_masses)()

        self.LabVIEWQMS.Read_Multiple_Mass_Spec.argtype = [type(pointer(clength)),type(pointer(arr1)),
                                                           type(pointer(arr2)), type(pointer(arr3))]

        self.LabVIEWQMS.Read_Multiple_Mass_Spec(byref(clength), byref(arr1), byref(arr2), byref(arr3))
        arr3 = np.ctypeslib.as_array(arr3)

        return arr3

    def read_mass_out(self, number_of_masses, mass):
        """
        void Return_Mass_Input(int32_t NumberOfMasses, double Mass[], double MassOut[])
        :param number_of_masses:
        :param mass:
        :return:
        """
        assert number_of_masses == len(mass), 'number of masses should equal len(mass)'
        clength = c_int32(number_of_masses)
        arr1 = (c_double*number_of_masses)(*mass)
        arr2 = (c_double * number_of_masses)()

        self.LabVIEWQMS.Return_Mass_Input.argtype = [type(pointer(clength)),type(pointer(arr1)), type(pointer(arr2))]
        self.LabVIEWQMS.Return_Mass_Input(byref(clength), byref(arr1), byref(arr2))
        arr2 = np.ctypeslib.as_array(arr2)

        return arr2

    def read_sens_out(self, number_of_masses, sensitivity):
        """
        void Return_Sensitivity_Input(int32_t *NumberOfMasses, int32_t Sensitivity[], int32_t SensitivityOut[])
        :param number_of_masses:
        :param sensitivity:
        :return:
        """
        assert number_of_masses == len(sensitivity), 'number of masses should equal len(sensitivity)'

        clength = c_int32(number_of_masses)
        arr1 = (c_int32*number_of_masses)(*sensitivity)
        arr2 = (c_int32 * number_of_masses)()

        self.LabVIEWQMS.Return_Sensitivity_Input.argtype = [type(pointer(clength)),type(pointer(arr1)), type(pointer(arr2))]
        self.LabVIEWQMS.Return_Sensitivity_Input(byref(clength), byref(arr1), byref(arr2))

        arr2 = np.ctypeslib.as_array(arr2)

        return arr2

    def __enter__(self):
        return self

    def __exit__(self, __type__, value, traceback):
        pass


def loop__time(number_of_masses, masses, sensitivities):
    """ Create UTI instance m
    mean_single is the average loop time for a single mass
    mean_set is the average loop time for the set of masses
    """

    # uti1 = UTI_QMS()
    """ Check time to loop through masses: """
    no_of_loops = 10
    set_read_times = []
    for i in range(no_of_loops):
        start_set = time.time()
        with UTI_QMS() as uti2:
            signals = uti2.read_mass(number_of_masses, sensitivities, masses)
        end_set = time.time() - start_set
        # print('signals: \n' + str(signals))
        set_read_times.append(end_set)

    """ This should be the time taken each loop to write setpoints """
    mean_set = np.mean(set_read_times[1:])
    print("Average set read time is:   {0}".format(np.round(mean_set, 4)))

    return mean_set

"""
int32_t NumberOfMasses, int32_t Sensitivity[], double Mass[], double Data[], double MassOut[], int32_t SensitivityOut[]
"""
if __name__ == "__main__":

    masses = np.array([18.3, 28.2, 44.2, 60, 2.1, 31.1, 15, 12])
    sensitivities = np.array([3, 3, 4, 5, 3, 3, 2, 4])

    loop__time(len(masses), masses, sensitivities)


    # with UTI_QMS() as uti1:
    #     senses_out = uti1.read_sens_out(len(masses), sensitivities)
    #     print('sens: \n' + str(senses_out))
    #
    # with UTI_QMS() as uti2:
    #     signals = uti2.read_mass(3, sensitivities, masses)
    #     print('signals: \n' + str(signals))
    #
    # with UTI_QMS() as uti3:
    #     masses_out = uti3.read_mass_out(3, masses)
    #     print('Masses: \n' + str(masses_out))






