#!/usr/bin/python

# Author: Mason McMillan

import pymcu
from time import sleep
mb =pymcu.mcuModule()
i = 0

mb.pinLow(11)

while i < 20:
    i = i + 1
    mb.pinToggle(11)
    sleep(1)

