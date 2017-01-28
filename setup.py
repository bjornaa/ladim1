from distutils.core import setup

setup(
   name='Ladim',
   version='0.6',
   description='Lagrangian Advection and DIffusion Model',
   author='Bjørn Ådlandsvik',
   author_email='bjorn@imr.no',
   packages=['ladim', 'postladim', 'ladim.ibms'],
   install_requires=['numpy', 'pandas', 'pyyaml', 'roppy'],
   scripts=['scripts/ladim']
)
