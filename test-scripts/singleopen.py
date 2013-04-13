#!/usr/bin/python


import pymcu
from time import sleep
mb =pymcu.mcuModule()
i = 0

while i < 2:
    i = i + 1
    mb.pinToggle(11)
    sleep(0.1)

