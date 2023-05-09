#!/bin/python3

import numpy as np
import pandas as pd
import datetime as dt
from CosRayModifiedISO.internalFunctions.importingNMdata import getOULUcountRateForTimestamp

from CosRayModifiedISO.internalFunctions.miscellaneous import convertToIterable
from CosRayModifiedISO.internalFunctions.pythonModifiedISO import getAtomicMass, getModifiedISO_GCR_Flux_Single, getWparameterFromOULUcountRate
from CosRayModifiedISO.internalFunctions.rigidityEnergyConversionFunctions import convertParticleEnergySpecToRigiditySpec, convertParticleRigiditySpecToEnergySpec, convertParticleRigidityToEnergy, convertParticleEnergyToRigidity
from CosRayModifiedISO.internalFunctions.spectrumHandling import ISOmodelSpectrum_fromSolarModulation

def getEnergyFluxesFromEnergies(solarModulationWparameter:float, atomicNumber:int, energyListInMeV:list):

    energyListInMeV = convertToIterable(energyListInMeV)

    return np.array([getModifiedISO_GCR_Flux_Single(solarModulationWparameter, atomicNumber, energy) for energy in energyListInMeV])

def getRigidityFluxesFromRigidities(solarModulationWparameter:float, atomicNumber:int, rigidityListInGV:list):

    rigidityListInGV = convertToIterable(rigidityListInGV)

    energyListInMeV = convertParticleRigidityToEnergy(particleRigidityInGV = pd.Series(rigidityListInGV), 
                                                      particleMassAU = getAtomicMass(atomicNumber), 
                                                      particleChargeAU = atomicNumber)

    energyFluxes = getEnergyFluxesFromEnergies(solarModulationWparameter, atomicNumber, energyListInMeV)

    rigidityFluxes = convertParticleEnergySpecToRigiditySpec(particleKineticEnergyInMeV = pd.Series(energyListInMeV), 
                                                             fluxInEnergyMeVform = pd.Series(energyFluxes), 
                                                             particleMassAU = getAtomicMass(atomicNumber), 
                                                             particleChargeAU = atomicNumber)

    return np.array(rigidityFluxes)

def getSpectrumUsingSolarModulation(solarModulationWparameter:float, atomicNumber:int):
    generalSpectrum = ISOmodelSpectrum_fromSolarModulation(solarModulationWparameter, atomicNumber)
    outputDF = generalSpectrum._generatedSpectrumDF
    outputDF.columns = ["Energy (MeV/n)", 
                        "d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)",
                        "Rigidity (GV/n)",
                        "d_Flux / d_R (cm-2 s-1 sr-1 (GV/n)-1)"]
    return outputDF

def getSpectrumUsingOULUcountRate(OULUcountRatePerSecond:float, atomicNumber:int):
    solarModulationWparameter = getWparameterFromOULUcountRate(OULUcountRatePerSecond)
    outputDF = getSpectrumUsingSolarModulation(solarModulationWparameter, atomicNumber)
    return outputDF

getSpectrumUsingSSN = getSpectrumUsingSolarModulation

getOULUcountRateForTimestamp = getOULUcountRateForTimestamp

getWparameterFromOULUcountRate = getWparameterFromOULUcountRate

getModifiedISO_GCR_Flux_Single = getModifiedISO_GCR_Flux_Single

def getSpectrumUsingTimestamp(timestamp:dt.datetime, atomicNumber:int):

    OULUcountRate = getOULUcountRateForTimestamp(timestamp)
    Wparameter = getWparameterFromOULUcountRate(OULUcountRate)
    return getSpectrumUsingSolarModulation(Wparameter, atomicNumber)

if __name__ == "__main__":
    #getSpectrumUsingOULUcountRate(89.7,atomicNumber=1)
    print(getSpectrumUsingTimestamp(dt.datetime(year=1989,month=10,day=27),atomicNumber=1))
    print(getSpectrumUsingTimestamp(dt.datetime(year=2000,month=10,day=27),atomicNumber=1))
    print(getSpectrumUsingTimestamp(dt.datetime(year=2000,month=10,day=27),atomicNumber=7))
    print(getRigidityFluxesFromRigidities(20.7, 1, 100))
