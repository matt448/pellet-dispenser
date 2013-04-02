#!/usr/bin/python

#
# This is a test program to figure out how to read button presses
# on matrix keypad. I am using the adafruit Membrane Matrix Keypad
# Item ID: 419  (http://adafruit.com/products/419)
#
# Matthew McMillan
# matthew.mcmillan@silvercar.com
#

import pymcu           # Import the pymcu module
import time            # Import time module for sleep functions
from time import sleep

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
print 'Starting loop. Press ctrl-c to exit'
sleep(2)
print ' '

while True:
    for ipin in inputpins:
        for opin in outputpins:
            #print 'OPIN ' + str(opin) + ' GOING LOW'
            mb.pinLow(opin)
            #print 'IPIN' + str(ipin) + ' OPIN' + str(opin) + ': '+ str(mb.digitalRead(ipin))
            #print 'READING IPIN ' + str(ipin)
            if not mb.digitalRead(ipin):
                print 'IPIN:' + str(ipin) + ' OPIN:' + str(opin)
                print '--------------------'
                sleep(0.5) # Sleep a little extra to avoid double presses
                #print 'IPIN: ' + str(ipin) 
                #print 'OPIN: ' + str(opin)
                #print ' '
                #sleep(1)
            #print 'OPIN ' + str(opin) + ' GOING HIGH'
            mb.pinHigh(opin)
    time.sleep(0.05)
