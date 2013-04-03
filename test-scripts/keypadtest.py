#!/usr/bin/python

#
# This is a test program to figure out how to read button presses
# on matrix keypad. I am using the adafruit Membrane Matrix Keypad
# Item ID: 419  (http://adafruit.com/products/419)
#
# Matthew McMillan
# matthew.mcmillan@silvercar.com
#
# Thanks to Adam Levy for helping me with the key_pad nested dictionary
# 
#

import pymcu           # Import the pymcu module
import time            # Import time module for sleep functions
from time import sleep

key_map = {   9:{ 5:1, 4:2, 3:3 },  8:{ 5:4, 4:5, 3:6 },  7:{ 5:7, 4:8, 3:9 },  6:{ 5:"*", 4:0, 3:"#" }   }

inputpins = [6,7,8,9]
outputpins = [3,4,5]

allpins = [3,4,5,6,7,8,9]

mb = pymcu.mcuModule() # Initialize pymcu board - Find first available pymcu hardware module.

for pin in inputpins:
    print ' IN PIN NUM: ' + str(pin)
    mb.digitalState(pin, 'input') #Set digital pins to input mode for reading button presses

for pin in outputpins:
    print 'OUT PIN NUM: ' + str(pin)
    mb.digitalState(pin, 'output') #Set digital pins to input mode for reading button presses
    mb.pinHigh(pin)

print ' '
print 'Starting loop to read keypad button presses.'
print 'Press ctrl-c to exit'
sleep(2)
print 'Press buttons now. '

while True:
    for ipin in inputpins:
        for opin in outputpins:
            mb.pinLow(opin)
            if not mb.digitalRead(ipin):
                #print 'IPIN:' + str(ipin) + ' OPIN:' + str(opin)
                print 'KEY PRESSED: ' + str(key_map[ipin][opin])
                print '--------------------'
                sleep(0.5) # Sleep a little extra to avoid double presses
            mb.pinHigh(opin)
    time.sleep(0.05)
