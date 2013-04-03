#!/usr/bin/python

import pymcu           # Import the pymcu module
import time            # Import time module for sleep functions
from time import sleep
import os
import subprocess
from decimal import Decimal
from subprocess import check_output

# Functions

def blanklcd():
    mb.lcd(1,'                    ')   # Blank the display
    mb.lcd(2,'                    ')
    mb.lcd(3,'                    ')
    mb.lcd(4,'                    ')
 
def blanklcdline(line):
    mb.lcd(line,'                    ')   #Blank one line on the display
        
#def readscale(val):
    # This is a fake scale reading that keeps increasing in 0.1 ounce increments
    #val += Decimal('0.1')
    #return val

def waitforbutton(pin,label):
    ### Loop waits for start button to be pressed.
    print 'Press ' + str(label)
    mb.lcd(3,'    Press ' + label)
    while True:
        if not mb.digitalRead(pin):
            time.sleep(0.05)
        else:
            break

def inputweight():
    ### Read in weight value.
    ### For now this can read in from keyboard.
    blanklcdline(3)
    mb.lcd(3,'Enter weight: ')
    readval = raw_input('Enter weight: ')
    weight = Decimal(readval).quantize(oneplace)
    return weight

def find_scale_device():
    # Loops until scale device file is found.
    # Once found function returns the path to the scale device file.
    while True:
        output = subprocess.check_output(["find", "/dev/usb/", "-name", "hiddev*", "-user", "pi"])
        if output == '':
            mb.lcd(2,' *SCALE NOT FOUND* ')
            mb.lcd(3,'Connect and power on')
            mb.lcd(4,' scale to continue')
            sleep(1)
        else:
            blanklcdline(2)
            blanklcdline(3)
            blanklcdline(4)
            mb.lcd(3,'    FOUND SCALE   ')
            sleep(1)
            break
    return output.strip()

def read_scale(devicefile):
    output = check_output(["/usr/local/bin/readscale", devicefile])
    output = Decimal(output.strip())
    output = Decimal(output) / Decimal(10)
    output = Decimal(output).quantize(oneplace)
    return output

def solenoid_control(action,pin):
    print 'solenoid_control - pin: ' + str(pin) + ' action: ' + str(action)
    if action == 'deactivate': mb.pinLow(pin)
    elif action == 'activate': mb.pinHigh(pin)
    else: mb.pinLow(pin) #Not sure what you want but closing to prevent spill 

def wait_for_zero_scale():
    while True:
        scaleweight = read_scale(scaledev)
        if scaleweight == Decimal(0.0):
            break
        else:
            blanklcdline(2)
            blanklcdline(3)
            blanklcdline(4)
            mb.lcd(2,' Scale not at 0.0oz ')
            mb.lcd(3,'Take item from scale')
            mb.lcd(4,'or press TARE button')
            sleep(1)
    #Scale is now zero. Printing msg to LCD.
    blanklcdline(2)
    blanklcdline(3)
    blanklcdline(4)
    mb.lcd(3,'    SCALE READY  ')
    sleep(2)
    return


#Initialize the pymcu board, LCD and digital pins for buttons
mb = pymcu.mcuModule() # Initialize pymcu board - Find first available pymcu hardware module.
mb.digitalState(12, 'input') #Set digital pins to input mode for reading button presses
mb.lcd()               # Initialize the LCD
mb.pinLow(1)           # Make sure LED's are turned off
mb.pinLow(2)
time.sleep(0.5)          # Wait for LCD to Initialize

#Variables
oneplace = Decimal('0.0') #Decimal precision for weights
scaleweight = Decimal('0.0')
stopweight = Decimal('0.0')

#Display start up screen
blanklcd()
time.sleep(0.07)
mb.lcd(1,'  Pellet Dispenser  ')
mb.lcd(3,'   Starting....       ')
time.sleep(1)

#Find the scale
scaledev = find_scale_device()
print 'Scale device file: >' + scaledev + '<'

# First read of scale returns 0.1oz for some reason
# Adding an extra first read to account for that
scaleweight = read_scale(scaledev)


wait_for_zero_scale()

# Do initial read of scale
scaleweight = read_scale(scaledev)
print 'Scale weight: ' + str(scaleweight) + 'oz'


### Read in weight value.
stopweight = inputweight()

#Wait for start button
waitforbutton(12,'START')

print "SCALE WEIGHT: " + str(scaleweight)
print " STOP WEIGHT: " + str(stopweight)

blanklcdline(2)
blanklcdline(3)
blanklcdline(4)

solenoid_control('activate',11)
while Decimal(scaleweight) < Decimal(stopweight):
    scaleweight = read_scale(scaledev)
    print "SCALE WEIGHT: " + str(scaleweight)
    print " STOP WEIGHT: " + str(stopweight)
    mb.lcd(2,'   -- FILLING --   ')
    mb.lcd(3,'SCALE: ' + str(scaleweight) + 'oz')
    mb.lcd(4,' STOP: ' + str(stopweight) + 'oz')
    time.sleep(0.25)
solenoid_control('deactivate',11)
mb.pinHigh(1) #Turn on LED light to signal finished
mb.lcd(2,'   --  FULL   --   ')



mb.close() # Close out pymcu board
