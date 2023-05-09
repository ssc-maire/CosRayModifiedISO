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
    version='1.0',
    url="https://github.com/ssc-maire/CosRayModifiedISO",
    author='Chris S. W. Davis',
    author_email='ChrisSWDavis@gmail.com',
    license='MIT',
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
