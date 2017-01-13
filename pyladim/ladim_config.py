

# import datetime
import numpy as np
import yaml


class Configure():

    def __init__(self, config_file):

        # Read the configuration file
        with open(config_file) as fp:
            conf = yaml.safe_load(fp)

        for name in ['start_time', 'stop_time', 'reference_time']:
            self[name] = conf['time_control'][name]

        for name in ['grid_file', 'input_file',
                     'particle_release_file', 'output_file']:
            self[name] = conf['files'][name]

        self['release_format'] = conf['particle_release']['variables']
        print(self.release_format)
        self['release_dtype'] = dict()
        for name in self['release_format']:
            self['release_dtype'][name] = (
                conf['particle_release'].get(name, 'float'))

        state = conf['state']
        if state:
            v = state['ibm_variables']
            if v:
                self['ibm_variables'] = v
        else:
            self['ibm_variables'] = []

        # Output
        self['output_particle'] = conf['output_variables']['particle']
        self['output_instance'] = conf['output_variables']['instance']
        self['nc_attributes'] = dict()
        for name in self.output_particle + self.output_instance:
            self['nc_attributes'][name] = conf['output_variables'][name]

        # Various
        self['dt'] = conf['ymse']['dt']

        simulation_time = np.timedelta64(
            self['stop_time'] - self['start_time'], 's').astype('int')
        self['nsteps'] = simulation_time // self['dt']
        print("Number of time steps = ", self['nsteps'])

        outper = np.timedelta64(*tuple(conf['ymse']['outper']))
        print(outper)
        self['outper'] = outper.astype('m8[s]').astype('int')
        print(self['outper'])

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)


#     setup['dt'] = int(self.get('time', 'dt'))
#
#
#     total_time = setup.stop_time - setup.start_time
#     total_time = np.timedelta64(total_time, 's').astype('i')
#     setup['nsteps'] = total_time // setup.dt
#
#     # ---------------------
#     # State variables
#     # ---------------------
#
#     # Få bedre hva som
#     pvars = self.get('variables', 'particle_variables')
#     setup['particle_variables'] = []
#     for v in pvars.split():
#         converter = float
#         n = v.find(':')
#         if n < 0:  # default = float
#             name = v
#         else:
#             name = v[:n]
#             dtype = v[n+1:]
#             if dtype == 'int':
#                 converter = int
#         setup.particle_variables.append((name, converter))
#
#     svars = self.get('variables', 'extra_state_variables')
#     setup['extra_state_variables'] = []
#     for v in svars.split():
#         converter = float
#         n = v.find(':')
#         if n < 0:  # default = float
#             name = v
#         else:
#             name = v[:n]
#             dtype = v[n+1:]
#             if dtype == 'int':
#                 converter = int
#         setup.extra_state_variables.append((name, converter))
#
#     # ----------
#     # Output
#     # ----------
#
#     # Lage seksjon [output] i sup-fil ??
#     setup['output_filename'] = self.get('output', 'output_filename')
#
#     ref_time = self.get('output', 'reference_time')
#     if not ref_time:
#         ref_time = setup.start_time
#     setup['reference_time'] = np.datetime64(ref_time)
#
#     outper = self.get('output', 'output_period')
#     outper_s = self.get('output', 'output_period_seconds')
#     outper_h = self.get('output', 'output_period_hours')
#
#     if outper not in ["", None, "None"]:
#         outper = int(outper)
#     elif outper_s not in ["", None, "None"]:
#         outper = int(outper_s) // setup.dt
#     elif outper_h not in ["", None, "None"]:
#         outper = int(outper_h) * 3600 // setup.dt
#     setup['output_period'] = outper
#
#     # Number of time frames in output, add one for initial distribution
#     setup['Nout'] = 1 + setup.nsteps // outper
#
#     # Output variables
#     w = self.get('output', 'output_variables')
#     w = w.replace(",", " ")  # replace commas with blanks
#     setup['output_variables'] = w.split()
#
# # --------------

    def write(self):

        # Disse kan defineres i __init__
        time_keys = ['start_time', 'stop_time', 'reference_time']
        file_keys = ['grid_file', 'input_file', 'particle_release_file',
                     'output_file']

        for key in time_keys:
            print('{:24s}:'.format(key), self[key])

        print("---")

        for key in file_keys:
            print('{:24s}:'.format(key), self[key])

        print("---")

        print('IBM-variable = ', self.ibm_variables)

        print('particle release format')
        for key in self.release_format:
            print('    {:20s}:'.format(key), self.release_dtype[key])

        print("---")

        # Kan skrives penere
        print("Output variables")
        print("  Particle variables")
        for name in self.output_particle:
            print('    {:20s}:'.format(name), self.nc_attributes[name])
        print("  Particle instance variables")
        for name in self.output_instance:
            print('    {:20s}:'.format(name), self.nc_attributes[name])


# def write_config(setup):
#     # Make an explicit sequence of keys
#     # Can be improved with ordered_dict (from python 2.7)
#     time_keys = ['start_time', 'stop_time', 'dt', 'nsteps']
#     input_keys = ['grid_file', 'input_file', 'particle_release_file']
#     variable_keys = ['particle_variables', 'extra_state_variables']
#     output_keys = ['output_filename', 'output_period',
#                    'Nout', 'output_variables']
#
#     for keylist in [time_keys, input_keys, variable_keys, output_keys]:
#         print(50*"-")
#         for key in keylist:
#             print("%24s :" % key, getattr(setup, key))
#
#     print(50*"-")
#
# # -------------
# # Simple test
# # -------------
#
if __name__ == '__main__':
    config = Configure('../ladim.yaml')
    config.write()
