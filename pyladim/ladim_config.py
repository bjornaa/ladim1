

# import datetime
import numpy as np
import yaml


class Configure():

    def __init__(self, config_file):

        # --- Read the configuration file ---
        with open(config_file) as fp:
            conf = yaml.safe_load(fp)

        # --- Time control ---
        for name in ['start_time', 'stop_time', 'reference_time']:
            self[name] = conf['time_control'][name]

        # --- Files ---
        for name in ['grid_file', 'input_file',
                     'particle_release_file', 'output_file']:
            self[name] = conf['files'][name]

        # --- Time steping ---
        self.dt = conf['ymse']['dt']
        simulation_time = np.timedelta64(
            self.stop_time - self.start_time, 's').astype('int')
        self.numsteps = simulation_time // self.dt

        # --- Particle release ---
        prelease = conf['particle_release']
        self.release_format = conf['particle_release']['variables']
        self.release_dtype = dict()
        for name in self.release_format:
            self.release_dtype[name] = (
                conf['particle_release'].get(name, 'float'))
        self.particle_variables = prelease['particle_variables']

        # --- Model state ---
        state = conf['state']
        if state:
            v = state['ibm_variables']
            if v:
                self.ibm_variables = v
        else:
            self.ibm_variables = []

        # --- Output control ---
        self.output_particle = conf['output_variables']['particle']
        self.output_instance = conf['output_variables']['instance']
        self.nc_attributes = dict()
        for name in self.output_particle + self.output_instance:
            value = conf['output_variables'][name]
            if 'units' in value:
                if value['units'] == 'seconds since reference_time':
                    value['units'] = 'seconds since {:s}'.format(
                            str(self.reference_time))
            self.nc_attributes[name] = conf['output_variables'][name]
        outper = np.timedelta64(*tuple(conf['ymse']['outper']))
        outper = outper.astype('m8[s]').astype('int') // self['dt']
        self.output_period = outper
        # Under may be moved to output class
        self.num_output = 1 + self.numsteps // self.output_period

    # Allow item notation
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

# --------------

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
            print("    {:s}".format(name))
            for item in self.nc_attributes[name].items():
                print('        {:15s}: {:s}'.format(*item))
            # print('    {:20s}:'.format(name), self.nc_attributes[name])
        print("  Particle instance variables")
        for name in self.output_instance:
            print("    {:s}".format(name))
            for item in self.nc_attributes[name].items():
                print('        {:15s}: {:s}'.format(*item))

        print(self.particle_variables)

# # -------------
# # Simple test
# # -------------
#
if __name__ == '__main__':
    config = Configure('../ladim.yaml')
    config.write()
