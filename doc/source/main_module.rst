:mod:`main` --- Main LADiM Module
=================================

.. module:: main
   :synopsis: The main control of LADiM

This module contains one function, :func:`main` governing  LADiM simulations.
Its signature is:

.. function:: main(config_stream, loglevel=logging.INFO)

   :arg stream config_stream: Configuration stream
   :arg int loglevel: Logging level, default = logging.INFO

The configuration stream is normally an open yaml-file, but can be a text
string by :mod:`StringIO` as in the jupyter example.

A simplified, but working, version of the :program:`ladim` script::

  import logging
  from ladim import main

  loglevel = logging.INFO
  config_file = 'ladim1.yaml'

  logging.basicConfig(
      level=loglevel, format='%(levelname)s:%(module)s - %(message)s')

  with open(config_file, encoding='utf8') as fp:
      main(config_stream=fp, loglevel=loglevel)
