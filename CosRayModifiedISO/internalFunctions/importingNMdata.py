import os
import pandas as pd
import pickle as pkl
import datetime as dt

from CosRayModifiedISO.internalFunctions.miscellaneous import homeDirectory
from importlib_resources import files
#import pkg_resources

def readInOULUdata()->pd.DataFrame:

    inputPKLfile = files('CosRayModifiedISO.neutronMonitorData').joinpath('OULUinputData.pkl')
    inputOULUDATfile = files('CosRayModifiedISO.neutronMonitorData').joinpath('OULU_1964_04_01 _00_00_2021_01_31 _00_00.dat')

    if not os.path.isfile(inputPKLfile):

        inputDF = pd.read_csv(inputOULUDATfile,
                            skiprows=22, header=None, skipfooter=3, delimiter=" ")
        inputDF.drop(6,axis=1,inplace=True)
        inputDF.columns = ["date", "time", "fractional year", "uncorrected counts / min", "corrected counts / min", "barometric pressure (mbar)"]
        inputDF["datetime"] = (inputDF["date"]+" " + inputDF["time"]).apply(lambda row:dt.datetime.strptime(row,"%Y.%m.%d %H:%M:%S"))

        outputDF = inputDF[["datetime","corrected counts / min"]]

        with open(inputPKLfile,"wb") as OULUPKLfile:
            pkl.dump(outputDF,OULUPKLfile)

    else:

        with open(inputPKLfile,"rb") as OULUPKLfile:
            outputDF = pkl.load(OULUPKLfile)

    return outputDF

def getOULUcountRateForTimestamp(timestamp:dt.datetime)->float:

    OULUfullDF = readInOULUdata()

    outputCountRate = OULUfullDF[(OULUfullDF["datetime"] <= timestamp)].tail(1)["corrected counts / min"].iloc[0]

    return outputCountRate/60.0 #converting into per second