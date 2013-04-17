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
    mb.lcd(1, '                    ')   # Blank the display
    mb.lcd(2, '                    ')
    mb.lcd(3, '                    ')
    mb.lcd(4, '                    ')


def blanklcdline(line):
    mb.lcd(line, '                    ')   # Blank one line on the display


def waitforbutton(pin, label):
    ### Loop waits for requested button to be pressed.
    ### Returns true if requested button is pressed.
    ### Returns false if cancel button is pressed.
    print 'Press ' + str(label)
    blanklcdline(4)
    mb.lcd(4, '    Press ' + label)
    while True:
        if mb.digitalRead(pin):  # Look for requested button to be pressed
            returnval = True
            break
        elif mb.digitalRead(13):  # Also look for cancel button to be pressed
            returnval = False
            break
        else:
            time.sleep(0.05)
    return(returnval)


def read_keypad():
    keys = []
    key = ''
    maxkeys = 0
    #Set input pins to input mode
    for pin in inputpins:
        mb.digitalState(pin, 'input')
    #Set output pins to output mode
    for pin in outputpins:
        mb.digitalState(pin, 'output')
        mb.pinHigh(pin)
    while True:
        for ipin in inputpins:
            for opin in outputpins:
                mb.pinLow(opin)
                if mb.digitalRead(13):  # Red button is used here to delete entered characters
                    print 'User pressed the red button.'
                    print keys
                    if len(keys) > 0:  # Make sure there are chars to delete before trying.
                        print 'Deleting last character.'
                        popped = keys.pop()
                        print 'POPPED VAL: >' + str(popped) + '<'
                        if popped == '.':  # Check to see if char is a decimal so we can reset maxkeys
                            maxkeys = 0
                        print keys
                        dispval = ''  # Blank out display output var
                        for i in keys:  # Generate output for LCD display
                            dispval = dispval + i
                            print 'DISPVAL: >' + str(dispval) + '<'
                        blanklcdline(3)
                        mb.lcd(3, 'Enter weight: ' + str(dispval))  # Reprint the LCD after removing char
                    sleep(0.5)  # Sleep a little bit to avoid double button presses
                if not mb.digitalRead(ipin):  # This means a key was pressed
                    key = str(key_map[ipin][opin])
                    print 'KEY PRESSED: ' + str(key_map[ipin][opin])
                    if key == '#':
                        if len(keys) > 0:
                            print '# key pressed. Exiting key reading loop.'
                            break
                        else:
                            print '# key pressed but no weight values entered. Continuing.'
                            key = ''
                    elif key == '.':
                        if maxkeys == 0 and len(keys) < 3:  # This prevents multiple decimal points
                            keys.append(str(key))
                            maxkeys = len(keys) + 1
                            dispval = ''
                            for i in keys:
                                dispval = dispval + i
                            mb.lcd(3,'Enter weight: ' + str(dispval))
                        else:
                            print 'Not allowing extra decimal points.'
                            mb.lcd(4, '       ERROR')
                        print 'User entered decimal point. Only allowing one more char.'
                        print 'maxkeys: ' + str(maxkeys)
                    else:
                        if (maxkeys == 0) or (len(keys) < maxkeys) and (len(keys) < 4):
                            keys.append(str(key))
                        else:
                            print 'Not allowing any more characters'
                            mb.lcd(4, '       ERROR')
                        dispval = ""
                        for i in keys:
                            dispval = dispval + i
                        mb.lcd(3, 'Enter weight: ' + str(dispval))
                    sleep(0.5)  # Sleep a little to avoid double button presses
                    blanklcdline(4)
                mb.pinHigh(opin)
                if key == '#':
                    break
            #time.sleep(0.05) #This is the sleep between scans of the key pad
        if key == '#':
            break
    returnval = ""
    for i in keys:
        returnval = returnval + i
    returnval = Decimal(returnval)
    return returnval


def read_keypad_mainmenu():
    key = ''
    #Set input pins to input mode
    for pin in inputpins:
        mb.digitalState(pin, 'input')
        #Set output pins to output mode
    for pin in outputpins:
        mb.digitalState(pin, 'output')
        mb.pinHigh(pin)
    while True:
        for ipin in inputpins:
            for opin in outputpins:
                mb.pinLow(opin)
                if not mb.digitalRead(ipin):  # This means a key was pressed
                    key = str(key_map[ipin][opin])
                    print 'KEY PRESSED: ' + str(key_map[ipin][opin])
                    if key == '1':
                        returnval = 1
                        sleep(0.5)  # Sleep a little bit to avoid double button presses
                        break
                    elif key == '2':
                        returnval = 2
                        sleep(0.5)  # Sleep a little bit to avoid double button presses
                        break
                    elif key == '3':
                        returnval = 3
                        sleep(0.5)  # Sleep a little bit to avoid double button presses
                        break
                    else:
                        print 'Invaild option ' + str(key)
                        sleep(0.5)  # Sleep a little bit to avoid double button presses
                mb.pinHigh(opin)
        if key == '1' or key == '2' or key == '3':
            break
    return returnval


