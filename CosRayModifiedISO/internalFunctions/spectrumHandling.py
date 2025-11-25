import pandas as pd
import numpy as np
from CosRayModifiedISO.internalFunctions.pythonModifiedISO import getAtomicMass, getModifiedISO_GCR_Flux_Default_Energies, getWparameterFromOULUcountRate, getModifiedISO_GCR_Flux_Time_Series_Custom_Energies
from CosRayModifiedISO.internalFunctions.rigidityEnergyConversionFunctions import convertParticleEnergySpecToRigiditySpec, convertParticleEnergyToRigidity


class rigiditySpectrum():

    def __init__(self):
        pass

    def __call__(self, x):
        return self.rigiditySpec(x)


class modifiedISOmodelSpectrum(rigiditySpectrum):

    def __init__(self):
        pass

    def acquireTheProtonSpectrum(self):
        self.acquireProtonSpectrumThroughThePythonModule()

    def setCurrentOULUcountRateInSeconds(self, OULUcountRateInSeconds):
        self._OULUcountRateInSeconds = OULUcountRateInSeconds

    def determineWparameterFromOULUcountRate(self):

        # # equation take from enginePythonScripts.Matthiä, Daniel, et al. "A ready-to-use galactic cosmic ray model."
        # # Advances in Space Research 51.3 (2013): 329-338, https://doi.org/10.1016/j.asr.2012.09.022

        self._Wparameter = getWparameterFromOULUcountRate(
            self._OULUcountRateInSeconds)

        return self._Wparameter

    def acquireProtonSpectrumThroughThePythonModule(self):

        atomicNumber = self._atomicNumber

        # reading in the program output
        # energy is in units of MeV/n, flux is in units of particles cm-2 s-1 sr-1 (MeV/n)-1

        energyAndfluxArray = getModifiedISO_GCR_Flux_Default_Energies(
            self._Wparameter, atomicNumber)
        generatedSpectrumDF = pd.DataFrame(energyAndfluxArray)

        generatedSpectrumDF.columns = ["Energy", "FluxInEnergyMeVform"]
        generatedSpectrumDF["Rigidity"] = convertParticleEnergyToRigidity(generatedSpectrumDF["Energy"],
                                                                          particleMassAU=getAtomicMass(atomicNumber), particleChargeAU=atomicNumber)
        generatedSpectrumDF["FluxInRigidityGVForm"] = convertParticleEnergySpecToRigiditySpec(generatedSpectrumDF["Energy"],
                                                                                              generatedSpectrumDF[
                                                                                                  "FluxInEnergyMeVform"],
                                                                                              particleMassAU=getAtomicMass(atomicNumber), particleChargeAU=atomicNumber)  # cm-2 s-1 sr-1 (GV/n)-1
        self._generatedSpectrumDF = generatedSpectrumDF

        return generatedSpectrumDF


class modifiedISOmodelSpectrum_fromOULU(modifiedISOmodelSpectrum):

    def __init__(self, OULUcountRateInSeconds, atomicNumber):
        self.setCurrentOULUcountRateInSeconds(OULUcountRateInSeconds)
        self.determineWparameterFromOULUcountRate()
        self._atomicNumber = atomicNumber
        self.acquireTheProtonSpectrum()


class ISOmodelSpectrum_fromSolarModulation(modifiedISOmodelSpectrum):

    def __init__(self, solarModulationWparameter, atomicNumber):
        self._Wparameter = solarModulationWparameter
        self._atomicNumber = atomicNumber
        self.acquireTheProtonSpectrum()


class modifiedISOmodelSpectrumFromTimeSeries():

    def __init__(self, solarModulationWparameterTimeSeries, atomicNumber, energy_bin_edges=None):
        self._WparameterTimeSeries = solarModulationWparameterTimeSeries
        self._atomicNumber = atomicNumber
        if energy_bin_edges is None:
            self._energy_bin_edges = np.geomspace(10, 1e6, 51)
        else:
            self._energy_bin_edges = energy_bin_edges
        self.energy_mid_points, self.flux_array = self.generateSpectrum()
        return

    def generateSpectrum(self):
        energy_mid_points, flux_mat = getModifiedISO_GCR_Flux_Time_Series_Custom_Energies(
            self._WparameterTimeSeries, self._atomicNumber, self._energy_bin_edges)
        return energy_mid_points, flux_mat
