from setuptools import find_packages, setup
import os

# get requirements for installation
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = [] # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(
    name='DLRISOmodel',
    packages=find_packages(),
    #packages=find_packages(where="DLRISOmodel"),
    #package_dir={"": "DLRISOmodel"},
    #package_dir={"":"."},
    package_data={"":["DLRISOmodel/neutronMonitorData/*.dat","DLRISOmodel/neutronMonitorData/*.pkl"]},
    include_package_data=True,
    version='0.1.1',
    description='Python library for running the DLR ISO cosmic ray model to get cosmic ray spectra',
    author='Me',
    license='MIT',
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