def inputweight():
    ### Read in weight value.
    ### For now this can read in from keyboard.
    blanklcdline(3)
    mb.lcd(3, 'Enter weight: ')
    readval = raw_input('Enter weight: ')
    weight = Decimal(readval).quantize(oneplace)
    return weight


def find_scale_device():
    # Loops until scale device file is found.
    # Once found function returns the path to the scale device file.
    while True:
        output = subprocess.check_output(["find", "/dev/usb/", "-name", "hiddev*", "-user", "pi"])
        if output == '':
            mb.lcd(2, ' *SCALE NOT FOUND* ')
            mb.lcd(3, 'Connect and power on')
            mb.lcd(4, ' scale to continue')
            sleep(1)
        else:
            blanklcdline(2)
            blanklcdline(3)
            blanklcdline(4)
            mb.lcd(3, '    FOUND SCALE   ')
            sleep(1)
            break
    return output.strip()


def read_scale(devicefile):
    output = check_output(["/usr/local/bin/readscale", devicefile])
    output = Decimal(output.strip())
    output = Decimal(output) / Decimal(10)
    output = Decimal(output).quantize(oneplace)
    return output


def solenoid_control(action, pin):
    print 'solenoid_control - pin: ' + str(pin) + ' action: ' + str(action)
    if action == 'deactivate': mb.pinLow(pin)
    elif action == 'activate': mb.pinHigh(pin)
    else: mb.pinLow(pin)  # Not sure what you want but closing to prevent spill


def wait_for_zero_scale():
    #Checks the scale to see if it is at zero and loops until it is zero.
    #Returns true if the scale was zero on the first check.
    #Returns false if the scale was not zero on the first check.
    returnval = True
    while True:
        scaleweight = read_scale(scaledev)
        if scaleweight == Decimal(0.0):  # If scale is zero break to continue.
            break
        else:
            returnval = False
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
    sleep(0.5)
    return(returnval)


def fill_bucket():
    ### Read in weight value.
    #stopweight = inputweight()
    blanklcdline(2)
    blanklcdline(3)
    blanklcdline(4)
    mb.lcd(3, 'Enter weight: ')
    stopweight = read_keypad()

    #Loop at current weight until cancel button is pressed.
    while True:
        mb.pinLow(1)  # Turn off status LED
        cancel = False
        #Wait for start button
        if waitforbutton(12, 'START'):
            if not wait_for_zero_scale():
                #If scale wasn't zero when we checked then ask for start button again.
                waitforbutton(12, 'START')
            scaleweight = read_scale(scaledev)

            print "SCALE WEIGHT: " + str(scaleweight)
            print " STOP WEIGHT: " + str(stopweight)

            blanklcdline(2)
            blanklcdline(3)
            blanklcdline(4)

            solenoid_control('activate', 11)
            while Decimal(scaleweight) < (Decimal(stopweight) - Decimal(0.2)):
                if mb.digitalRead(13):
                    #This aborts the current fill loop
                    print "User pressed cancel button"
                    mb.lcd(4, ' STOP: *Cancelled*')
                    cancel = True
                    break
                scaleweight = read_scale(scaledev)
                print "SCALE WEIGHT: " + str(scaleweight)
                print " STOP WEIGHT: " + str(stopweight)
                mb.lcd(2, '   -- FILLING --   ')
                mb.lcd(3, 'SCALE: ' + str(scaleweight) + 'oz')
                mb.lcd(4, ' STOP: ' + str(stopweight) + 'oz')
            solenoid_control('deactivate', 11)
            mb.lcd(2, '   --  FULL  --   ')
            sleep(0.5)
            scaleweight = read_scale(scaledev)
            mb.lcd(3, 'SCALE: ' + str(scaleweight) + 'oz')

            #This is the fine adjustment loop. It waits for the scale to
            #stablize and adds weight in 0.1oz increments if needed.
            if not cancel:
                #Check to see if we hit the target. If not give
                #the scale a few seconds to stabilize.
                while Decimal(scaleweight) < Decimal(stopweight):
                    mb.lcd(2, '   --  UNDER  --   ')
                    mb.pinLow(1)  # Turn off status LED
                    i = 0
                    while i <= 10:
                        i += 1
                        scaleweight = read_scale(scaledev)
                        mb.lcd(3, 'SCALE: ' + str(scaleweight) + 'oz')
                        mb.pinToggle(1)  # Flash status LED while doing final weight adjustment
                        if Decimal(scaleweight) >= Decimal(stopweight):
                            mb.lcd(2, '   --  FULL  --   ')
                            break
                        sleep(0.25)
                    if Decimal(scaleweight) >= Decimal(stopweight):
                        mb.lcd(2, '   --  FULL  --   ')
                        break
                    elif Decimal(scaleweight) < Decimal(stopweight):
                    # Quickly open door to add more pellets. 0.1 seconds dumps about 0.1 oz
                        mb.pinHigh(11)
                        sleep(0.1)
                        mb.pinLow(11)

            mb.pinHigh(1)  # Turn on status LED to signal finished

            if Decimal(scaleweight) == Decimal(stopweight):
                mb.lcd(2, '   --  FULL  --   ')
            elif Decimal(scaleweight) > Decimal(stopweight):
                mb.lcd(2, '   --  OVER  --   ')
            elif Decimal(scaleweight) < Decimal(stopweight):
                mb.lcd(2, '   --  UNDER  --   ')
        else:  # If cancel button pressed instead of start
            break


