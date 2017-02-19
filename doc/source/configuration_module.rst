.. configuration:

:mod:`configuration` --- LADIM Configuration
============================================

.. module:: configuration
   :synopsis: LADIM configuration

LADIM's configuration system uses the :mod:`pyyaml` package to read the
configuration file. This allows comments, nested keywords,
and flexibility in the sequence of keywords, missing or extra keyweord,

The Configuration class has no public methods, so it is basically
a dictionary. It supports both dictionary and attribute type access,
that is ``config['dt']`` is equivalent to ``config.dt``.
This is useful for IBM variables, where the variable names are flexible.

.. class:: Configure()

   Mandatory attributes

   .. attribute:: start_time
   .. attribute:: stop_time
   .. attribute:: reference_time

      for output "time-units since reference_time"

   .. attribute:: grid_file
   .. attribute:: forcing_file
   .. attribute:: particle_release_file
   .. attribute:: output_file

   .. attribute:: Grid class

   attributes for Grid class, ROMS: subgrid and Vinfo

   .. attribute:: ibm_variables
   .. attribute:: IBM class

   attributes for IBM class

   .. attribute:: release_format

      Format for a release line

   .. attribute:: release_dtype

      The types of the entries in the release line

   .. attribute:: particle_variables:

      The particle variables in the release  [name is too general]

   .. attribute:: velocity

      Mapping specifying velocity names

   .. attribute:: ibm_forcing

      Mapping specifying ibm input names

   .. attribute:: output_period
   .. attribute:: output_variables

   .. attribute:: dt
   .. attribute:: advection

      EF, RK2 or RK4

   .. attribute:: diffusion

      Logical switch for horizontal diffusion

   .. attribute:: diffusion_coefficient

      Only needed if diffusion = True
