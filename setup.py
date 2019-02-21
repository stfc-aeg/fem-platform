"""Setup script for odin_data python package."""

import sys
from setuptools import setup, find_packages
import versioneer

with open('requirements.txt') as f:
   required = f.read().splitlines()

setup(name='fem',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='STFC FEM client framework',
      url='https://github.com/stfc-aeg/fem-platform.git',
      author='Tim Nicholls',
      author_email='tim.nicholls@stfc.ac.uk',
      packages=find_packages(),
      install_requires=required,
      entry_points={
        'console_scripts': [
            'fem_shell = fem.utils.shell:main',
            'fem_reconfig_ip = fem.utils.reconfig_ip:main'
         ]
      },
      zip_safe=False,
)
