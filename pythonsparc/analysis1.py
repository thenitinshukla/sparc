import numpy as np
from particle import Particle
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

# to use Latex font type
plt.rcParams['text.usetex'] = True

# load npy file
data = np.load("Coulomb_explosion_dt0p001.npy", allow_pickle=True)

niter = len(data)

# instructions to set the figure
# we want a figure containing 3 subplots arranged in a 3x1 fashion
fig = plt.figure(figsize=(16,8))
# first sublot will be field vs radial position
ax1 = fig.add_subplot(3,1,1)
ax1.set_xlim(0.0,3.0)
ax1.set_ylim(0,5)
ax1.set_ylabel(r"$E_r \; [m \omega^2 R/e]$",fontsize=20)
ax1.tick_params(labelsize=20)
plot1, = ax1.plot([],[],'k')
# second sublot will be particle density vs radial position
ax2 = fig.add_subplot(3,1,2)
ax2.set_xlim(0.0,3.0)
ax2.set_ylim(0,1.2)
ax2.set_xlabel(r"$r \; [R_0]$",fontsize=20)
ax2.set_ylabel(r"$n \; [n_0]$",fontsize=20)
ax2.tick_params(labelsize=20)
plot2, = ax2.plot([],[],'k')
# third sublot will be the phase space (e.g. radial velocity vs radial position of each particle)
ax3 = fig.add_subplot(3,1,3)
ax3.set_xlim(0.0,3.0)
ax3.set_ylim(0,3)
ax3.set_xlabel(r"$r \; [R_0]$",fontsize=20)
ax3.set_ylabel(r"$v_r \; [R_0 \omega]$",fontsize=20)
ax3.tick_params(labelsize=20)
plot3, = ax3.plot([],[],'k.')

# function to set the plot
def anim_step(i):

    # unpacking information from data
    time = data[i][0]
    part = data[i][2]
    
    # first subplot
    r = np.sqrt(part.x**2 + part.y**2 + part.z**2)
    er = part.Er
    
    plot1.set_data(r,er)

    # second subplot
    # we need to bin the particles in a histogram
    nbins = 50
    Rmax = 10
    n = np.histogram(r, bins = nbins, range = (0,Rmax), weights = part.q)
    rc = (0.5 + np.arange(0, nbins, 1, dtype=float)) * Rmax/nbins
    drc = (rc[1] - rc[0])
    dVc = 4/3 * np.pi * ( (rc + drc/2)**3 - (rc - drc/2)**3)
    plot2.set_data(rc,n[0]/dVc)

    # third subplot
    vr = np.sqrt(part.vx**2 + part.vy**2 + part.vz**2)
    plot3.set_data(r,vr)

    return plot1, plot2, plot3,

# special instructions to show an animation
anim = FuncAnimation(fig, anim_step, frames = niter, interval = 1000, blit = True, repeat=False)
plt.show()