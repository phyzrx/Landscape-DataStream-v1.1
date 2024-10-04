"""
    Class for Landscape Dataset
"""

# To import from outside \lib
# import sys
# path = sys.path[0]
# sys.path.append(path + r"\lib")

import LandscapeUtilities
from time import sleep
from collections import OrderedDict

class LandscapeDataset():
    """
    ---
    Strings:
    Description, File Name, Dataset Name, Note, Scan Delay, Read Interval, Read Repeat, Read After Scan,
    x_start, x_end, x_step, y_start, y_end, y_step, z
    ---
    List of Strings:
    Scan_Instrument, Read_Instrument,
    ---
    Ordered_Dict:
    Data_Processing,
    ---
    Array:
    Scan_Array,
    """
    Description = ""
    File_Name = "Data File Name"
    Dataset_Name = "Dataset"
    Note = ""
    Scan_Delay = "20ms"
    Read_Interval = "0ms"
    Read_Repeat = "1"
    Read_After_Scan = "False"
    x_start = None
    x_end = None
    x_step = None
    x_number = None
    y_start = None
    y_end = None
    y_step = None
    y_number = None
    z = ""

    Scan_Instrument = [] # (Instrument_Description, Instrument_Parameters)

    Read_Instrument = [] # (Instrument_Description, Instrument_Parameters)

    Data_Processing = OrderedDict()
    """
    Data_Processing["name"] = "function col(name1)*col(name2)"
    """

    Scan_Array = []

    def __init__(self, file_name, dataset_name = "Dataset", description = "Standard"):
        self.File_Name = str(file_name)
        self.Dataset_Name = str(dataset_name)
        self.Description = str(description)

    def setup(self, parameters):
        try:
            for pair in parameters:
                (parameter_name, parameter_value) = pair
                self.__setattr__(parameter_name.replace(" ", "_"), parameter_value)
        except:
            pass
        return self
    
    def preview_parameters(self):
        all_names = dir(self)
        p = []
        for name in all_names:
            if not name.startswith("__"):
                tpe = type(self.__getattribute__(name))
                value = str(self.__getattribute__(name))
                if not value.startswith("<bound method"):
                    if tpe == str:
                        p = p + [(str(name).replace("_", " "), str(value))]
        k = []
        for key, value in self.Data_Processing.items():
            k = k + [(str(key), str(value))]
        return (p, self.Scan_Instrument, self.Read_Instrument, k)

    def dataset_parameters(self):
        all_names = dir(self)
        p = []
        for name in all_names:
            if not name.startswith("__"):
                tpe = type(self.__getattribute__(name))
                value = str(self.__getattribute__(name))
                if not value.startswith("<bound method"):
                    if tpe == str:
                        p = p + [(str(name).replace("_", " "), str(value))]

        if self.Scan_Array == []:
            if self.x_start == None or self.x_end == None or (self.x_step == None and self.x_number == None):
                pass
            elif self.y_start == None or self.y_end == None or (self.y_step == None and self.y_number == None):
                if not self.x_step == None:
                    self.Scan_Array = LandscapeUtilities.sarray1D(float(self.x_start), float(self.x_end), float(self.x_step))
                else:
                    self.Scan_Array = LandscapeUtilities.sarray1Dnum(float(self.x_start), float(self.x_end), float(self.x_number))
            else:
                if (not self.x_step == None) and (not self.y_step == None):
                    self.Scan_Array = LandscapeUtilities.sarray2D(float(self.x_start), float(self.x_end), float(self.x_step), float(self.y_start), float(self.y_end), float(self.y_step))
                elif (not self.x_number == None) and (not self.y_number == None):
                    self.Scan_Array = LandscapeUtilities.sarray2Dnum(float(self.x_start), float(self.x_end), float(self.x_number), float(self.y_start), float(self.y_end), float(self.y_number))
                elif False:
                    pass
                else:
                    pass
        k = []
        for key, value in self.Data_Processing.items():
            k = k + [(str(key), str(value))]
        return (p, self.Scan_Instrument, self.Read_Instrument, self.Scan_Array, k)
    
    def preview(self, *args):
        while type(args) == tuple:
            try:
                (args, *rst) = args
            except:
                break
        if len(args) == 0 or args == "" or args == "Preview" or args[0] == "" or args[0] == "Preview":
            return (self.preview_parameters())
        else:
            return (self.dataset_parameters())

    def identify(self, Description = ""):
        if not Description == "":
            self.Description = Description
        return self.Description

    def scan(self, Instrument_Description, Instrument_Parameters = []):
        self.Scan_Instrument = self.Scan_Instrument + [(Instrument_Description, Instrument_Parameters)]
        return self
    
    def read(self, Instrument_Description, Instrument_Parameters = []):
        self.Read_Instrument = self.Read_Instrument + [(Instrument_Description, Instrument_Parameters)]
        return self
    
    def process(self, name = "", function = ""):
        self.Data_Processing.update({name: function})
        return self
    
if __name__ == "__main__":
    d = LandscapeDataset("1")
    print(d.preview("Preview"))