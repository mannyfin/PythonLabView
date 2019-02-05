# import os
import sys
import minimalmodbus as mm
import time
# import winsound


if __name__ == '__main__':
    # input temperature ranges from Labview
    mVset = float(sys.argv[1])

    # for testing...comment these two lines out for Labview
    # mVset = -1.3


# connect to eurotherm --may not need this for the program if you are going to write to the device in LabView
port = 'COM10'
baudrate = 9600
eurotherm = mm.Instrument(port, 1)
eurotherm.serial.baudrate = baudrate
time.sleep(0.1)
# writing

eurotherm.write_register(registeraddress=2, value=mVset, numberOfDecimals=3, signed=True)
# print(eurotherm.read_register(registeraddress=2, numberOfDecimals=3, signed=True))
# winsound.Beep(2500, 50)
# eurotherm.write_register(registeraddress=2, value=interpmV[0], numberOfDecimals=3, signed=True)
# winsound.Beep(500, 500)
eurotherm.serial.close()
#print(eurotherm.serial.isOpen())
