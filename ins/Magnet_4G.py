"""
    Cryomagnetic Model 4G Magnet controller
    Example for python + pyvisa based communications
    Example for complicated functions
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

class Magnet4G(LandscapeInstrument):
    Description = "Magnet4G Z-X"
    Version = "1.0"
    Type = "Python"
    # Default, use internal VI
    # External, use a labview .vi
    # Python, use a python file
    Address = ""
    Instrument_Address = "Not Defined" #Instrument VISA Address
    Mode = ""
    Scan_Name = "B_set (T)"
    Retrieve_Command = "IOUT?"
    Scan_Command = ""
    Ramp_Step = "0.01" # in A/s
    Scan_Condition = "0.00002" #20uT
    Ramp_Delay = "" # in second
    Scan_Limit = r""
    Scan_Stablize = ""
    Scan_Stablize_Timeout = "600s"
    External_VI_Behavior = "Mini"
    Read_Command = r"IOUT?"
    Read_Name = r""
    Buffer = "True"
    Read_Termination = "\n"
    Previous_Value = 0

    def setmode(self, mode = ""):
        if not mode == "":
            self.Mode = mode
        if self.Mode == "Z":
            self.Read_Name = r"I_z (A)\B_z (T)"
        elif self.Mode == "X":
            self.Read_Name = r"I_x (A)\B_x (T)"
        else:
            pass

    @InitializeDecorator
    def initialize(self):
        if self.Mode == "Z":
            self.ins.write("REMOTE")
            self.ins.write("CHAN 1")
            self.ins.write("UNITS A")
            self.rate = min(ut.findnum(self.Ramp_Step)[0], 0.1)
            self.rate = max(self.rate, 0.01)
            self.ins.write("RATE 0 {:.4g}".format(self.rate))
            self.c = 972.0 # Gauss/A
        elif self.Mode == "X":
            self.ins.write("REMOTE")
            self.ins.write("CHAN 2")
            self.ins.write("UNITS A")
            self.rate = min(ut.findnum(self.Ramp_Step)[0], 0.015)
            self.rate = max(self.rate, 0.01)
            self.ins.write("RATE 0 {:.4g}".format(self.rate))
            self.c = 551.6 # Gauss/A
        else:
            pass
        return self
    
ins = Magnet4G()

def Call(parameters):
    global ins
    print("Calling")
    result = "Called"
    ins.setup(parameters)
    ins.call()
    return (ins.instrument_parameters(), result)

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
    ins.stbcount = 0
    ins.near = False
    ins.overshoot = False
    ins.field_arrived = False
    ins.field_timer = 0
    for i in range(5):
        try:
            rd = sv-ins.Previous_Value
            d = rd/abs(rd) * min(abs(rd)*0.5, 0.0375*ins.c/10000)
            ins.raw_write("ULIM {:.4g}".format((sv+d)/ins.c*10000))
            ins.raw_write("SWEEP UP")
            break
        except Exception as e:
            print(e)
            pass
    for i in range(5):
        try:
            ins.write().read()
            break
        except Exception as e:
            print(e)
            pass
    rb = True
    # rt = ut.findnum(ins.Scan_Stablize_Timeout)[0]
    rt = 600
    return (result, rb, rt)

def Approach(sv):
    global ins
    result = "Approached"
    rb = False
    rt = ut.findnum(ins.Scan_Stablize_Timeout)[0]
    # condition = min(max(abs(sv-ins.Previous_Value)*0.25, 0.000075), ins.rate*0.25*ins.c/10000)
    condition = min(max(abs(sv-ins.Previous_Value)*0.25, 0.0002*ins.c/10000), ins.rate*0.5*ins.c/10000)
    if ins.rresult == "":
        rb = False
    else:
        if abs(ut.findnum(ins.rresult)[0]*ins.c/10000 - sv) <= condition and not ins.near:
            ins.raw_write("ULIM {:.4g}".format(sv/ins.c*10000))
            ins.raw_write("SWEEP UP")
            for i in range(5):
                try:
                    ins.write().read()
                    break
                except:
                    pass
            ins.near = True
            ins.overshoot = True
            print("Field Near, start = %g, target = %g, now = %g, rate = %g, d = %g, condition = %g" % (ins.Previous_Value, sv, ut.findnum(ins.rresult)[0]*ins.c/10000, ins.rate, abs(ut.findnum(ins.rresult)[0]*ins.c/10000 - sv), condition))
        if ((ut.findnum(ins.rresult)[0]*ins.c/10000 <= sv <= ins.Previous_Value) or (ut.findnum(ins.rresult)[0]*ins.c/10000 >= sv >= ins.Previous_Value)) and not ins.overshoot:
            ins.raw_write("ULIM {:.4g}".format(sv/ins.c*10000))
            ins.raw_write("SWEEP UP")
            for i in range(5):
                try:
                    ins.write().read()
                    break
                except:
                    pass
            ins.near = True
            ins.overshoot = True
            print("Field Overshoot, start = %g, target = %g, now = %g, rate = %g, d = %g, condition = %g" % (ins.Previous_Value, sv, ut.findnum(ins.rresult)[0]*ins.c/10000, ins.rate, abs(ut.findnum(ins.rresult)[0]*ins.c/10000 - sv), condition))
        if ins.near:
            if abs(ut.findnum(ins.rresult)[0]*ins.c/10000 - sv) <= min(max(abs(ut.findnum(ins.Scan_Condition)[0]), abs(sv-ins.Previous_Value)*0.01), 0.0001):
                ins.stbcount = ins.stbcount + 1
            else:
                ins.stbcount = max(ins.stbcount - 5, 0)
            rb = ins.stbcount >= 10
            if rb and not ins.field_arrived:
                ins.field_arrived = True
                ins.field_timer = time.time()
                print("Field Arrived")
                ins.Previous_Value = sv
                rb = False
                rt = 600
            if ins.field_arrived:
                rb = (time.time() - ins.field_timer) >= ut.findnum(ins.Scan_Stablize_Timeout)[0]
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
    b = ut.findnum(result)[0] * ins.c /10000
    result = result + str(b)
    return result

def Start_Monitor():
    global ins
    ins.setmode("Z")
    ins.call()
    ins.initialize()
    ins.start_monitor()

def Stop_Monitor():
    global ins
    ins.stop_monitor()

def Log():
    global ins
    result = ""
    result = ins.log()
    b = ut.findnum(result)[0] * ins.c /10000
    result = result +  str(b) + "T"
    return (ins.Read_Name, result)

def Close():
    global ins
    ins.close()
    return "Closed"

def Exit():
    global ins
    ins.exit()
    return "Exited"

if __name__ == "__main__":
    k = Magnet4G()
    k.Instrument_Address = "TCPIP0::192.168.1.21::7777::SOCKET"
    Call(k.instrument_parameters())
    Initialize()
    Start_Monitor()
    while True:
        try:
            sleep(1)
            print("---------")
            print(Log())
            print("---------")
        except:
            Stop_Monitor()
            break
    Close()
    Exit()