def shutdown():
    # This function is used to confirm system shutdown
    returnval = ''
    blanklcdline(2)
    blanklcdline(3)
    blanklcdline(4)
    mb.lcd(2, 'Shutdown?')
    mb.lcd(3, 'YES: Green button')
    mb.lcd(4, ' NO: Red button')
    while True:
        # Wait for a red or green button to be pressed
        if mb.digitalRead(13):
            print 'User pressed the red button. Not shutting down'
            returnval = False
            break
        elif mb.digitalRead(12):
            print 'User pressed the green button. Going ahead with shutdown'
            returnval = True
            break
    return returnval


# Initialize the pymcu board, LCD and digital pins for buttons
mb = pymcu.mcuModule()  # Initialize pymcu board - Find first available pymcu hardware module.
mb.digitalState(12, 'input')  # Set digital pins to input mode for reading button presses
mb.digitalState(13, 'input')  # Set digital pins to input mode for reading button presses
mb.lcd()               # Initialize the LCD
mb.pinLow(1)           # Make sure LED's are turned off
mb.pinLow(2)
time.sleep(0.5)        # Wait for LCD to Initialize

#Variables
cancel = False
oneplace = Decimal('0.0')  # Decimal precision for weights
scaleweight = Decimal('0.0')
stopweight = Decimal('0.0')
inputpins = [6, 7, 8, 9]
outputpins = [3, 4, 5]
allpins = outputpins + inputpins

# Map the input and output pins to the buttons on the keypad.
key_map = {9: {5: 1, 4: 2, 3: 3},  8: {5: 4, 4: 5, 3: 6},  7: {5: 7, 4: 8, 3: 9},  6: {5: ".", 4: 0, 3: "#"}}

# Display start up text
blanklcd()
time.sleep(0.07)
mb.lcd(1, '  Pellet Dispenser  ')
mb.lcd(3, '   Starting....       ')
time.sleep(1)

# Find the scale
scaledev = find_scale_device()
print 'Scale device file: >' + scaledev + '<'

# First read of scale returns 0.1oz for some reason
# Adding an extra first read to account for that
scaleweight = read_scale(scaledev)

wait_for_zero_scale()

# Do initial read of scale
scaleweight = read_scale(scaledev)
print 'Scale weight: ' + str(scaleweight) + 'oz'

# Main menu
while True:
    blanklcdline(2)
    blanklcdline(3)
    blanklcdline(4)

    mb.lcd(2, '1. Enter weight    ')
    mb.lcd(3, '2. Calculate weight')
    mb.lcd(4, '3. Shutdown        ')

    menuoption = read_keypad_mainmenu()

    if menuoption == 1:
        fill_bucket()
    elif menuoption == 2:
        print 'Menu option 2 pressed'
        print 'Need to add calc function'
    elif menuoption == 3:
        #This will shutdown the system
        print 'Menu option 3 pressed'
        if shutdown():
            blanklcdline(2)
            blanklcdline(3)
            blanklcdline(4)
            mb.lcd(3, ' -- SHUTTING DOWN -- ')
            mb.close()  # Close out pymcu board
            print 'Add linux shutdown command here'
            break
