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

# Fourth order Runge Kutta

C = C4
W4a = 1 - C*(1 - C/2 + C**2/6 - C**3/24)
W4b = 1 - C*(5./6 - C/3 + C**2/12)
W4c = 1 - C / 2
G = 1 - C + C**2/2 - C**3/4
W4 = W4a
W4 = np.where(G < 0, W4b, W4)
W4 = np.where(C > 2, W4c, W4)

# Estimate root of G (here 4*G)

coeff = [-1, 2, -4, 4]
print(np.roots(coeff)[-1])





plt.plot(C4, W,   lw=4, label='Exact')

plt.plot(C1, W1,  lw=2, label='Euler Forward')

plt.plot(C2, W2a, lw=2, label='Heun')
plt.plot(C4, W2b, lw=2, label='Midpoint')

plt.plot(C,  W4,  lw=2, label='Runge-Kutta 4')

plt.grid(True)

plt.axis((0, 4.05, 0, 1.05))

plt.legend(loc='best')

plt.show()
