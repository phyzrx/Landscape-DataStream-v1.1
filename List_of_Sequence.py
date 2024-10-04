# List of Sequence for Landscape DataStream
import sys
path = sys.path[0]
sys.path.append(path + r"\lib")
sys.path.append(path + r"\ins")

from LandscapeDataset import LandscapeDataset as dt

def d1(*arg):
    d = dt("Sequence Step 01")
    d.Description = "Sequence Step 01"
    ins = "K2450-1"
    conf = [
        ("Parameter Name 1", "Parameter Value 1")
    ]
    d.scan(ins, conf)
    d.read(ins, conf)
    d.x_start = 0
    d.x_end = 1
    d.x_step = 0.1
    return (d.Description, d.preview(*arg))

### ----------------------------------------------------------------- ###
# End of sequences
p = dir()
all_instruments = []
all_sequences = []
for name in p:
    if not name.startswith("__"):
        if not name in all_instruments:
            if not name == "get_all_instrument":
                value = str(eval(name))
                if value.startswith("<function"):
                    all_sequences = all_sequences + [str(name)]
def get_all_sequence():
    global all_sequences
    result = []
    for sequence in all_sequences:
        result = result + [globals()[sequence]()]
    return result
def compile_sequence(Description):
    global all_sequences
    result = ()
    for sequence in all_sequences:
        (d, p) = globals()[sequence]()
        if d == Description:
            (d, p) = globals()[sequence]("Run")
            result = p
            break
    return result

if __name__ == "__main__":
    print(get_all_sequence())
    print(compile_sequence("Sequence Step 01"))