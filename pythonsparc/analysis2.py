import numpy as np
from particle import Particle
from matplotlib import pyplot as plt

# to use Latex font type
plt.rcParams['text.usetex'] = True

# load npy file
data = np.load("Coulomb_explosion_dt0p001.npy", allow_pickle=True)

niter = len(data)

time = []
ene = []

# create lists with time and energy information only from data
for it in range(0,niter):
    time.append(data[it][0])
    ene.append(data[it][1])

print("At time {}, the conservation of energy is {}%".format(time[-1], 100*abs(ene[-1]-ene[0])/ene[0]))

# plot conservation of energy vs time
fig = plt.figure(figsize=(16,8))
plt.plot(time,abs(ene-ene[0])/ene[0],'k')
plt.xlabel(r"$t \; [\omega^{-1}]$", fontsize=20)
plt.ylabel(r"$|\varepsilon(t) - \varepsilon_0|/\varepsilon_0$", fontsize=20)
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.show()

