"""
    Keithley 2450 Source Meter
    Example for python + pyvisa based communications
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

class Keithley2450(LandscapeInstrument):
    Description = "Keithley 2450 source meter"
    Version = "1.0"
    Type = "Python"
    # Default, use internal VI
    # External, use a labview .vi
    # Python, use a python file
    Address = ""
    Instrument_Address = "Not Defined" #Instrument VISA Address
    Mode = "Source Voltage - Measure Current"
    Scan_Name = "V_2450_set (V)"
    Retrieve_Command = ":SOUR:VOLT:LEV:IMM:AMPL?"
    Scan_Command = ":SOUR:VOLT:LEV:IMM:AMPL {:.5g}"
    Ramp_Step = "0.01" # in V
    Ramp_Delay = "0.1" # in second
    Scan_Limit = r"-10V\+10V"
    Scan_Stablize = "False"
    Scan_Stablize_Timeout = "0s"
    External_VI_Behavior = "Mini"
    Read_Command = r":MEAS:VOLT:DC?\:MEAS:CURR:DC?"
    Read_Name = r"V_2450_read (V)\I_2450_read (A)"
    Buffer = "True"
    Read_Termination = ""
    Previous_Value = 0

    @InitializeDecorator
    def initialize(self):
        if self.Mode == "Source Voltage - Measure Current":
            self.raw_clear()
            self.raw_write(":SENS:FUNC \"CURR\"")
            self.raw_write(":SENS:CURR:UNIT AMP")
            self.raw_write(":SENS:CURR:NPLC 1")
            self.raw_write(":SENS:CURR:RANG 1E-6")
            self.raw_write("TRAC:CLE \"defbuffer1\"")
        else:
            pass
        return self

ins = None # Instrument Class

def Identify(*arg):
    global ins
    return ins.identify(*arg)

def Call(parameters):
    if not ins == None:
        _ins = ins._ins
    else:
        _ins = None
    global ins
    ins = Keithley2450()
    ins._ins = _ins
    print("Calling")
    result = "Called"
    ins.setup(parameters)
    ins_parameters = ins.instrument_parameters()
    ins.call()
    return (ins_parameters, result)

def Open(*args):
    global ins
    print("Openning")
    result = "Opened"
    ins.open_resource()
    return result

def Initialize(*args):
    global ins
    result = "Initialized"
    ins.initialize()
    return result

def Retrieve(*arg):
    global ins
    result = "Retrieved"
    ins.retrieve()
    return result

def Scan(sv):
    global ins
    result = "Scanned"
    rb = False
    rt = 0
    ins.scan(sv)
    # rb = not ins.approach(sv)
    # rt = 600
    return (result, rb, rt)

def Approach(sv):
    global ins
    result = "Approached"
    rb = False
    rt = 0
    rb = ins.approach(sv)
    rt = 600
    return (result, rb, rt)

def Write():
    global ins
    result = "Write Done"
    ins.write()
    return result

def Read():
    global ins
    result = ""
    result = ins.read()
    return result

def Start_Monitor():
    global ins
    ins.call()
    ins.start_monitor()
    return "Start Monitor"

def Stop_Monitor():
    global ins
    ins.stop_monitor()
    return "Stop Monitor"

def Log():
    global ins
    return (ins.Read_Name, ins.log())

def Release():
    global ins
    ins.release_resource()
    return "Released"

def Close():
    global ins
    ins.close()
    return "Closed"

def Exit():
    global ins
    ins.exit()
    ins = None
    return "Exited"

def Abort():
    global ins
    ins.abort()
    return "Aborted"

if __name__ == "__main__":
    print(Identify("K2450-1"))
    Call([("Instrument Address", r"TCPIP0::192.168.1.101::inst0::INSTR")])
    Open()
    Initialize()
    Retrieve()
    Start_Monitor()
    while True:
        try:
            (result, rb, rt) = Approach(0)
            Write()
            Read()
            sleep(0.5)
            if rb:
                break
        except:
            Close()
            break
    Release()
    Close()
    Exit()