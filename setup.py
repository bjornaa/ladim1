from distutils.core import setup

# from setuptools import setup

setup(
    name="LADiM",
    version="1.2",
    description="Lagrangian Advection and Diffusion Model",
    author="Bjørn Ådlandsvik",
    author_email="bjorn@imr.no",
    #packages=["ladim", "postladim", "ladim1.ibms", "ladim1.gridforce"],
    packages=["ladim1", "ladim1.ibms", "ladim1.gridforce"],
    scripts=["scripts/ladim1"],
    requires=["numpy", "yaml", "netCDF4", "pandas"],
)
