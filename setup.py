from setuptools import find_packages, setup
import os

# get requirements for installation
lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()
        
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

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
