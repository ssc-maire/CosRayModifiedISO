from CosRayModifiedISO.CosRayModifiedISO import getRigidityFluxesFromRigidities, getSpectrumUsingTimestamp
import datetime as dt

print(getSpectrumUsingTimestamp(dt.datetime(year=1989,month=10,day=27),atomicNumber=1))
print(getSpectrumUsingTimestamp(dt.datetime(year=2000,month=10,day=27),atomicNumber=1))
print(getSpectrumUsingTimestamp(dt.datetime(year=2000,month=10,day=27),atomicNumber=7))
print(getRigidityFluxesFromRigidities(20.7, 1, 100))