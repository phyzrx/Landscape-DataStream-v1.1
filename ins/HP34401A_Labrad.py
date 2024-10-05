"""
    DMM HP34401A
    Example for python + user defined module based communications
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

class HP34401A(LandscapeInstrument):
    """
    Start Labrad and server before running
    Doesn't use built-in method in LandscapeInstrument to communicate
    Functions are written separately
    """
    Description = "DMM HP34401A Labrad"
    Version = "1.0"
    Type = "Python"
    # Default, use internal VI
    # External, use a labview .vi
    # Python, use a python file
    Address = ""
    Instrument_Address = "Not Defined" #Instrument VISA Address
    Mode = ""
    Read_Command = r""
    Read_Name = r"R_DMM (Ohm)"
    Buffer = "True"
    Read_Termination = ""

ins = None

def Call(parameters):
    result = "Called"
    return (parameters, result)

def Open():
    import labrad
    global ins
    print("Calling")
    cxn = labrad.connect()
    ins = cxn.hp34401a
    ins.select_device("phys-feynman GPIB Bus - GPIB0::22::INSTR")
    return "Opened"

def Initialize(*args):
    global ins
    result = "Initialized"
    return result

def Write():
    global ins
    result = "Write Done"
    try:
        ins.write("Read?")
    except Exception as e:
        try:
            ins.close()
        except:
            pass
        print(e)
        result = str(e)
    return result

def Read():
    global ins
    result = ""
    try:
        result = ins.read()
    except:
        pass
    return result

def Release():
    global ins
    return "Released"

def Close():
    global ins
    return "Closed"

def Exit():
    global ins
    return "Exited"

def Abort():
    global ins
    return "Aborted"

if __name__ == "__main__":
    m = HP34401A()
    Call(m.instrument_parameters())
    Initialize()
    Write()
    ans = Read()
    print(ans)
    Close()
    Exit()
