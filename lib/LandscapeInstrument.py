"""
    Class for Landscape Instrument
"""

# To import from outside \lib
# import sys
# path = sys.path[0]
# sys.path.append(path + r"\lib")

import pyvisa
import LandscapeUtilities
from LandscapeError import LandscapeERROR as err
from time import sleep
import sys

def InitializeDecorator(func):
    def wrapper(*args, **kwargs):
        try:
            fc = func(*args, **kwargs)
            fc.ins.clear()
            print("%s @ %s : is Initialzied" % (fc.Description, str(fc.Instrument_Address)))
        except Exception as e:
            print("%s @ %s : Initialze with Error" % (fc.Description, str(fc.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Initialze with Error: %s" % (fc.Description, str(fc.Instrument_Address), str(e)))
            fc = None
        return fc
    return wrapper

def CallDecorator(func):
    def wrapper(*args, **kwargs):
        try:
            fc = func(*args, **kwargs)
            fc.ins.clear()
            print("%s @ %s : is Called" % (fc.Description, str(fc.Instrument_Address)))
        except Exception as e:
            print("%s @ %s : Call with Error" % (fc.Description, str(fc.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Call with Error: %s" % (fc.Description, str(fc.Instrument_Address), str(e)))
            fc = None
        return fc
    return wrapper

class LandscapeInstrument():
    Description = "Standard"
    Version = "1.0"
    Type = "Python"
    # Default, use internal VI
    # External, use a labview .vi
    # Python, use a python file
    Address = ""
    Instrument_Address = "Not Defined" #Instrument VISA Address
    Mode = ""
    Scan_Name = "Set"
    Retrieve_Command = ""
    Scan_Command = ""
    Ramp_Step = "" #
    Ramp_Delay = "" # in second
    Scan_Limit = r""
    Scan_Stablize = "False"
    Scan_Stablize_Timeout = "0s"
    External_VI_Behavior = "Mini"
    Read_Command = r""
    Read_Name = r""
    Buffer = "True"
    Write_Delay = "" # in second
    Read_Termination = ""
    Monitor_Delay = "5s"
    Previous_Value = 0

    def __init__(self, address=""):
        self.Address = str(address)

    def setup(self, parameters):
        try:
            for pair in parameters:
                (parameter_name, parameter_value) = pair
                self.__setattr__(parameter_name.replace(" ", "_"), parameter_value)
        except:
            pass
        return self

    def instrument_parameters(self):
        all_names = dir(self)
        p = []
        for name in all_names:
            if not name.startswith("__"):
                value = str(self.__getattribute__(name))
                if not value.startswith("<bound method"):
                    p = p + [(str(name).replace("_", " "), str(value))]
        return p
    
    def get_parameter(self, parameter_name=""):
        value = ""
        try:
            value = str(self.__getattribute__(parameter_name))
        except:
            pass
        return value

    def identify(self, Description = ""):
        if not Description == "":
            self.Description = Description
        return self.Description

    def call(self, insaddress = ""):
        if insaddress == "":
            insaddress = self.Instrument_Address
        else:
            self.Instrument_Address = insaddress
        
        self.monitor_stop = True
        try:
            self.monitor_thread.join()
        except:
            pass

        self.rs = abs(LandscapeUtilities.findnum(self.Ramp_Step)[0])
        if self.rs == 0:
            self.rs = float("+inf")
        self.rd = LandscapeUtilities.findnum(self.Ramp_Delay)[0]
        self.rd = max(0, self.rd)
        try:
            self.smin = min(LandscapeUtilities.findnum(self.Scan_Limit)[0], LandscapeUtilities.findnum(self.Scan_Limit)[1])
            self.smax = max(LandscapeUtilities.findnum(self.Scan_Limit)[0], LandscapeUtilities.findnum(self.Scan_Limit)[1])
        except:
            try:
                self.smax = LandscapeUtilities.findnum(self.Scan_Limit)[0]
                self.smin = float("-inf")
            except:
                self.smax = float("+inf")
                self.smin = float("-inf")
        self.rc = self.Read_Command.split("\\")
        trc = []
        for cmd in self.rc:
            if not trc == "":
                trc = trc + [cmd]
        self.rc = trc
        self.wd = LandscapeUtilities.findnum(self.Write_Delay)[0]
        self.wd = max(0, self.wd)
        self.md = LandscapeUtilities.findnum(self.Monitor_Delay)[0]
        self.md = max(0, self.md)
        self.rresult = ""
        self.buff = self.Buffer.startswith("T") or self.Buffer.startswith("t")

        print("%s @ %s : is Called" %(self.Description, str(self.Instrument_Address)))

        return self

    def open_resource(self):
        try:
            rm = pyvisa.ResourceManager()
            self.ins = rm.open_resource(self.Instrument_Address)
            if not self.Read_Termination == "":
                self.ins.read_termination = self.Read_Termination
            print("%s @ %s : resource is Opened" %(self.Description, str(self.Instrument_Address)))
        except Exception as e:
            try:
                self.ins.read_termination = self.Read_Termination
            except:
                pass
            print("%s @ %s : resource Open with error, resource might already been openned" % (self.Description, str(self.Instrument_Address)))

    def initialize(self):
        print("%s @ %s : Default Initialize Function is Called" % (self.Description, str(self.Instrument_Address)))
        try:
            self.ins.clear()
            print("%s @ %s : is Initialzied" % (self.Description, str(self.Instrument_Address)))
        except Exception as e:
            print("%s @ %s : Initialze with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Initialze with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return self
    
    def retrieve(self):
        try:
            self.Previous_Value = LandscapeUtilities.findnum(self.ins.query(self.Retrieve_Command))[0]
            print("%s @ %s : was at Value = %g"  % (self.Description, str(self.Instrument_Address), self.Previous_Value))
        except Exception as e:
            print("%s @ %s : Retrieve with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Retrieve with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return self

    def approach(self, sv):
        try:
            sv = min(sv, self.smax)
            sv = max(sv, self.smin)
            target = sv
            if sv == self.Previous_Value:
                pass
            else:
                if sv >= self.Previous_Value:
                    sv = min(self.Previous_Value+self.rs, sv)
                else:
                    sv = max(self.Previous_Value-self.rs, sv)
                self.ins.write(self.Scan_Command.format(sv))
                self.Previous_Value = sv
                sleep(self.rd)
            rbool = sv == target
            if rbool:
                print("%s @ %s : Approached Target = %g" % (self.Description, str(self.Instrument_Address), target))
            else:
                print("%s @ %s : Approaching Target = %g Set = %g" % (self.Description, str(self.Instrument_Address), target, sv))
        except Exception as e:
            print("%s @ %s : at %g Approached with Error" % (self.Description, str(self.Instrument_Address), self.Previous_Value))
            print(e)
            rbool = True
            raise err("%s @ %s : at %g Approached with Error: %s" % (self.Description, str(self.Instrument_Address), self.Previous_Value, str(e)))
        return rbool
    
    def scan(self, sv):
        startv = self.Previous_Value
        endv = sv
        print("%s @ %s : starts Scan from %g to %g at step %g" % (self.Description, str(self.Instrument_Address), startv, endv, self.rs))
        while True:
            try:
                if self.approach(sv):
                    break
            except Exception as e:
                print("%s @ %s : at %g Scan with Error" % (self.Description, str(self.Instrument_Address), self.Previous_Value))
                print(e)
                raise("%s @ %s : at %g Scan with Error: %s" % (self.Description, str(self.Instrument_Address), self.Previous_Value, str(e)))
        return self

    def write(self):
        if self.monitor_stop:
            rresult = ""
            try:
                for cmd in self.rc:
                    self.ins.write(cmd)
                    if not self.buff:
                        rresult = rresult + self.ins.read() + ","
                    else:
                        sleep(self.wd)
                if not self.buff:
                    self.rresult = rresult
            except Exception as e:
                print("%s @ %s : Write with Error" % (self.Description, str(self.Instrument_Address)))
                print(e)
                raise err("%s @ %s : Write with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        else:
            pass
        return self

    def read(self):
        if self.monitor_stop:
            try:
                rresult = ""
                if self.buff:
                    for cmd in self.rc:
                        rresult = rresult + self.ins.read() + ","
                    self.rresult = rresult
                else:
                    pass
            except Exception as e:
                print("%s @ %s : Read with Error" % (self.Description, str(self.Instrument_Address)))
                print(e)
                self.rresult = "ERROR+" + rresult + "+ERROR"
                raise err("%s @ %s : Read with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
            print("%s @ %s : Read: %s" % (self.Description, str(self.Instrument_Address), self.rresult.replace("\r","").replace("\n","")))
        else:
            pass
        result = self.rresult
        return result

    def raw_write(self, command):
        try:
            self.ins.write(str(command))
            print("%s @ %s : Write = %s" % (self.Description, str(self.Instrument_Address), str(command)))
        except Exception as e:
            print("%s @ %s : Write = %s with Error" % (self.Description, str(self.Instrument_Address), str(command)))
            print(e)
            raise err("%s @ %s : Write = %s with Error: %s" % (self.Description, str(self.Instrument_Address), str(command), str(e)))
        return self
    
    def raw_read(self):
        result = ""
        try:
            result = self.ins.read()
            print("%s @ %s : Reads = %s" % (self.Description, str(self.Instrument_Address), str(result).replace("\r","").replace("\n","")))
        except Exception as e:
            print("%s @ %s : Read with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Read with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return result
    
    def raw_clear(self):
        try:
            self.ins.clear()
            print("%s @ %s : Cleared" % (self.Description, str(self.Instrument_Address)))
        except Exception as e:
            print("%s @ %s : Clear with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Clear with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return self

    def monitor_loop(self):
        while True:
            if self.monitor_stop:
                break
            if not self.monitor_stop:
                ## Write Process
                rresult = ""
                try:
                    for cmd in self.rc:
                        self.ins.write(cmd)
                        if not self.buff:
                            rresult = rresult + self.ins.read() + ","
                        else:
                            delay = 0
                            while delay < self.wd:
                                sleep(0.2)
                                delay = delay + 0.2
                                if self.monitor_stop:
                                    break
                except Exception as e:
                    print("%s @ %s : Write with Error" % (self.Description, str(self.Instrument_Address)))
                    print(e)
                    raise err("%s @ %s : Write with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
                ## Read Process
                try:
                    if self.buff:
                        for cmd in self.rc:
                            rresult = rresult + self.ins.read() + ","
                    else:
                        pass
                    self.rresult = rresult
                    delay = 0
                    while delay < self.md:
                        sleep(0.2)
                        delay = delay + 0.2
                        if self.monitor_stop:
                            break
                except Exception as e:
                    print("%s @ %s : Read with Error" % (self.Description, str(self.Instrument_Address)))
                    print(e)
                    self.rresult = "ERROR+" + self.rresult + "+ERROR"
                    raise err("%s @ %s : Read with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
                print("%s @ %s : Monitor: %s" % (self.Description, str(self.Instrument_Address), self.rresult.replace("\r","").replace("\n","")))

    def start_monitor(self):
        if self.monitor_stop:
            self.open_resource()
            import threading as th
            self.monitor_thread = th.Thread(target=self.monitor_loop)
            self.monitor_thread.start()
            print("%s @ %s : monitor loop Started" % (self.Description, str(self.Instrument_Address)))
        else:
            print("%s @ %s : monitor loop might already Started" % (self.Description, str(self.Instrument_Address)))
        return self
    
    def stop_monitor(self):
        self.monitor_stop = True
        self.monitor_thread.join()
        return self

    def log(self):
        return self.rresult.replace("\r","").replace("\n","")
    
    def close(self):
        print("%s @ %s : is Closed" % (self.Description, str(self.Instrument_Address)))
        return self

    def release_resource(self):
        try:
            self.ins.close()
            print("%s @ %s : resource is Released" % (self.Description, str(self.Instrument_Address)))
        except:
            print("%s @ %s : resource Release with error, resource might already been released" % (self.Description, str(self.Instrument_Address)))
        return self

    def exit(self):
        try:
            self.stop_monitor()
        except:
            pass
        try:
            self.ins.close()
        except:
            pass
        print("%s @ %s : is Exited" % (self.Description, str(self.Instrument_Address)))
        return self
    
    def abort(self):
        sys.exit()
        return self
    
if __name__ == "__main__":
    ins = LandscapeInstrument()