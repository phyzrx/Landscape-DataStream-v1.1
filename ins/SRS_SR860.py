"""
    SRS SR860 Lock-in amplifier
    Example for use internal communication core
"""
# To import from outside \lib
import sys
import os.path
path = sys.path[0]
path = os.path.dirname(path)
sys.path.append(path + r"\lib")

import pyvisa
import LandscapeUtilities as ut
from time import sleep
from LandscapeInstrument import LandscapeInstrument
from LandscapeInstrument import InitializeDecorator
from LandscapeDataset import LandscapeDataset

class SR860(LandscapeInstrument):
    """
    Start Labrad and server before running
    Doesn't use built-in method in LandscapeInstrument to communicate
    Functions are written separately
    """
    Description = "SRS SR860"
    Version = "1.0"
    Type = "Default"
    # Default, use internal VI
    # External, use a labview .vi
    # Python, use a python file
    Address = ""
    Instrument_Address = "Not Defined" #Instrument VISA Address
    Scan_Name = "V_ac_set (V)"
    Retrieve_Command = "SLVL?"
    Scan_Command = r"SLVL %.3e"
    Read_Command = r"SNAP? 0,1,3"
    Read_Name = r"V_x\V_y\Phase"
    Buffer = "True"