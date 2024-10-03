import numpy as np
import re

def array1D(start, end, step):
    if start <= end:
        step = +abs(step)
    else:
        step = -abs(step)
    array = np.arange(start, end, step)
    array = np.append(array, end)
    array = array.tolist()
    return array

def array1Dnum(start, end, number):
    array = np.linspace(start, end, number)
    array = array.tolist()
    return array

def sarray1D(start,end,step,*args):
    """
    # First column is file suffix: 0 is original dataset, 1 is retrace dataset, 2 is dump dataset
    # Second column is index: 0,1,2,3,4,5,...
    # From the third column is the scan array
    """
    line = 0
    array1 = []
    for d1 in array1D(start, end, step):
        array1.append([0, line, d1])
        line = line + 1
    for d1 in array1D(start, end, step)[::-1]:
        array1.append([1, line, d1])
        line = line + 1
    return array1

def sarray1Dnum(start,end,number,*args):
    """
    # First column is file suffix: 0 is original dataset, 1 is retrace dataset, 2 is dump dataset
    # Second column is index: 0,1,2,3,4,5,...
    # From the third column is the scan array
    """
    line = 0
    array1 = []
    for d1 in array1Dnum(start, end, number):
        array1.append([0, line, d1])
        line = line + 1
    for d1 in array1Dnum(start, end, number)[::-1]:
        array1.append([1, line, d1])
        line = line + 1
    return array1

def sarray2D(start1, end1, step1, start2, end2, step2):
    """
    # First column is file suffix: 0 is original dataset, 1 is retrace dataset, 2 is dump dataset
    # Second column is index: 0,1,2,3,4,5,...
    # From the third column is the scan array
    """
    line = 0
    array2 = []
    for d2 in array1D(start2, end2, step2):
        for d1 in array1D(start1, end1, step1):
            array2.append([0, line, d1, d2])
            line = line + 1
        for d1 in array1D(start1, end1, step1)[::-1]:
            array2.append([1, line, d1, d2])
            line = line + 1
    return array2

def sarray2Dnum(start1, end1, number1, start2, end2, number2):
    """
    # First column is file suffix: 0 is original dataset, 1 is retrace dataset, 2 is dump dataset
    # Second column is index: 0,1,2,3,4,5,...
    # From the third column is the scan array
    """
    line = 0
    array2 = []
    for d2 in array1Dnum(start2, end2, number2):
        for d1 in array1Dnum(start1, end1, number1):
            array2.append([0, line, d1, d2])
            line = line + 1
        for d1 in array1Dnum(start1, end1, number1)[::-1]:
            array2.append([1, line, d1, d2])
            line = line + 1
    return array2

def findnum(instring):
    # Find all numbers in a string
    returndata= re.findall(r"[-+]?\d+\.?\d*[eE]?[-+]?\d*", instring)
    # print(returndata)
    numarray = list(map(float, returndata))
    if len(numarray)==0:
        numarray = [0]
    return numarray

def get(parameters, name):
    out = ""
    try:
        for pair in parameters:
            (parameter_name, parameter_value) = pair
            if parameter_name == name:
                out = parameter_value
                break
    except:
        pass
    return out