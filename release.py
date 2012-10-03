# -*- coding: utf-8 -*-

# Particle release class

# File format
# columns x, y, z, relative time (in hours)

# Vil ha ut, nye partikler + tidspunkt for ny
# HA dette som en generator
# initielt: particle_counter = 0, 
# etter kall: oppdateret particle_counter, 
#     dictionary med nye partikler (arrays)
#     +tid for ny

# Ha dette som klasse 

# Bedre ha klasse (eller dictionary for output) 
# pluss generator

class ParticleReleaser(object):

    def __init__(self, particle_release_file):
        self.fid = open(particle_release_file)
        self.particle_counter = 0
        self.release_step = 0
        # Read to first time line 
        # Alternativt ikke bruke T på denne
        # Nå: Leser ikke tiden.
        for line in self.fid:
            print line
            if line[0] == 'T' : break

    def read_particles(self):

        for line in self.fid:

            # Remove trailing white space
            line = line.strip()  

            # Skip blank lines
            if not line: continue

            # Skip comments
            if line[0] in ['#','!']: continue

            print line
            
            if line[0] == 'G':   # Grid coordinates
                w = line.split()
                self.particle_counter += 1
                X.append(float(w[1]))
                Y.append(float(w[2]))
                Z.append(float(w[3]))
                start.append(release_step)
                pid.append(particle_counter)
 
            if line[0] == "T": # Time line
                # Break 
                self.X = np.array(X)
                self.Y = np.array(Y)
                self.Z = np.array(Z)
                self.start = np.array(start)  # Bedre navn
                self.pid = np.array(pid)
                #yield()
                break
                if line[1] == "R":  # Relative time
                    w = line.split()
                    tdelta = int(w[1])
                    units = w[2]
                    if units[0] == 'h':
                        tdelta = tdelta*3600
                    elif units[0] == 'd': 
                        tdelta = tdelta*24*3600
                    release_step = tdelta // setup['dt']
                    print "next release step = ", release_step
                X, Y, Z, start = [], [], [], []


            







if __name__ == "__main__":

    from setup import readsup
    setup = readsup('ladim.sup')
    particle_release_file = 'particles.in'
    p = ParticleReleaser('particles.in')
    p.read_particles()
    #p.read_particles()
    print p.X


    
