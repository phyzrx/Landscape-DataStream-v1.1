"""
    Keithley 2450 Source Meter
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
            self.ins.clear()
            self.ins.write(":SENS:FUNC \"CURR\"")
            self.ins.write(":SENS:CURR:UNIT AMP")
            self.ins.write(":SENS:CURR:NPLC 1")
            self.ins.write(":SENS:CURR:RANG 1E-6")
            self.ins.write("TRAC:CLE \"defbuffer1\"")
        else:
            pass
        return self

ins = Keithley2450() # Instrument Class

def Identify(*arg):
    return ins.identify(*arg)

def Call(parameters):
    global ins
    print("Calling")
    result = "Called"
    try:
        ins.setup(parameters)
        ins.call()
    except Exception as e:
        try:
            ins.close()
        except:
            pass
        print(e)
        result = False
    return (ins.instrument_parameters(), result)

def Initialize(*args):
    global ins
    result = "Initialized"
    try:
        ins.initialize()
    except Exception as e:
        try:
            ins.close()
        except:
            pass
        print(e)
        result = False
    return result

def Retrieve(*arg):
    global ins
    result = "Retrieved"
    try:
        ins.retrieve()
    except Exception as e:
        try:
            ins.close()
        except:
            pass
        print(e)
        result = False
    return result

def Scan(sv):
    global ins
    result = "Scanned"
    rb = False
    rt = 0
    try:
        ins.scan(sv)
        # rb = not ins.approach(sv)
        # rt = 600
    except Exception as e:
        try:
            ins.close()
        except:
            pass
        print(e)
        result = False
    return (result, rb, rt)

def Approach(sv):
    global ins
    result = "Approached"
    rb = False
    rt = 0
    try:
        rb = ins.approach(sv)
        rt = 600
    except Exception as e:
        try:
            ins.close()
        except:
            pass
        print(e)
        result = False
    return (result, rb, rt)

def Write():
    global ins
    result = "Write Done"
    try:
        ins.write()
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

def Start_Monitor():
    global ins
    ins.start_monitor()

def Stop_Monitor():
    global ins
    ins.stop_monitor()

def Log():
    global ins
    return ins.log()

def Close():
    global ins
    try:
        ins.close()
    except:
        pass
    return "Closed"

if __name__ == "__main__":
    print(Identify("K2450-1"))
    Call([("Instrument Address", r"TCPIP0::192.168.1.101::inst0::INSTR")])
    Initialize()
    Retrieve()
    Start_Monitor()
    sleep(1)
    while True:
        try:
            Scan(0)
            print("--------")
            print(Log())
            print("--------")
            sleep(0.5)
        except:
            Stop_Monitor()
            Close()
            break