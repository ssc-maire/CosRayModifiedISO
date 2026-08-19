import numpy as np
import pandas as pd
import decimal as dec

dec.getcontext().prec = 100

protonRestMass = dec.Decimal(1.67262192e-27)  #kg
chargeOfElectron = dec.Decimal(1.60217663e-19) #C
c = dec.Decimal(299792458.0) #m/s

def determineParticleAttributes(particleMassAU, particleChargeAU):
    m0 = dec.Decimal(particleMassAU) * protonRestMass #kg
    particleCharge = dec.Decimal(particleChargeAU) * chargeOfElectron #C
    particleRestEnergy = m0 * (c**2)
    return particleCharge,particleRestEnergy


def _as_energy_series(particleKineticEnergyInMeV):
    if isinstance(particleKineticEnergyInMeV, pd.Series):
        return particleKineticEnergyInMeV
    return pd.Series(particleKineticEnergyInMeV)


def convertPerNucleonEnergyToTotalRigidity(
    energyPerNucleonMeV,
    particleMassAU=1,
    particleChargeAU=1,
):
    """Convert kinetic energy per nucleon (MeV/n) to total rigidity (GV).

    ``convertParticleEnergyToRigidity`` expects total kinetic energy in MeV.
    """
    energy_per_nucleon = _as_energy_series(energyPerNucleonMeV)
    energy_total_MeV = energy_per_nucleon * particleMassAU
    return convertParticleEnergyToRigidity(
        energy_total_MeV,
        particleMassAU=particleMassAU,
        particleChargeAU=particleChargeAU,
    )


def convertPerNucleonEnergySpecToTotalRigiditySpec(
    energyPerNucleonMeV,
    fluxPerMeVPerNucleon,
    particleMassAU=1,
    particleChargeAU=1,
):
    """Convert a per-nucleon energy spectrum to a total-rigidity spectrum.

    If ``j_En`` is in (cm-2 s-1 sr-1 (MeV/n)-1) and ``R`` is total GV, then
    ``j_R = j_En * d(E/n)/dR = (j_En / A) * d(E_tot)/dR``.
    """
    energy_per_nucleon = _as_energy_series(energyPerNucleonMeV)
    flux_per_mev_n = _as_energy_series(fluxPerMeVPerNucleon)
    energy_total_MeV = energy_per_nucleon * particleMassAU
    flux_for_total_jacobian = flux_per_mev_n / particleMassAU
    return convertParticleEnergySpecToRigiditySpec(
        energy_total_MeV,
        flux_for_total_jacobian,
        particleMassAU=particleMassAU,
        particleChargeAU=particleChargeAU,
    )


def convertParticleEnergyToRigidity(particleKineticEnergyInMeV:pd.Series, particleMassAU = 1, particleChargeAU = 1):
    """Convert total kinetic energy (MeV) to total rigidity (GV)."""

    particleCharge, particleRestEnergy = determineParticleAttributes(particleMassAU, particleChargeAU)

    particleKineticEnergyInJoules = particleKineticEnergyInMeV.apply(dec.Decimal) * chargeOfElectron * dec.Decimal(1e6)

    totalParticleEnergy = particleKineticEnergyInJoules + particleRestEnergy
    pc = np.sqrt((totalParticleEnergy**2) - (particleRestEnergy**2))

    #rigidity = pc / particleCharge

    rigidityInGV = (pc / particleCharge) * dec.Decimal(1e-9)

    return rigidityInGV.apply(float)

def convertParticleRigidityToEnergy(particleRigidityInGV:pd.Series, particleMassAU = 1, particleChargeAU = 1):
    """Convert total rigidity (GV) to total kinetic energy (MeV)."""

    particleCharge, particleRestEnergy = determineParticleAttributes(particleMassAU, particleChargeAU)

    pc = particleRigidityInGV.apply(dec.Decimal) * particleCharge * dec.Decimal(1e9)

    totalParticleEnergy = np.sqrt((pc**2) + (particleRestEnergy**2))

    particleKEinJoules = totalParticleEnergy - particleRestEnergy

    KEinMeV = particleKEinJoules / (chargeOfElectron * dec.Decimal(1e6))

    return KEinMeV.apply(float)

def calculate_dKEoverdR(particleKineticEnergyInMeV, particleCharge, particleRestEnergy):
    particleKineticEnergyInJoules = particleKineticEnergyInMeV.apply(dec.Decimal) * chargeOfElectron * dec.Decimal(1e6)

    totalParticleEnergy = particleKineticEnergyInJoules + particleRestEnergy
    pc = np.sqrt((totalParticleEnergy**2) - (particleRestEnergy**2))

    #fullFactor = pc/particleKineticEnergyInJoules
    fullFactor = pc/totalParticleEnergy

    dKEInMeV_drigidityInGV = fullFactor * particleCharge * dec.Decimal(1e9) / (chargeOfElectron * dec.Decimal(1e6))
    return dKEInMeV_drigidityInGV

def convertParticleEnergySpecToRigiditySpec(particleKineticEnergyInMeV:pd.Series, fluxInEnergyMeVform:pd.Series, particleMassAU = 1, particleChargeAU = 1):
    """Convert dJ/dE (per total MeV) to dJ/dR (per total GV)."""

    particleCharge, particleRestEnergy = determineParticleAttributes(particleMassAU, particleChargeAU)

    dKEInMeV_drigidityInGV = calculate_dKEoverdR(particleKineticEnergyInMeV, particleCharge, particleRestEnergy)

    return (dKEInMeV_drigidityInGV * fluxInEnergyMeVform.apply(dec.Decimal)).apply(float)

def convertParticleRigiditySpecToEnergySpec(particleRigidityInGV:pd.Series, fluxInRigidityGVform:pd.Series, particleMassAU = 1, particleChargeAU = 1):
    """Convert dJ/dR (per total GV) to dJ/dE (per total MeV)."""

    particleCharge, particleRestEnergy = determineParticleAttributes(particleMassAU, particleChargeAU)

    particleKineticEnergyInMeV = convertParticleRigidityToEnergy(
        particleRigidityInGV,
        particleMassAU=particleMassAU,
        particleChargeAU=particleChargeAU,
    ).apply(dec.Decimal)

    dKEInMeV_drigidityInGV = calculate_dKEoverdR(particleKineticEnergyInMeV, particleCharge, particleRestEnergy)

    return (fluxInRigidityGVform.apply(dec.Decimal) / dKEInMeV_drigidityInGV).apply(float)
