import numpy as np
from particle import Particle
import copy
import os

# Create output directory if it doesn't exist
output_dir = "python_output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# initialise random number
np.random.seed(10)

# we will model a spherical plasma composed of only protons
# we are going to use N computational particles
# quantity are normalised: R -> R/R_0, t -> t omega, n -> n/n_0
# our spherical plasma will have radius = 1 and total charge Q = sphere volume * n with n = 1
# protons will have normalised mass over charge = 1
N = int(1e4)
R = 1
Q = 4/3 * np.pi * R**3
iqom = 1 # inverse of charge over mass

# we want to generate particles uniformely distributed in a sphere
# so we first generate particles uniformely distributed in a cube
# and then we remove the particles with r_i > R
x = -R + 2 * R * np.random.rand(N)
y = -R + 2 * R * np.random.rand(N)
z = -R + 2 * R * np.random.rand(N)

r2 = x**2 + y**2 + z**2

inside = r2 <= R**2

xp = x[inside]
yp = y[inside]
zp = z[inside]

Np = xp.size

# we set the initial velocity of our particles to 0
vxp = np.zeros(Np)
vyp = np.zeros(Np)
vzp = np.zeros(Np)

# we compute the computational charge of our computational particles
# this is done in this way in such a way that if we increase/decrease the number of computational
# particles, we will still model the same system
qp = Q/Np * np.ones(Np)

# we initialise an instance of a class Particle called protons
protons = Particle(xp,yp,zp,vxp,vyp,vzp,"protons",qp,iqom)

# we set the temporal parameters of our simulation
dt = 0.001
tend = 1
Nt = int(np.ceil(tend/dt))

# we create an empty array data that will be used to store the results
data = []

# temporal cycle to advance our system
for it in range(0,Nt):

    # call class method to sort the particles
    protons.sorted()

    # call class method to update the radial electric field
    protons.updateE()

    # call class method to update the velocity and position of the particles
    protons.update(dt)

    # store quantities in the array data every 100 iterations
    if (it%100 == 0):
        print("Iteration {} out of {}.".format(it,Nt))
        ene = protons.energy()
        mylist = [it*dt, ene, copy.deepcopy(protons)]
        data.append(mylist)

# save data to npy file in the output directory
output_file = os.path.join(output_dir, "Coulomb_explosion_dt0p001.npy")
np.save(output_file, data, allow_pickle=True)
print(f"Results saved to {output_file}")

# Also save some additional data for analysis
energy_file = os.path.join(output_dir, "energy_vs_time.txt")
with open(energy_file, 'w') as f:
    f.write("Time\tEnergy\n")
    for item in data:
        f.write(f"{item[0]}\t{item[1]}\n")
print(f"Energy data saved to {energy_file}")