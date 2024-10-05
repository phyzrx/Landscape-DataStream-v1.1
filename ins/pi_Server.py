"""
    pi Server to monitor fridge status
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

class piServer(LandscapeInstrument):
    Description = "piServer for SQUID DR"
    Version = "1.0"
    Type = "Python"
    # Default, use internal VI
    # External, use a labview .vi
    # Python, use a python file
    Address = ""
    Instrument_Address = "Not Defined" #Instrument VISA Address
    Mode = "Monitor All"
    Scan_Name = "T_set (K)"
    Retrieve_Command = "Get T_MC_ADD"
    Scan_Command = ""
    Ramp_Step = "0.01" # in K/min
    Ramp_Delay = "" # in second
    Scan_Limit = r""
    Scan_Stablize = ""
    Scan_Stablize_Timeout = "600s"
    External_VI_Behavior = "Mini"
    Read_Command = r""
    Read_Name = r""
    Buffer = "True"
    Write_Delay = "0.02"
    Read_Termination = "\n"
    Previous_Value = 0
    Heater_Range = "0"

    def setmode(self, mode = ""):
        if not mode == "":
            self.Mode = mode

        group_he_c = r"Get He_Level\Get He_Volume" 
        group_he = r"He_Level (%)\He_Volume (L)"
        group_he_index  = "0, 1,"

        group_tempc_c = r"\Get T_MC_Target\Get T_MC_Set\Get MC_Heater_Range\Get MC_Heater\Get Still_Heater"
        group_tempc = r"\T_MC_Target (K)\T_MC_Set (K)\MC_Heater_Range\MC_Heater (%)\Still_Heater (V)"
        group_tempc_index = "2, 3, 4, 5, 6,"

        group_tempr_c = r"\Get R_IVC\Get R_Still\Get R_ICP\Get R_MC_Cernox\Get R_MC_Sample\Get R_MC_Plate\Get R_MC_Add"
        group_tempr = r"\R_IVC (ohm)\R_Still (ohm)\R_ICP (ohm)\R_MC_Cernox (ohm)\R_MC_Sample (ohm)\R_MC_Plate (ohm)\R_MC_Add (ohm)"
        group_tempr_index = "7, 8, 9, 10, 11, 12, 14,"

        group_temp_c = r"\Get T_IVC\Get T_Still\Get T_ICP\Get T_MC_Cernox\Get T_MC_Sample\Get T_MC_Plate\Get T_MC_Add"
        group_temp = r"\T_IVC (K)\T_Still (K)\T_ICP (K)\T_MC_Cernox (K)\T_MC_Sample (K)\T_MC_Plate (K)\T_MC_Add (K)"
        group_temp_index = "15, 16, 17, 18, 19, 20, 22,"

        group_ghs_c = r"\Get Flow\Get P_DR_Still\Get P_DR_BackPump\Get P_DR_BackCompressor"
        group_ghs = r"\Flow (%)\P_Still (mbar)\P_Back (mbar)\P_Comp (mbar)"
        group_ghs_index = "23, 24, 26, 27,"

        group_1k_c = r"\Get P_1K_Cell\Get P_1K_Condense\Get P_1K_Dump\Get P_1K_1K\Get P_Vacuum"
        group_1k = r"\P_Cell (mbar)\P_Cell_Condense (mbar)\P_Cell_Dump (mbar)\P_1K (mbar)\P_Vacuum (mbar)"
        group_1k_index = "30, 31, 32, 33, 36,"

        if self.Mode == "Monitor All":
            self.Buffer = "False"
            self.Read_Command = "GetAll"
            self.Read_Name = group_he + group_tempc + group_tempr + group_temp + group_ghs + group_1k
            self.rindex = group_he_index + group_tempc_index + group_tempr_index + group_temp_index + group_ghs_index + group_1k_index
        elif False:
            pass
        else:
            pass

ins = piServer() # Instrument Class

def Call(parameters):
    global ins
    print("Calling")
    result = "Called"
    ins.setup(parameters)
    ins.call()
    ins.setmode()
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
    ins.raw_write("Set Control_T OFF").raw_read()
    ins.raw_write("Set T_MC {:.3g}".format(sv)).raw_read()
    ins.raw_write("Set T_MC_Channel 8").raw_read()
    ins.raw_write("Set T_MC_Ramp" + str(ins.Ramp_Step)).raw_read()
    ins.raw_write("Set T_MC_Heater_Range " + str(ins.Heater_Range)).raw_read()
    ins.raw_write("Set Control_T ON").raw_read()
    rb = True
    rt = ut.findnum(ins.Scan_Stablize_Timeout)[0]
    return (result, rb, rt)

def Approach(sv):
    global ins
    result = "Approached"
    rb = False
    rt = 0
    if abs(ut.findnum(ins.raw_write("Get T_MC_Add").raw_read())[0] - sv) <= max(sv*0.001, 0.001):
        ins.stbcount = ins.stbcount + 1
    else:
        ins.stbcount = max(ins.stbcount - 5, 0)
    rb = ins.stbcount >= 20
    rt = 600
    return (result, rb, rt)

def Start_Monitor():
    global ins
    ins.setmode("Monitor All")
    ins.call()
    ins.start_monitor()

def Stop_Monitor():
    global ins
    ins.stop_monitor()

def Log():
    global ins
    return (ins.Read_Name, ins.log())

def Write():
    global ins
    result = "Write Done"
    ins.write()
    return result

def Read():
    global ins
    result = ""
    raw = ins.read()
    for i in ut.findnum(ins.rindex):
        result = result + raw.split(",")[int(i)].split(":")[1] + ", "
    return result

def Close():
    global ins
    ins.close()
    return "Closed"

def Exit():
    global ins
    ins.exit()
    return "Exited"

if __name__ == "__main__":
    k = piServer()
    k.Instrument_Address = "TCPIP0::192.168.1.20::6666::SOCKET"
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