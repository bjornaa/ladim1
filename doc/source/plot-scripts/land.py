import numpy as np
import matplotlib.pyplot as plt

C1 = np.linspace(0, 1, 50)
C2 = np.linspace(0, 2, 100)
C4 = np.linspace(0, 4.1, 200)

# Exact
W  = np.exp(-C4)

# First order
W1 = 1 - C1
# Second order

W2a = 1 - 0.5*C2
W2a = np.where(C2 < 1, 1 - C2 + 0.5*C2*C2, W2a)

W2b = np.ones_like(C4)
W2b = np.where(C4 < 2, 1 - C4 + 0.5*C4*C4, W2b)


plt.plot(C4, W, lw=2)

plt.plot(C1, W1)

plt.plot(C2, W2a)
plt.plot(C4, W2b)

plt.grid(True)

plt.axis((0, 4.05, 0, 1.05))

plt.show()
