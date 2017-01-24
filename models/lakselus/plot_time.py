import numpy as np
import matplotlib.pyplot as plt

T, U, S, Tot = np.loadtxt('timing.dat', unpack=True)

plt.plot(T, U, 'o-')
plt.plot(T, S, 'o-')
plt.plot(T, Tot, 'o-')

plt.show()
