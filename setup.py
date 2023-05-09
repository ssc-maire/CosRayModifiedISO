from setuptools import find_packages, setup
from pathlib import Path
import os

# get requirements for installation
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='CosRayModifiedISO',
    packages=find_packages(),
    package_data={"":["CosRayModifiedISO/neutronMonitorData/*.dat","CosRayModifiedISO/neutronMonitorData/*.pkl"]},
    include_package_data=True,
    version='1.2',
    url="https://github.com/ssc-maire/CosRayModifiedISO",
    author='Chris S. W. Davis',
    author_email='ChrisSWDavis@gmail.com',
    license='MIT',
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    description='A Python library for acquiring galactic cosmic ray spectra at Earth from the ISO model as modified by DLR. All the details and equations about this model can be found in Matthiae et al., A ready-to-use galactic cosmic ray model, Advances in Space Research 51.3 (2013): 329-338, https://doi.org/10.1016/j.asr.2012.09.022 .',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
