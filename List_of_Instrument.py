# List of Instrument for Landscape DataStream
import sys
path = sys.path[0]
sys.path.append(path + r"\lib")
sys.path.append(path + r"\ins")
import inspect

def i1(*args):
    from Keithley_2450 import Keithley2450
    p = Keithley2450(inspect.getfile(Keithley2450))
    p.Description = "K2450-1"
    p.Instrument_Address = "TCPIP0::192.168.1.101::inst0::INSTR"
    p.Ramp_Step = "0.5"
    return (p.Description, p.instrument_parameters())

### ----------------------------------------------------------------- ###
# End of instruments
p = dir()
all_instruments = []
for name in p:
    if not name.startswith("__"):
        value = str(eval(name))
        if value.startswith("<function"):
            all_instruments = all_instruments + [str(name)]
def get_all_instrument(*args):
    global all_instruments
    result = []
    for instrument in all_instruments:
        result = result + [globals()[instrument](*args)]
    return result
def compile_instrument(Description):
    global all_instruments
    result = []
    for instrument in all_instruments:
        (d, p) = globals()[instrument]()
        if d == Description:
            result = p
            break
    return result

if __name__ == "__main__":
    print(get_all_instrument())
    print(compile_instrument("K2450-1"))