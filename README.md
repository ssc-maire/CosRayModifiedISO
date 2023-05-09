# CosRayModifiedISO

A simple library for running the ISO galactic cosmic ray spectrum model as modified by DLR. 

All the details and equations about this model can be found in Matthiä et al., 
"A ready-to-use galactic cosmic ray model", Advances in Space Research 51.3 (2013): 329-338, https://doi.org/10.1016/j.asr.2012.09.022 . This model only requires
a single parameter, *W*, which describes the modulation of the Sun at a given date and time, to calculate the flux of cosmic rays hitting Earth.
    
# Installation

You can either install directly from PyPi using

```
pip install CosRayModifiedISO
```

Or clone CosRayModifiedISO from https://github.com/ssc-maire/CosRayModifiedISO, and then from the cloned directory, run

```
sudo python setup.py install
```

# Usage

to import this module, use

```
from CosRayModifiedISO import CosRayModifiedISO
```

unless otherwise stated, all of the quantities specified in this library use the following units:
* Energies are always in units of **MeV**
* Rigidities are always in units of **GV**
* Differential energy fluxes are always in units of **cts / cm<sup>2</sup> / s / sr / (MeV/n)**
* Differential rigidity fluxes are always in units of **cts / cm<sup>2</sup> / s / sr / (GV/n)**

It should be noted that in the field of space radiation, "energy" is frequently generally used specifically as a shorthand for "kinetic energy" rather than 
the total energy of a particle (rest mass energy + kinetic energy), and all references to "energy" in this library should be assumed to be kinetic energy
unless otherwise specified.

All users should be always be careful to remember which differential flux type they are using for their application, as differential 
energy flux and differential rigidity flux are different quantities which have a non-linear conversion between them. In general, differential
energy flux should always be used when working with energies, and differential rigidity flux should be used when working with particle rigidities.
If you're trying to create something like a particle 'kinetic energy spectrum' for instance, you should use particle kinetic energy on the x-axis, and the differential
energy flux on the y-axis (here using energy as a shorthand for kinetic energy).

Unit description:

| Symbol      | name |
| ----------- | ----------- |
| cm      | centimeter       |
| s   | seconds        |
| sr  | steradian |
| MeV    | Megaelectronvolts |
| GV | Gigavolts |
| n | nucleons |

## Single differential flux values and ranges of differential flux values

to get a single differential flux value for a particle value of solar modulation, and for a particular particle with a given atomic number and kinetic energy 
(or range of kinetic energies), the appropriate method for `CosRayModifiedISO` is
```
CosRayModifiedISO.getEnergyFluxesFromEnergies(solarModulationWparameter, atomicNumber, energyListInMeV)
```

For example, the script
```
from CosRayModifiedISO import CosRayModifiedISO

solarModulationWparameter = 19.25 # the solar modulation at a specific point in the solar cycle
atomicNumber = 1 # the atomic number of the particle in question - in this case a proton/hydrogen ion, which has an atomic number of 1
energyListInMeV = 945.2 # kinetic energy of particle in MeV

print(CosRayModifiedISO.getEnergyFluxesFromEnergies(solarModulationWparameter, atomicNumber, energyListInMeV))
```
gives
```
[0.00012419]
```
as output.

The argument `energyListInMeV` can be supplied as either a single float or as a list of floats to give either a single differential flux as output, 
or a range of differential fluxes corresponding to each supplied kinetic energy.

If you instead want to acquire differential rigidity fluxes rather than differential energy fluxes, you can use
```
CosRayModifiedISO.getRigidityFluxesFromRigidities(solarModulationWparameter, atomicNumber, rigidityListInGV)
```
which has exactly the same syntax and usage as the `getEnergyFluxesFromEnergies` method, but where rigidities in GV must be supplied instead 
of kinetic energies in MeV.

## Outputting full particle spectra from a date and time, from neutron monitor data, or from the solar modulation.

Instead of directly needing to input the solar modulation and required kinetic energies or rigidities for each calculation, methods are available to return 
differential fluxes automatically based on neutron monitor data and a default set of kinetic energies designed to cover a range corresponding to particles 
that are relevant specifically for radiation dose rate calculations in Earth's atmosphere.

The method
```
CosRayModifiedISO.getSpectrumUsingTimestamp(timestamp, atomicNumber)
```
method can be used to output the differential fluxes for a given date and time, for example,

