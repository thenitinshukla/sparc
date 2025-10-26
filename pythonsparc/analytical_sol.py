import numpy as np
from scipy.optimize import fsolve
from matplotlib import pyplot as plt
from particle import Particle

# to use Latex font type
plt.rcParams['text.usetex'] = True

def func(xi, t):
    Q0 = 4/3 * np.pi * 1**3
    return np.sqrt(xi * (xi - 1)) + np.log(np.sqrt(xi) + np.sqrt(xi-1)) - np.sqrt(2 * Q0/1**3) * t

maxR = []

time = np.arange(0,1,0.1)
for t in time:
    sol = fsolve(func,1,args = (t))
    maxR.append(sol)

data = np.load("Coulomb_explosion_dt0p001.npy", allow_pickle=True)
niter = len(data)
time_s = []
maxR_s = []
for it in range(0,niter):
    
    time_s.append(data[it][0])
    part = data[it][2]
    
    r = np.sqrt(part.x**2 + part.y**2 + part.z**2)
    maxR_s.append(np.max(r))

fig = plt.figure(figsize=(16,8))
plt.plot(time, maxR,'k',label = r"$theory$")
plt.plot(time_s, maxR_s, 'ro', label = r"$simulation$")
plt.xlabel(r"$t \; [\omega^{-1}]$", fontsize=20)
plt.ylabel(r"$r_{max} \; [R_0]$", fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.legend(fontsize=20)
plt.show()