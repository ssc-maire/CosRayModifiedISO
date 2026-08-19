#!/bin/python3

import numpy as np
import pandas as pd
import datetime as dt
from CosRayModifiedISO.internalFunctions.importingNMdata import getOULUcountRateForTimestamp

from CosRayModifiedISO.internalFunctions.miscellaneous import convertToIterable
from CosRayModifiedISO.internalFunctions.pythonModifiedISO import getAtomicMass, getModifiedISO_GCR_Flux_Single, getWparameterFromOULUcountRate
from CosRayModifiedISO.internalFunctions.rigidityEnergyConversionFunctions import (
    convertParticleEnergySpecToRigiditySpec,
    convertParticleRigiditySpecToEnergySpec,
    convertParticleRigidityToEnergy,
    convertParticleEnergyToRigidity,
    convertPerNucleonEnergySpecToTotalRigiditySpec,
    convertPerNucleonEnergyToTotalRigidity,
)
from CosRayModifiedISO.internalFunctions.spectrumHandling import ISOmodelSpectrum_fromSolarModulation

import logging

logging.basicConfig(level=logging.WARNING)

def getEnergyFluxesFromEnergies(solarModulationWparameter:float, atomicNumber:int, energyListInMeV:list):
    """Differential energy flux at kinetic energies per nucleon (MeV/n).

    Returns values in cm-2 s-1 sr-1 (MeV/n)-1.
    """

    energyListInMeV = convertToIterable(energyListInMeV)

    return np.array([getModifiedISO_GCR_Flux_Single(solarModulationWparameter, atomicNumber, energy) for energy in energyListInMeV])

def getRigidityFluxesFromRigidities(solarModulationWparameter:float, atomicNumber:int, rigidityListInGV:list):
    """Differential rigidity flux at total rigidities (GV).

    ``rigidityListInGV`` is total rigidity pc/Ze. The Matthiä model is evaluated
    at the corresponding kinetic energy per nucleon.
    Returns values in cm-2 s-1 sr-1 GV-1.
    """

    rigidityListInGV = convertToIterable(rigidityListInGV)
    atomic_mass = getAtomicMass(atomicNumber)

    energyTotalMeV = convertParticleRigidityToEnergy(
        particleRigidityInGV=pd.Series(rigidityListInGV),
        particleMassAU=atomic_mass,
        particleChargeAU=atomicNumber,
    )
    energyPerNucleonMeV = energyTotalMeV / atomic_mass

    energyFluxes = getEnergyFluxesFromEnergies(
        solarModulationWparameter, atomicNumber, energyPerNucleonMeV
    )

    rigidityFluxes = convertPerNucleonEnergySpecToTotalRigiditySpec(
        energyPerNucleonMeV,
        pd.Series(energyFluxes),
        particleMassAU=atomic_mass,
        particleChargeAU=atomicNumber,
    )

    return np.array(rigidityFluxes)

def getSpectrumUsingSolarModulation(solarModulationWparameter:float, atomicNumber:int):
    generalSpectrum = ISOmodelSpectrum_fromSolarModulation(solarModulationWparameter, atomicNumber)
    outputDF = generalSpectrum._generatedSpectrumDF
    outputDF.columns = [
        "Energy (MeV/n)",
        "d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)",
        "Rigidity (GV)",
        "d_Flux / d_R (cm-2 s-1 sr-1 GV-1)",
    ]
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

    if timestamp.tzinfo is None:
        logging.warning("The inputted timestamp does not have timezone info. Assuming UTC.")
        timestamp = timestamp.replace(tzinfo=dt.timezone.utc)

    OULUcountRate = getOULUcountRateForTimestamp(timestamp)
    Wparameter = getWparameterFromOULUcountRate(OULUcountRate)
    return getSpectrumUsingSolarModulation(Wparameter, atomicNumber)

if __name__ == "__main__":
    #getSpectrumUsingOULUcountRate(89.7,atomicNumber=1)
    print(getSpectrumUsingTimestamp(dt.datetime(year=1989,month=10,day=27),atomicNumber=1))
    print(getSpectrumUsingTimestamp(dt.datetime(year=2000,month=10,day=27),atomicNumber=1))
    print(getSpectrumUsingTimestamp(dt.datetime(year=2000,month=10,day=27),atomicNumber=7))
    print(getRigidityFluxesFromRigidities(20.7, 1, 100))
