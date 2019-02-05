from ctypes import *
import numpy as np
import numpy.ctypeslib
import os

# dlldir should be directory in which the shared library is stored
dlldir = 'C:\\Users\\Administrator\\Desktop\\builds\\array\\array_test'
dll = 'array_test.dll' # Shared library that contains one LabVIEW
os.chdir(dlldir)

loadlib = cdll.LoadLibrary(dll)


pyarr = np.array([1, 2.4, 3, 4, 5.5,6,7,8])
length = len(pyarr)
clength = c_int32(length)

arr1 = (c_double * length)(*pyarr)
arr2 = (c_double * length)()

loadlib.Array_tmp.argtypes = [type(pointer(arr1)), type(pointer(clength)), type(pointer(arr2))]

loadlib.Array_tmp(byref(arr1), byref(clength), byref(arr2))

arr2 = np.ctypeslib.as_array(arr2)
print(arr2)
