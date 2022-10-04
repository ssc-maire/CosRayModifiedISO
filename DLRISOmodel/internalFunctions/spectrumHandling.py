import os
import pickle as pkl
import subprocess

import pandas as pd

from DLRISOmodel.internalFunctions.pythonDLRISO import getAtomicMass, getDLRISO_GCR_Flux_Default_Energies, getWparameterFromOULUcountRate
from DLRISOmodel.internalFunctions.rigidityEnergyConversionFunctions import convertParticleEnergySpecToRigiditySpec, convertParticleEnergyToRigidity
from DLRISOmodel.internalFunctions.miscellaneous import homeDirectory

class rigiditySpectrum():

    def __init__(self):
        pass

    def __call__(self, x):
        return self.rigiditySpec(x)

class DLRmodelSpectrum(rigiditySpectrum):

    def __init__(self):
        pass
        # self.setCurrentOULUcountRateInSeconds(OULUcountRateInSeconds)
        # self.determineWparameterFromOULUcountRate()
        # self.acquireTheProtonSpectrum()
        

    def acquireTheProtonSpectrum(self):
        #self.acquireProtonSpectrumThroughTheFortranScript()
        self.acquireProtonSpectrumThroughThePythonModule()

        # self.rigiditySpec = interp1d(x=self._generatedSpectrumDF["Rigidity"],
        #                                                 y=self._generatedSpectrumDF["FluxInRigidityGVForm"],
        #                                                 kind="linear",
        #                                                 bounds_error=False,
        #                                                 fill_value = (0.0,0.0))

        with open("DLRsavedSpectrum.pkl","wb") as DLRspecFile:
            pkl.dump(self,DLRspecFile)

    def setCurrentOULUcountRateInSeconds(self,OULUcountRateInSeconds):
        self._OULUcountRateInSeconds = OULUcountRateInSeconds

    def determineWparameterFromOULUcountRate(self):

        # # equation take from enginePythonScripts.Matthiä, Daniel, et al. "A ready-to-use galactic cosmic ray model."
        # # Advances in Space Research 51.3 (2013): 329-338, https://doi.org/10.1016/j.asr.2012.09.022

        # OULUmeanCountRateInMins = self._OULUcountRateInSeconds * 60

        # print("OULU mean count rate in seconds used is", self._OULUcountRateInSeconds)

        # self._Wparameter = (-0.093 * OULUmeanCountRateInMins) + 638.7

        # return self._Wparameter

        self._Wparameter = getWparameterFromOULUcountRate(self._OULUcountRateInSeconds)

        return self._Wparameter
    
    def acquireProtonSpectrumThroughTheFortranScript(self):

        atomicNumber = 1

        cmd = [
            (homeDirectory) + "/FortranDLRexe/" + "getDLRGCRFlux",
            str(int(atomicNumber)),
            str(self._Wparameter),
        ]

        subprocess.run(cmd)

        ### reading in the program output
        # energy is in units of MeV/n, flux is in units of particles cm-2 s-1 sr-1 (MeV/n)-1
        generatedSpectrumFilePath = "dlr_gcr.dat"
        generatedSpectrumDF = pd.read_csv(generatedSpectrumFilePath, header=None, sep="\s+")
        generatedSpectrumDF.columns = ["Energy", "FluxInEnergyMeVform"]
        os.remove(generatedSpectrumFilePath)

        generatedSpectrumDF["Rigidity"] = convertParticleEnergyToRigidity(generatedSpectrumDF["Energy"], 
                                                                        particleMassAU = 1, particleChargeAU = 1)
        generatedSpectrumDF["FluxInRigidityGVForm"] = convertParticleEnergySpecToRigiditySpec(generatedSpectrumDF["Energy"],
                                                                                            generatedSpectrumDF["FluxInEnergyMeVform"], 
                                                                                            particleMassAU = 1, particleChargeAU = 1) #cm-2 s-1 sr-1 (GV/n)-1

        self._generatedSpectrumDF = generatedSpectrumDF

        return generatedSpectrumDF

    def acquireProtonSpectrumThroughThePythonModule(self):

        atomicNumber = self._atomicNumber

        ### reading in the program output
        # energy is in units of MeV/n, flux is in units of particles cm-2 s-1 sr-1 (MeV/n)-1

        energyAndfluxArray = getDLRISO_GCR_Flux_Default_Energies(self._Wparameter, atomicNumber)
        generatedSpectrumDF = pd.DataFrame(energyAndfluxArray)

        generatedSpectrumDF.columns = ["Energy", "FluxInEnergyMeVform"]
        generatedSpectrumDF["Rigidity"] = convertParticleEnergyToRigidity(generatedSpectrumDF["Energy"], 
                                                                        particleMassAU = getAtomicMass(atomicNumber), particleChargeAU = atomicNumber)
        generatedSpectrumDF["FluxInRigidityGVForm"] = convertParticleEnergySpecToRigiditySpec(generatedSpectrumDF["Energy"],
                                                                                            generatedSpectrumDF["FluxInEnergyMeVform"], 
                                                                                            particleMassAU = getAtomicMass(atomicNumber), particleChargeAU = atomicNumber) #cm-2 s-1 sr-1 (GV/n)-1
        self._generatedSpectrumDF = generatedSpectrumDF

        return generatedSpectrumDF

class DLRmodelSpectrum_fromOULU(DLRmodelSpectrum):

    def __init__(self, OULUcountRateInSeconds, atomicNumber):
        self.setCurrentOULUcountRateInSeconds(OULUcountRateInSeconds)
        self.determineWparameterFromOULUcountRate()
        self._atomicNumber = atomicNumber
        self.acquireTheProtonSpectrum()

class DLRmodelSpectrum_fromSolarModulation(DLRmodelSpectrum):

    def __init__(self, solarModulationWparameter, atomicNumber):
        self._Wparameter = solarModulationWparameter
        self._atomicNumber = atomicNumber
        self.acquireTheProtonSpectrum()