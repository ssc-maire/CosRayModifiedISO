from CosRayModifiedISO import CosRayModifiedISO
import numpy as np
import pandas as pd
import datetime as dt
from CosRayModifiedISO.internalFunctions.pythonModifiedISO import getAtomicMass
from CosRayModifiedISO.internalFunctions.rigidityEnergyConversionFunctions import (
    convertParticleEnergyToRigidity,
    convertParticleRigiditySpecToEnergySpec,
    convertParticleRigidityToEnergy,
    convertPerNucleonEnergyToTotalRigidity,
)

def test_energy_flux_output():

    solarModulationWparameter = 19.25 # the solar modulation at a specific point in the solar cycle
    atomicNumber = 1 # the atomic number of the particle in question - in this case a proton/hydrogen ion, which has an atomic number of 1
    energyListInMeV = 945.2 # kinetic energy of particle in MeV

    outputEnergyFlux = CosRayModifiedISO.getEnergyFluxesFromEnergies(solarModulationWparameter, atomicNumber, energyListInMeV)

    assert round(outputEnergyFlux[0],7) == round(0.00012419,7)

def test_timestamp_flux_output_no_tzinfo():

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
    assert round(outputtedSpectralDataFrame["Rigidity (GV)"].iloc[0],5) == round(0.146022,5)
    assert round(outputtedSpectralDataFrame["Rigidity (GV)"].iloc[4],5) == round(0.232474,5)
    assert round(outputtedSpectralDataFrame["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[0],10) == round(2.290835e-07,10)
    assert round(outputtedSpectralDataFrame["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[4],10) == round(1.546788e-06,10)
    assert round(outputtedSpectralDataFrame["d_Flux / d_R (cm-2 s-1 sr-1 GV-1)"].iloc[0],8) == round(3.522790e-05,8)
    assert round(outputtedSpectralDataFrame["d_Flux / d_R (cm-2 s-1 sr-1 GV-1)"].iloc[4],8) == round(3.719962e-04,8)

def test_timestamp_flux_output():

    datetimeToUse = dt.datetime(
    year = 2001,
    month = 10,
    day = 27,
    hour = 0,
    minute = 10,
    second = 35,
    tzinfo = dt.timezone.utc
    )
    
    outputtedSpectralDataFrame = CosRayModifiedISO.getSpectrumUsingTimestamp(datetimeToUse,atomicNumber=1)

    assert round(outputtedSpectralDataFrame["Energy (MeV/n)"].iloc[0],5) == round(11.294627,5)
    assert round(outputtedSpectralDataFrame["Energy (MeV/n)"].iloc[4],5) == round(28.370820,5)
    assert round(outputtedSpectralDataFrame["Rigidity (GV)"].iloc[0],5) == round(0.146022,5)
    assert round(outputtedSpectralDataFrame["Rigidity (GV)"].iloc[4],5) == round(0.232474,5)
    assert round(outputtedSpectralDataFrame["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[0],10) == round(2.290835e-07,10)
    assert round(outputtedSpectralDataFrame["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[4],10) == round(1.546788e-06,10)
    assert round(outputtedSpectralDataFrame["d_Flux / d_R (cm-2 s-1 sr-1 GV-1)"].iloc[0],8) == round(3.522790e-05,8)
    assert round(outputtedSpectralDataFrame["d_Flux / d_R (cm-2 s-1 sr-1 GV-1)"].iloc[4],8) == round(3.719962e-04,8)


def test_spectrum_does_not_use_gv_per_nucleon_column_names():
    spectrum = CosRayModifiedISO.getSpectrumUsingSolarModulation(100.0, atomicNumber=1)
    assert "Rigidity (GV/n)" not in spectrum.columns
    assert "d_Flux / d_R (cm-2 s-1 sr-1 (GV/n)-1)" not in spectrum.columns
    assert list(spectrum.columns) == [
        "Energy (MeV/n)",
        "d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)",
        "Rigidity (GV)",
        "d_Flux / d_R (cm-2 s-1 sr-1 GV-1)",
    ]


def test_helium_rigidity_uses_total_kinetic_energy():
    spectrum = CosRayModifiedISO.getSpectrumUsingSolarModulation(100.0, atomicNumber=2)
    atomic_mass = getAtomicMass(2)
    energy_per_nucleon = spectrum["Energy (MeV/n)"]
    expected_total_rigidity = convertPerNucleonEnergyToTotalRigidity(
        energy_per_nucleon,
        particleMassAU=atomic_mass,
        particleChargeAU=2,
    )
    np.testing.assert_allclose(spectrum["Rigidity (GV)"], expected_total_rigidity, rtol=1e-10)

    incorrect_rigidity = convertParticleEnergyToRigidity(
        energy_per_nucleon,
        particleMassAU=atomic_mass,
        particleChargeAU=2,
    )
    assert not np.allclose(spectrum["Rigidity (GV)"], incorrect_rigidity, rtol=1e-2)
    assert np.all(spectrum["Rigidity (GV)"] > incorrect_rigidity)


def test_helium_rigidity_flux_matches_jacobian_from_energy_flux():
    spectrum = CosRayModifiedISO.getSpectrumUsingSolarModulation(100.0, atomicNumber=2)
    atomic_mass = getAtomicMass(2)
    index = 20
    energy_n = float(spectrum["Energy (MeV/n)"].iloc[index])
    flux_en = float(spectrum["d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)"].iloc[index])
    rigidity = float(spectrum["Rigidity (GV)"].iloc[index])
    flux_r = float(spectrum["d_Flux / d_R (cm-2 s-1 sr-1 GV-1)"].iloc[index])

    delta_r = rigidity * 1e-6
    energy_plus = float(
        convertParticleRigidityToEnergy(
            pd.Series([rigidity + delta_r]),
            particleMassAU=atomic_mass,
            particleChargeAU=2,
        ).iloc[0]
    ) / atomic_mass
    energy_minus = float(
        convertParticleRigidityToEnergy(
            pd.Series([rigidity - delta_r]),
            particleMassAU=atomic_mass,
            particleChargeAU=2,
        ).iloc[0]
    ) / atomic_mass
    d_energy_n_d_r = (energy_plus - energy_minus) / (2.0 * delta_r)
    expected_flux_r = flux_en * d_energy_n_d_r
    np.testing.assert_allclose(flux_r, expected_flux_r, rtol=1e-4)
    assert abs(energy_n - 0.5 * (energy_plus + energy_minus)) / energy_n < 1e-6


def test_get_rigidity_fluxes_uses_energy_per_nucleon_for_heavies():
    rigidity = 2.0
    atomic_number = 2
    atomic_mass = getAtomicMass(atomic_number)
    flux = CosRayModifiedISO.getRigidityFluxesFromRigidities(100.0, atomic_number, rigidity)

    energy_total = float(
        convertParticleRigidityToEnergy(
            pd.Series([rigidity]),
            particleMassAU=atomic_mass,
            particleChargeAU=atomic_number,
        ).iloc[0]
    )
    energy_per_nucleon = energy_total / atomic_mass
    energy_flux = CosRayModifiedISO.getEnergyFluxesFromEnergies(
        100.0, atomic_number, energy_per_nucleon
    )[0]
    spectrum = CosRayModifiedISO.getSpectrumUsingSolarModulation(100.0, atomic_number)
    interpolated = np.interp(
        rigidity,
        spectrum["Rigidity (GV)"].to_numpy(),
        spectrum["d_Flux / d_R (cm-2 s-1 sr-1 GV-1)"].to_numpy(),
    )
    np.testing.assert_allclose(flux[0], interpolated, rtol=5e-3)
    assert energy_per_nucleon < energy_total
    assert energy_flux > 0.0


def test_rigidity_to_energy_spectrum_uses_supplied_mass_and_charge():
    rigidity = pd.Series([1.0, 5.0])
    flux_r = pd.Series([1.0, 0.1])
    helium = convertParticleRigiditySpecToEnergySpec(
        rigidity, flux_r, particleMassAU=4.0, particleChargeAU=2
    )
    proton = convertParticleRigiditySpecToEnergySpec(
        rigidity, flux_r, particleMassAU=1.0, particleChargeAU=1
    )
    assert not np.allclose(helium.to_numpy(), proton.to_numpy())
    assert np.all(np.isfinite(helium))
    assert np.all(helium > 0.0)
