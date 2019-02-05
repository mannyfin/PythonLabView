from ctypes import *
import numpy as np
import numpy.ctypeslib
import os

rootdir = 'C:\\Users\\Administrator\\Desktop\\TESTTPD-2012OLD - Copy'
dlldir = 'C:\\Users\\Administrator\\Desktop\\builds\\array\\array_test'
dll = 'array_test.dll'
os.chdir(dlldir)

loadlib = cdll.LoadLibrary(dll)


# arr = np.array([1,2,3,4,5])
# length = len(arr)
#
# LP_c_int32_5 = POINTER(c_int32*5)
# my_pointer1 = LP_c_int32_5()
#
# Array2 = (c_int32 * length).in_dll(loadlib, "Array_tmp")
#
# c_arr = np.ctypeslib.as_ctypes(arr)
# clen = c_int32(length)
# p_clen = pointer(clen)
# c_arr_ptr = pointer(c_arr)
# c_arr_ptr = cast(c_arr, pointer(c_int32))

pyarr = np.array([1, 2.4, 3, 4, 5.5,6,7,8])
length = len(pyarr)
clength = c_int32(length)
# arr1 = (c_int32 * length)(*pyarr)
# arr2 = (c_int32 * length)()

arr1 = (c_double * length)(*pyarr)
arr2 = (c_double * length)()
# INTP = POINTER(c_int32)
# addr_len = addressof(clength)
# addr_arr1 = addressof(arr1)
# addr_arr2 = addressof(arr2)
# ptr_len = cast(addr_len, INTP)
# ptr_arr1 = cast(addr_arr1, INTP)
# ptr_arr2 = cast(addr_arr2, INTP)


# loadlib.Array_tmp.argtypes = [c_int32 *length, c_int32, c_int32*length]
# loadlib.Array_tmp.argtypes = [pointer((c_int32 * length)), pointer(clength), pointer((c_int32 * length))]

loadlib.Array_tmp.argtypes = [type(pointer(arr1)), type(pointer(clength)), type(pointer(arr2))]

# loadlib.Array_tmp.argtypes = [type(my_pointer1), type(p_clen)]
# loadlib.Array_tmp.argtypes = [type(c_arr_ptr), type(p_clen)]
# loadlib.Array_tmp.argtypes = [c_arr._type_, c_int32]
# loadlib.Array_tmp.argtypes = [pointer(c_double*length), pointer(c_int32)]
# loadlib.Array_tmp.restype = type(c_arr)
# loadlib.Array_tmp.restype = c_arr._type_
# loadlib.Array_tmp.restype = type(arr2)
# loadlib.Array_tmp.restype = type(my_pointer1)
# loadlib.Array_tmp.restype = c_voidp
# asdf = loadlib.Array_tmp(c_arr_ptr, cast(5, POINTER(c_int32)))

loadlib.Array_tmp(byref(arr1), byref(clength), byref(arr2))
# g = loadlib.Array_tmp(arr1, clength, arr2)
# g = loadlib.Array_tmp(ptr_arr1, ptr_len, ptr_arr2)
# g = loadlib.Array_tmp(Array2, clen)
# g = loadlib.Array_tmp(c_arr, clen)
# g = loadlib.Array_tmp(c_arr_ptr, pointer(c_int32(5))
#
#
arr2 = np.ctypeslib.as_array(arr2)
print(arr2)
# print(g)
# print(ptr_arr2)
# np_arr_g = np.ctypeslib.as_array(ptr_arr2)
# print(np_arr_g)
# h = cast(g, POINTER(c_double*5))
# as_np_array = np.frombuffer(h, np.float32)
#
# print(np.ctypeslib.as_array(as_np_array))