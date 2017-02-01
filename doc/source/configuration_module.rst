Configuration class
===================

LADIM's configuration system uses the pyyaml package to read the
configuration file. This allows comments, nested keywords,
and flexibility in the sequence of keywords, missing or extra keyweord,

The Configuration class has no public methods, so it is basically
a dictionary. It supports both dictionary and attribute type access,
that is config['dt'] is equivalent to config.dt.
This is useful for IBM_variables, where the variable names are flexible.

Mandatory attributes
 - start_time
 - stop_time
 - reference_time: for output "time-units since reference_time"

 - grid_file
 - input_file  # rename to forcing_file
 - particle_release_file
 - output_file

 - Grid class   # presntly only ROMS type
 - attributes for Grid class, ROMS: subgrid and Vinfo

 - ibm_variables
 - IBM class
 - attributes for IBM class

 - release_format:  Format for a release line
 - release_dtype:  The type of the entries in the release line
 - particle_variables: The particle variables in the release
      [name is too general]

 - velocity:  mapping specifying velocity names
 - ibm_forcing:  mapping specifying ibm input names

 - output_period
 - output_variables

 - dt
 - advection: EF, RK2 or RK4
 - diffusion: Logical switch for horizontal diffusion
 - diffusion_coefficient: only needed if diffusion = True
