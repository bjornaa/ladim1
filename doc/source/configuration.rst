LADIM configuration
===================

The LADIM model is highly configurable using a separate configuration file.
The goal is that a user should not have to touch the code, every necessary
aspect should be customable by the configuration file.

The name of the configuration file is given as a command line argument to the
main ladim script. If the name is missing, a default name of ladim.yaml is
supposed.

It is a goal to provide sane defaults in the configuration file, so that
enhancements of the configuration setup do not break existing configuration
files.

The syntax of the configuration file is yaml (YAML Ain't Markup Language)
http://yaml.org . Detailed knowledge of yaml is not necessary. The example
configuration files are self-describing and can easily be modified.

Question

LADIM can be used with different IBMs (Individual Based behaviour Models).
These may require quite different
configurations. Should they be accompanied by a separate configuration file?
Main configuration may just state which IBM module to use,
and the name of the IBM configuration file.




An example configuration file
-----------------------------

Below is an example configuration file,
