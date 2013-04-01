pellet-dispenser
================

This is a project I'm helping my son with. His school has a yearly event called Ace Innovation where students come up with some sort of invention. His idea is an automatic plastic pellet dispensing machine to help his mom with her weighted blanket business. This machine will speed up the weighing of plastic pellets that are used in the weighted blankets.


The initial version of the dispenser runs on a Raspberry Pi and uses a pyMCU microcontroller for I/O. The scale we are using is a Dymo M10 connected over USB. Everything is written in Python with the exception of the code that communicates with the scale which that is written in C. I had tremendous amounts of problems trying to talk to the scale with Python and the PyUSB library. 
