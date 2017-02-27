from distutils.core import setup

setup(
   name='Ladim',
   version='2.8',
   description='Lagrangian Advection and DIffusion Model',
   author='Bjørn Ådlandsvik',
   author_email='bjorn@imr.no',
   packages=['ladim', 'postladim', 'ladim.ibms', 'ladim.gridforce'],
   scripts=['scripts/ladim'],
   requires=['numpy', 'yaml', 'netCDF4']
)