```
from CosRayModifiedISO import CosRayModifiedISO
import datetime as dt

datetimeToUse = dt.datetime(
  year = 2001,
  month = 10,
  day = 27,
  hour = 0,
  minute = 10,
  second = 35
  )
  
print(CosRayModifiedISO.getSpectrumUsingTimestamp(datetimeToUse,atomicNumber=1))
```
returns the output
```
    Energy (MeV/n)  d_Flux / d_E (cm-2 s-1 sr-1 (MeV/n)-1)  Rigidity (GV/n)  d_Flux / d_R (cm-2 s-1 sr-1 (GV/n)-1)
0        11.294627                            2.290835e-07         0.146022                           3.522790e-05
1        14.219093                            3.785376e-07         0.163966                           6.516322e-05
2        17.900778                            6.157642e-07         0.184152                           1.185919e-04
3        22.535744                            9.848618e-07         0.206875                           2.120539e-04
4        28.370820                            1.546788e-06         0.232474                           3.719962e-04
...
```
`getSpectrumUsingTimestamp` returns output in the form of a [Pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

This method uses historic values from the [OULU neutron monitor](https://cosmicrays.oulu.fi/) to determine values of solar modulation for input into 
the model, using the method described in [Matthiä et al., (2013)](https://doi.org/10.1016/j.asr.2012.09.022). Currently only dates between 1964/04/01 00:00 
and 2021/01/31 00:00 can be used.

Count rates from the OULU neutron monitor (or representative values) can be supplied directly into the model using the
```
CosRayModifiedISO.getSpectrumUsingOULUcountRate(OULUcountRatePerSecond, atomicNumber)
```
method, where `OULUcountRatePerSecond` is a single float representing the count rate per second of the OULU neutron monitor at a given instance of time. 
The solar modulation parameter can also be supplied directly using
```
CosRayModifiedISO.getSpectrumUsingSolarModulation(solarModulationWparameter, atomicNumber)
```
This function can be identically supplied with the monthly averaged sunspot number instead of the solar modulation parameter, which the solar modulation parameter
is essentially a proxy for. Alternatively the identical function 

```
CosRayModifiedISO.getSpectrumUsingSSN(sunspotNumber, atomicNumber)
```  
can be used instead for code understandability.

Each of these three methods output Pandas DataFrames in the same format as outputted by `getSpectrumUsingTimestamp`. The value of the solar modulation parameter
as a function of OULU neutron monitor monitor count rate can also be outputted by running

```
CosRayModifiedISO.getWparameterFromOULUcountRate(OULUcountRateInSeconds)
```

# Quantity Conversion Functions

In addition to the above spectrum calculation methods, there are also several methods for performing conversion between different quantities for input and output.

The methods
```
CosRayModifiedISO.convertParticleRigidityToEnergy(particleRigidityInGV, 
                                            particleMassAU, 
                                            particleChargeAU)
```
and
```
CosRayModifiedISO.convertParticleRigidityToEnergy(particleRigidityInGV, 
                                            particleMassAU, 
                                            particleChargeAU)
```
can be used to convert particle rigidities to kinetic energies and vice versa, respectively. Currently particle rigidities and energy *must* be supplied 
as [Pandas Series objects](https://pandas.pydata.org/docs/reference/api/pandas.Series.html). Particle masses and charges here must be inputted as single numbers
and in atomic units.

The methods
```
CosRayModifiedISO.convertParticleRigiditySpecToEnergySpec(particleRigidityInGV, 
                                                    fluxInRigidityGVform, 
                                                    particleMassAU, 
                                                    particleChargeAU)
```
and
```
CosRayModifiedISO.convertParticleEnergySpecToRigiditySpec(particleKineticEnergyInMeV, 
                                                    fluxInEnergyMeVform, 
                                                    particleMassAU, 
                                                    particleChargeAU)
```
can be used to convert differential rigidity flux to differential energy flux and vice versa, respectively. Both the particle rigidity values and their 
respective differential flux values must be inputted as [Pandas Series objects](https://pandas.pydata.org/docs/reference/api/pandas.Series.html).

The particle mass for all of these methods can be acquired directly from atomic number using
```
CosRayModifiedISO.getAtomicMass(atomicNumber)
```

# Acknowledgments

Thank you to Daniel Matthiä and others at DLR for allowing us to test their model initially using their own scripts. 

This package contains and for certain functions uses data from the OULU neutron monitor, as acquired from https://www.nmdb.eu/ , where data can also be found at https://cosmicrays.oulu.fi/ . We therefore acknowledge the NMDB database www.nmdb.eu, founded under the European Union's FP7 programme (contract no. 213007) for providing data. 





