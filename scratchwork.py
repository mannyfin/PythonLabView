"""
sending should be ind. from reading

1. create mv setpoints array
2. send first setpoint and close port
3. open port, read temp and close port
4. iterate through the masses

write code here:

1. Start LabVIEW MS data collection
    a. iterates through set masses at predefined rate -- not sure the predefined rate will give best signal/noise when we vary the number of masses...unless we include that
2. Start python program to control temperature
    a. force setpoint change and mV reading to be same frequency as LabVIEW
3. Merge txt files based on matching (approximately?) time stamps in both


Lets think more procedurely about this. I'm not sure the way its outlined above will work best.
iterate through masses
read temp

We could have python just do the setpoints and have labview do all the readings?

1. Start LabVIEW Mass Spec and Temperature data collection
    a. Iterate through the masses and temperature as quickly as possible
2. Start python program to write setpoints to Eurotherm in order to achieve linear heating
3. All data is collected in LabVIEW so we don't need to merge files

The issue is that we'll get the VISA resource error because the LabVIEW and python program will want to control the Eurotherm at the same time


-Is it possible to run two separate labview programs at the same time?
-Would we get the VISA error if both programs wanted to control the Eurotherm?
    -i.e. program 1. is just linked to the python program for setting setpoings and heating rate and program 2 is just for reading masses and temp
-Can we do proper error handling so a potential VISA resource error doesnt shut down the program?
    -i.e. try...except or something? One could argue that I'm handling the same issue in python with that "checksum rtu error"

maybe make a for loop like follows?

1. start reading the masses cycle through 1-2 times
2. take the average time to cycle = total time to write setpoints
3. start the 'official' program
4. read temperature, and masses and write while reading the masses
a. assume that the time to read the temperature = 0

do read mass 2 times:
get the cycle time


for asdfa:
do read mass and write sp(cycle time) use threads
thread1.join()
thread2.join()
do read value

^ the above loop would fix the timing issue?
But why split the mass reading up in two parts if it is quick anyway
why not:
1. read temp
2. change setpoint
3. read all masses
4. repeat (or change setpoint again then repeat)

worried that there will be lag in heating rate. We should try what you're saying first and see how well it works.
Although is that what we tried as the very first thing? Didn't we try a program that called the python script just to set the setpoint?
idr i think so..
where is that text file saved?


reboot and then log into TV

LabVIEW does have error handling and we could run two programs at once but I think we would still need to force the timing somehow


"""
#
# from ctypes import *
# from sys import exit
#
# lvdll = WinDLL("Python_Call_Scan_Mass\Test_Scan_Mass\Test_Scan_Mass.dll")
# scan = lvdll.Scan_mass_IR_chamber_07142017
# print("Testing...", scan())

import struct
print (struct.calcsize("P") * 8)