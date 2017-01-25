import numpy as np
import matplotlib.pyplot as plt

i = 23
x = i - 0.5 + 0.3  
#q = i + 0.5 - x     # 0.7



def u(s, c):
    if s < i + 0.5:
        return (i+0.5-s)*c
    else:
        return 0

N = 101
A = np.zeros((N,))
C = np.linspace(0, 4.0, N)

q = (i+0.5-x)

K1 = q*C

V = q - 0.5*K1
K2 = np.where(V > 0, V*C, 0)

V = q - 0.5*K2
#K3 = np.where(V > 0, V*C, 0)
K3 = V*C

V = q - K3
K4 = np.where(V > 0, V*C, 0)


K = (K1 + 2*K2 + 2*K3 + K4)/6


#plt.plot(C, K1)
#plt.plot(C, K2)
#plt.plot(C, K3)
#plt.plot(C, K4)
plt.plot(C, K)

M1 = q*C

M2 = q*C*(1-C/2)        
#M2 = np.where(C<2, M2, 0)  

M3a = q*C*(1-C/2+C**2/4)
M3b = q*C
M3 = np.where(C<2, M3a, M3b)

M4 = q*C*(1-C+C**2/2-C**3/4)
M4 = np.where(K > 0, M4, 0)




#M = (M1 + 2*M2 + 2*M3 + M4)/6
Ma = q*C*(1 - C/2 + C**2/6 - C**3/24)
Mb = q*C*(5./6 - C/3 + C**2/12)
Mc = q*C / 2

G = 1 - C + C**2/2 - C**3/4

M = Ma
M = np.where(G < 0, Mb, M)
M = np.where(C > 2, Mc, M)


#plt.plot(C, M1)
#plt.plot(C, M2, 'o')
#plt.plot(C, M3, 'o')
#plt.plot(C, M4, 'o')
#plt.plot(C, Ma, 'o')
#plt.plot(C, Mb, 'o')
#plt.plot(C, Mc, 'o')

plt.plot(C, M, 'o')


plt.grid(True)

plt.show()




