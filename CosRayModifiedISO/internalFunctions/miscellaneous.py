import os

homeDirectory = os.path.dirname(os.path.realpath(__file__)) + "/.."

def convertToIterable(x):

    if hasattr(x, '__iter__'):
        outputIter = x
    else:
        outputIter = [x]

    return outputIter