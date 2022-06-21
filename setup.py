from distutils.core import setup

# from setuptools import setup

setup(
    name="LADiM",
    version="1.2",
    description="Lagrangian Advection and Diffusion Model",
    author="Bjørn Ådlandsvik",
    author_email="bjorn@imr.no",
    #packages=["ladim", "postladim", "ladim.ibms", "ladim.gridforce"],
    packages=["ladim", "ladim.ibms", "ladim.gridforce"],
    scripts=["scripts/ladim"],
    requires=["numpy", "yaml", "netCDF4", "pandas"],
)
