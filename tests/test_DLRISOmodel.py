from CosRayModifiedISO import CosRayModifiedISO
import numpy as np
import datetime as dt

def test_energy_flux_output():

    solarModulationWparameter = 19.25 # the solar modulation at a specific point in the solar cycle
    atomicNumber = 1 # the atomic number of the particle in question - in this case a proton/hydrogen ion, which has an atomic number of 1
    energyListInMeV = 945.2 # kinetic energy of particle in MeV

    outputEnergyFlux = CosRayModifiedISO.getEnergyFluxesFromEnergies(solarModulationWparameter, atomicNumber, energyListInMeV)

    assert round(outputEnergyFlux[0],7) == round(0.00012419,7)

def test_timestamp_flux_output():

    datetimeToUse = dt.datetime(
    year = 2001,
    month = 10,
    day = 27,
    hour = 0,
    minute = 10,
    second = 35
    )
    
    outputtedSpectralDataFrame = CosRayModifiedISO.getSpectrumUsingTimestamp(datetimeToUse,atomicNumber=1)

    assert round(outputtedSpectralDataFrame["Energy (MeV/n)"].iloc[0],5) == round(11.294627,5)
    assert round(outputtedSpectralDataFrame["Energy (MeV/n)"].iloc[4],5) == round(28.370820,5)
    assert round(outputtedSpectralDataFrame["Rigidity (GV/n)"].iloc[0],5) == round(0.146022,5)
    assert round(outputtedSpectralDataFrame["Rigidity (GV/n)"].iloc[4],5) == round(0.232474,5)
    assert round(outputtedSpectralDataFrame["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[0],10) == round(2.290835e-07,10)
    assert round(outputtedSpectralDataFrame["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[4],10) == round(1.546788e-06,10)
    assert round(outputtedSpectralDataFrame["d_Flux / d_R (cm-2 s-1 sr-1 (GV/n)-1)"].iloc[0],8) == round(3.522790e-05,8)
    assert round(outputtedSpectralDataFrame["d_Flux / d_R (cm-2 s-1 sr-1 (GV/n)-1)"].iloc[4],8) == round(3.719962e-04,8)