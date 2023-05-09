import numpy as np
from numba import jit

def getWparameterFromOULUcountRate(OULUcountRateInSeconds:float):
    # equation take from Matthiä, Daniel, et al. "A ready-to-use galactic cosmic ray model."
    # Advances in Space Research 51.3 (2013): 329-338, https://doi.org/10.1016/j.asr.2012.09.022

    OULUmeanCountRateInMins = OULUcountRateInSeconds * 60

    #print("OULU mean count rate in seconds used is", OULUcountRateInSeconds)

    Wparameter = (-0.093 * OULUmeanCountRateInMins) + 638.7

    return Wparameter

#@jit(nopython=True)
def getModifiedISO_GCR_Flux_Default_Energies(W, Z):

    minEnergy = 10.0
    maxEnergy = 1.0E+6
    nbins = 50

    listOfEnergyBins = np.geomspace(minEnergy,maxEnergy,num=nbins+1)
    middleEnergies = (listOfEnergyBins[1:] + listOfEnergyBins[:-1])/2

    outputFluxArray = np.array([[energy,getModifiedISO_GCR_Flux_Single(W, Z, energy)] for energy in middleEnergies])

    return outputFluxArray

@jit(nopython=True)
def getModifiedISO_GCR_Flux_Single(W:float, Z:int, energy:float)->float:

    # ensuring correct inputs
    if ((W < 0) or (W > 200)):
            raise Exception("parameter W  not valid; range is 0<=W<=200")
    elif ((Z < 1) or (Z > 28)):
            raise Exception("atomic number Z not valid; range is 1<=Z<=28")
    elif(energy < 11.0):
            raise Exception("energy not valid; range is E>=10 MeV/n")
    else:

        #constants for the modified ISO model, which are empirical and taken from tabulated data. These constants are a function
        #of atomic number Z.
        AI = [1.,    4.0,  6.9,  9.0, 10.8, 12.0, 14.0, 16.0,19.0, 20.2, \
                23.0, 24.3, 27.0, 28.1, 31.0, 32.1, 35.4,39.9,39.1, 40.1, \
                44.9, 47.9, 50.9, 52.0, 54.9, 55.8, 58.9, 58.7]

        CI = [1.85E4, 3.69E3, 19.5, 17.7, 49.2, 103.0, 36.7,87.4, 3.19, 16.4,\
                4.4300, 19.300, 4.17, 13.4, 1.15, 3.060, 1.30,2.33, 1.87, 2.17, \
                0.74,    2.63,  1.23, 2.12, 1.14, 9.32, 0.10,0.48]

        gammaI = [2.74, 2.77, 2.82, 3.05, 2.96, 2.76, 2.89,2.70, 2.82, 2.76, \
                    2.84, 2.70, 2.77, 2.66, 2.89, 2.71, 3.00, 2.93,3.05, 2.77, \
                    2.97, 2.99, 2.94, 2.89, 2.74, 2.63, 2.63,2.63]

        alphaI = [2.85, 3.12, 3.41, 4.30, 3.93, 3.18, 3.77,3.11, 4.05, 3.11, \
                    3.14, 3.65, 3.46, 3.00, 4.04, 3.30, 4.40, 4.33,4.49, 2.93, \
                    3.78, 3.79, 3.50, 3.28, 3.29, 3.01, 4.25,3.52]

        #i = Z #This code was converted from C++, where i was used to displace Z by one to match with C-like arrays. I have left the variable i in, however as Fortran arrays begin at 1 not
        #      #0 unlike in C++, i here is equal to Z rather than Z-1
        i = Z - 1

        A = AI[i]
        restmass = 0.938
        if (Z>1):
            restmass = 0.939
        
        c = CI[i]
        alpha = alphaI[i]
        gamm = gammaI[i] #had to use gamm as the variable name here rather than gamma, as gamma is already used in Fortran

        #converting energy to the correct units
        x = 0.001 * energy

        #converting kinetic energy to rigidity
        rigidity = (A/Z*np.sqrt(x*(x+2*restmass)))

        #determining beta = (particle speed / speed of light) using relativistic equations
        beta = np.sqrt(x*(x+2*restmass))/(x+restmass)

        # ==============================================================================
        #       using the main modified ISO model equation to calculate the output flux
        # ==============================================================================
        R0 = (0.37+0.0003*(W**1.45))
        delta = 0.02*W+4.7
        phi = c*(beta**alpha)/(rigidity**gamm)*((rigidity/(rigidity+R0))**delta)

        outputFlux = 0.0001*phi*A/Z*0.001/beta

    return outputFlux

@jit(nopython=True)
def getAtomicMass(atomicNumber):

    A = [1.0,  4.0,  6.9,  9.0, 10.8, 12.0, 14.0, 16.0, 19.0, 20.2,\
       23.0, 24.3, 27.0, 28.1, 31.0, 32.1, 35.4, 39.9, 39.1, 40.1,\
       44.9, 47.9, 50.9, 52.0, 54.9, 55.8, 58.9, 58.7, 63.5, 65.4,\
       69.7, 72.6, 74.9, 79.0, 79.9, 83.8, 85.5, 87.6, 88.9, 91.2,\
       92.9, 95.9, 97.0,101.0,102.9,106.4,107.9,112.4,114.8,118.7,\
      121.8,127.6,126.9,131.3,132.9,137.3,138.9,140.1,140.9,144.2,\
      145.0,150.4,152.0,157.3,158.3,162.5,164.9,167.3,168.9,173.0,\
      175.0,178.5,180.9,183.9,186.2,190.2,192.2,195.1,197.0,200.6,\
      204.4,207.2,209.0,209.0,210.0,222.0,223.0,226.0,227.0,232.0,\
      231.0,238.0]

    if ( atomicNumber < 0 ):
        atomicMass = 1.0           # handle case for electron
    elif (atomicNumber <= 92):
        atomicMass = A[atomicNumber-1]       # look up table for other elements.
    else:
        atomicMass = 0.0           # just in case

    return atomicMass

if __name__ == "__main__":
    testW = 111.3
    testZ = 1
    defaultOutputFluxes = getModifiedISO_GCR_Flux_Default_Energies(testW, testZ)
    print("Success!")