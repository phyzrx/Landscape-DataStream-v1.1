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
        
        self.__monitor_stop = True
        try:
            self.__monitor_thread.join()
        except:
            pass

        self.__rs = abs(LandscapeUtilities.findnum(self.Ramp_Step)[0])
        if self.__rs == 0:
            self.__rs = float("+inf")
        self.__rd = LandscapeUtilities.findnum(self.Ramp_Delay)[0]
        self.__rd = max(0, self.__rd)
        try:
            self.__smin = min(LandscapeUtilities.findnum(self.Scan_Limit)[0], LandscapeUtilities.findnum(self.Scan_Limit)[1])
            self.__smax = max(LandscapeUtilities.findnum(self.Scan_Limit)[0], LandscapeUtilities.findnum(self.Scan_Limit)[1])
        except:
            try:
                self.__smax = LandscapeUtilities.findnum(self.Scan_Limit)[0]
                self.__smin = float("-inf")
            except:
                self.__smax = float("+inf")
                self.__smin = float("-inf")
        self.__rc = self.Read_Command.split("\\")
        trc = []
        for cmd in self.__rc:
            if not trc == "":
                trc = trc + [cmd]
        self.__rc = trc
        self.__wd = LandscapeUtilities.findnum(self.Write_Delay)[0]
        self.__wd = max(0, self.__wd)
        self.__md = LandscapeUtilities.findnum(self.Monitor_Delay)[0]
        self.__md = max(0, self.__md)
        self.__rresult = ""
        self.__buff = self.__buffer.startswith("T") or self.__buffer.startswith("t")

        print("%s @ %s : is Called" %(self.Description, str(self.Instrument_Address)))

        return self

    def open_resource(self):
        opened = False
        try:
            self.__ins = self.__ins
        except:
            rm = pyvisa.ResourceManager()
            self.__ins = rm.open_resource(self.Instrument_Address)
            print("%s @ %s : resource is Opened" %(self.Description, str(self.Instrument_Address)))
            opened = True
        if self.__ins == None:
            rm = pyvisa.ResourceManager()
            self.__ins = rm.open_resource(self.Instrument_Address)
            if not self.Read_Termination == "":
                self.__ins.read_termination = self.Read_Termination
            print("%s @ %s : resource is Opened" %(self.Description, str(self.Instrument_Address)))
            opened = True
        else:
            if not self.Read_Termination == "":
                self.__ins.read_termination = self.Read_Termination
            if not opened:
                print("%s @ %s : resource might already Opened" %(self.Description, str(self.Instrument_Address)))

    def initialize(self):
        print("%s @ %s : Default Initialize Function is Called" % (self.Description, str(self.Instrument_Address)))
        try:
            self.__ins.clear()
            print("%s @ %s : is Initialzied" % (self.Description, str(self.Instrument_Address)))
        except Exception as e:
            print("%s @ %s : Initialze with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Initialze with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return self
    
    def retrieve(self):
        try:
            self.Previous_Value = LandscapeUtilities.findnum(self.__ins.query(self.Retrieve_Command))[0]
            print("%s @ %s : was at Value = %g"  % (self.Description, str(self.Instrument_Address), self.Previous_Value))
        except Exception as e:
            print("%s @ %s : Retrieve with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Retrieve with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return self

    def approach(self, sv):
        try:
            sv = min(sv, self.__smax)
            sv = max(sv, self.__smin)
            target = sv
            if sv == self.Previous_Value:
                pass
            else:
                if sv >= self.Previous_Value:
                    sv = min(self.Previous_Value+self.__rs, sv)
                else:
                    sv = max(self.Previous_Value-self.__rs, sv)
                self.__ins.write(self.Scan_Command.format(sv))
                self.Previous_Value = sv
                sleep(self.__rd)
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
        print("%s @ %s : starts Scan from %g to %g at step %g" % (self.Description, str(self.Instrument_Address), startv, endv, self.__rs))
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
        if self.__monitor_stop:
            rresult = ""
            try:
                for cmd in self.__rc:
                    self.__ins.write(cmd)
                    if not self.__buff:
                        rresult = rresult + self.__ins.read() + ","
                    else:
                        sleep(self.__wd)
                if not self.__buff:
                    self.__rresult = rresult
            except Exception as e:
                print("%s @ %s : Write with Error" % (self.Description, str(self.Instrument_Address)))
                print(e)
                raise err("%s @ %s : Write with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        else:
            pass
        return self

    def read(self):
        if self.__monitor_stop:
            try:
                rresult = ""
                if self.__buff:
                    for cmd in self.__rc:
                        rresult = rresult + self.__ins.read() + ","
                    self.__rresult = rresult
                else:
                    pass
            except Exception as e:
                print("%s @ %s : Read with Error" % (self.Description, str(self.Instrument_Address)))
                print(e)
                self.__rresult = "ERROR+" + rresult + "+ERROR"
                raise err("%s @ %s : Read with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
            print("%s @ %s : Read: %s" % (self.Description, str(self.Instrument_Address), self.__rresult.replace("\r","").replace("\n","")))
        else:
            pass
        result = self.__rresult
        return result

    def raw_write(self, command):
        try:
            self.__ins.write(str(command))
            print("%s @ %s : Write = %s" % (self.Description, str(self.Instrument_Address), str(command)))
        except Exception as e:
            print("%s @ %s : Write = %s with Error" % (self.Description, str(self.Instrument_Address), str(command)))
            print(e)
            raise err("%s @ %s : Write = %s with Error: %s" % (self.Description, str(self.Instrument_Address), str(command), str(e)))
        return self
    
    def raw_read(self):
        result = ""
        try:
            result = self.__ins.read()
            print("%s @ %s : Reads = %s" % (self.Description, str(self.Instrument_Address), str(result).replace("\r","").replace("\n","")))
        except Exception as e:
            print("%s @ %s : Read with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Read with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return result
    
    def raw_clear(self):
        try:
            self.__ins.clear()
            print("%s @ %s : Cleared" % (self.Description, str(self.Instrument_Address)))
        except Exception as e:
            print("%s @ %s : Clear with Error" % (self.Description, str(self.Instrument_Address)))
            print(e)
            raise err("%s @ %s : Clear with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
        return self

    def monitor_loop(self):
        while True:
            if self.__monitor_stop:
                break
            if not self.__monitor_stop:
                ## Write Process
                rresult = ""
                try:
                    for cmd in self.__rc:
                        self.__ins.write(cmd)
                        if not self.__buff:
                            rresult = rresult + self.__ins.read() + ","
                        else:
                            delay = 0
                            while delay < self.__wd:
                                sleep(0.2)
                                delay = delay + 0.2
                                if self.__monitor_stop:
                                    break
                except Exception as e:
                    print("%s @ %s : Write with Error" % (self.Description, str(self.Instrument_Address)))
                    print(e)
                    raise err("%s @ %s : Write with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
                ## Read Process
                try:
                    if self.__buff:
                        for cmd in self.__rc:
                            rresult = rresult + self.__ins.read() + ","
                    else:
                        pass
                    self.__rresult = rresult
                    delay = 0
                    while delay < self.__md:
                        sleep(0.2)
                        delay = delay + 0.2
                        if self.__monitor_stop:
                            break
                except Exception as e:
                    print("%s @ %s : Read with Error" % (self.Description, str(self.Instrument_Address)))
                    print(e)
                    self.__rresult = "ERROR+" + self.__rresult + "+ERROR"
                    raise err("%s @ %s : Read with Error: %s" % (self.Description, str(self.Instrument_Address), str(e)))
                print("%s @ %s : Monitor: %s" % (self.Description, str(self.Instrument_Address), self.__rresult.replace("\r","").replace("\n","")))

    def start_monitor(self):
        if self.__monitor_stop:
            self.__monitor_stop = False
            self.open_resource()
            import threading as th
            self.__monitor_thread = th.Thread(target=self.monitor_loop)
            self.__monitor_thread.start()
            print("%s @ %s : monitor loop Started" % (self.Description, str(self.Instrument_Address)))
        else:
            print("%s @ %s : monitor loop might already Started" % (self.Description, str(self.Instrument_Address)))
        return self
    
    def stop_monitor(self):
        self.__monitor_stop = True
        self.__monitor_thread.join()
        return self

    def log(self):
        result = ""
        try:
            if not self.__monitor_stop:
                result = self.__rresult.replace("\r","").replace("\n","")
        except:
            pass
        return result
    
    def close(self):
        print("%s @ %s : is Closed" % (self.Description, str(self.Instrument_Address)))
        return self

    def release_resource(self):
        try:
            self.__ins.close()
            self.__ins = None
            print("%s @ %s : resource is Released" % (self.Description, str(self.Instrument_Address)))
        except:
            try:
                self.__ins = None
            except:
                pass
            print("%s @ %s : resource Release with error, resource might already been released" % (self.Description, str(self.Instrument_Address)))
        return self

    def exit(self):
        try:
            self.stop_monitor()
        except:
            pass
        try:
            self.__ins.close()
        except:
            pass
        print("%s @ %s : is Exited" % (self.Description, str(self.Instrument_Address)))
        return self
    
    def abort(self):
        sys.exit()
        return self
    
if __name__ == "__main__":
    ins = LandscapeInstrument()