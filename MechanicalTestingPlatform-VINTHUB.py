# Open Mechanical Testing Platform (MTP)
# Amir J Bidhendi, Email: amir.bidhendi@mcgill.ca
# The latest version can be found under: https://github.com/Bidhendi/MTP


# The script below, tested under Python 2.7.1, was used to read "FORCE-DISPLACEMENT" sensor signals 
# from a VINT HUB (ID: HUB000_0, Phidgets) connected to a load cell and an LVDT. 
# The setup was used to demonstrate a simple and versatile mechanical testing platform to perform 
# tensile test. For more information refer to:

# 	"Assembly of a Simple Scalable Device for Micromechanical Testing of Plant Tissues"
# 		Amir J. Bidhendi , M. Shafayet Zamil , Anja Geitmann, Methods in Cell Biology, 2020.
#		https://doi.org/10.1016/bs.mcb.2020.04.003
#   If you found this code useful, please consider citing us with the main publication.
 
# Parts of this script was provided by www.phidgets.com forums. The script generates ex1.csv file 
# with two columns containing LVDT and load cell signal data, and plots these in real time as well. 
# Before running the tests, the calibration constants are to be determined and input in pertinent lines below.
#
import sys
import time
from Phidget22.Devices.VoltageRatioInput import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
import matplotlib.pyplot as plt
import os
from os import linesep
from termcolor import colored
import os.path
from Tkinter import *
import tkMessageBox 
from drawnow import *
#----------------------USER INPUT SECTION
S=175594    # Example slope of the line from load cell calibration
CS=12.875    # Example constant from the line from load cell calibration
#----------------------USER INPUT SECTION
L=43.909    # Example slope of the line from LVDT calibration
CL=- 8.9142    # Example Constant from the line from LVDT calibration
################################
# Checking if the file already exsists in the directory
if os.path.isfile("ex1.csv"):
    Root=Tk()
    Root.wm_attributes("-topmost", 1)
    tkMessageBox.showinfo('Tensile tester v2.1: Overwrite error', \
                          ' Remove old CSV file and try again!')
    sys.exit()
################################
# Plotting
plt.ion()
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
plt.ylabel('force (g)')
plt.xlabel('Disp.(um)')  
def plotUpdate() : # a function to plot live data
#    plt.xlim(3)  # limit for X axis so that it does not scale itself
#    plt.ylim(50) # limit for Y axis so that it does not update itself`
    plt.title("Streaming Force-Displacement data")
    plt.ylabel("Force")
    plt.xlabel("Disp.")
    plt.grid(True)
    plt.plot(Y,X,'ro-')
################################
# Defining functions to read voltageratios
try:
    ch = VoltageRatioInput()
    ch2 = VoltageRatioInput()
except RuntimeError as e:
    print("Runtime Exception %s" % e.details)
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    exit(1)
a=-CL/L # To report F and D as zero in the first loop
b=-CS/S
# Setting a and b global variables so that they can be used in other sections.
def VoltageRatioChangeHandlerA(e, voltageRatio):
        global a
        a = voltageRatio
#
def VoltageRatioChangeHandlerB(e, voltageRatio):
        global b
        b = voltageRatio
#
start = time.time()
# Bridge (DAQ1500) is enabled by default so no need to enable it.
# Some functions are Boolean. 1 means enabled. Unit of time is ms.
ch.setOnVoltageRatioChangeHandler(VoltageRatioChangeHandlerA)
ch.setHubPort(1)
ch.setIsHubPortDevice(1)
ch.openWaitForAttachment(5000)
ch.setDataInterval(500) #minimum 1
#
ch2.setOnVoltageRatioChangeHandler(VoltageRatioChangeHandlerB)
ch2.setHubPort(0)
ch2.setChannel(0)
ch2.openWaitForAttachment(5000)
ch2.setDataInterval(500) # minimum 20
################################
X=[]
Y=[]
################################
while 1:
    F= b*S+CS  # Force # "b" is signal from load cell
    D= a*L+CL #Displacement or position. "a" comes from lvdt  
    # in this example, mechanical zero and stage zero coincide. Equation for D
    # may need to be modified.
    if D!=25:
            try:
                # Printing outputs in Console 
                print("Force: {0}   Disp: {1}".format(F,D))
                # To see the signal values, F and D in line above can be 
                # replaced by b and a, respectively and reverted to check 
                # the final Disp. and Force after calibration.
                with open('ex1.csv', 'ab') as f:
                    f.write(str(D)+","+str(F)+os.linesep)
                    X.append(F)
                    Y.append(D)
                    drawnow(plotUpdate)
                    plt.pause(0.01)
                time.sleep(0.5)
################################
            except (KeyboardInterrupt):
                end = time.time()
                seconds=end-start
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                print 
                print "Duration = " "%d:%02d:%02d" % (h, m, s)
                print colored("Process terminated by user","blue", attrs= \
                              ['bold','blink'])
                ch.close()       
                ch2.close()
                sys.exit()
    else:
        pass    