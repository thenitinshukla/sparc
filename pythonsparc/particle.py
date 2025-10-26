import numpy as np

class Particle:

    """
    Class to setup particle species

    Parameters
    ----------
    x, y, z: numpy arrays
       Arrays containing the 3D position of each computational particles
    vx, vy, vz: numpy arrays
       Arrays containing the 3D velocity of each computational particles
    name: string
       Name of the species
    q: numpy array
       Array containing the computational charge of each particle
    iqom: float
       Inverse of the charge over mass for the species
    """

    def __init__(self, x, y, z, vx, vy, vz, name, q, iqom):

        self.name = name
        self.iqom = iqom
        self.x = np.array(x, dtype=float)
        self.y = np.array(y, dtype=float)
        self.z = np.array(z, dtype=float)
        self.vx = np.array(vx, dtype=float)
        self.vy = np.array(vy, dtype=float)
        self.vz = np.array(vz, dtype=float)
        self.q = np.array(q, dtype=float)
        self.Er = np.zeros_like(q)
    
    def __str__(self):
        npart = self.x.size
        return "In your simulation there are {0} particles of species {1}.".format(npart, self.name)

    def squareRadius(self):

        """
        Method to compute the radial position of each particle

        Returns
        -------
        r2: numpy array
           Array containing the radial position square of each particle
        """

        r2 = self.x**2 + self.y**2 + self.z**2
        return r2

    def sorted(self):

        """
        Method to sort the particle arrays based on the particle radial position
        """

        idx = np.argsort(self.squareRadius())

        self.x = self.x[idx]
        self.y = self.y[idx]
        self.z = self.z[idx]

        self.vx = self.vx[idx]
        self.vy = self.vy[idx]
        self.vz = self.vz[idx]

        self.q = self.q[idx]

    def updateE(self):

        """
        Method to compute the radial electirc field based on Gauss's law
        """

        self.Er = np.cumsum(self.q)/(self.squareRadius())

    def update(self,dt):

        """
        Method to update the 3D cartesian velocity and position of the particles using Euler-Cromer

        Parameters
        ----------
        dt: float
           The temporal step
        """

        r = np.sqrt(self.squareRadius())
        qom = 1/self.iqom
        self.vx += dt * qom * self.Er * self.x / r
        self.vy += dt * qom * self.Er * self.y / r
        self.vz += dt * qom * self.Er * self.z / r

        self.x += dt * self.vx
        self.y += dt * self.vy
        self.z += dt * self.vz

    def energy(self):

        """
        Method to compute the total energy of the system
        """
        
        v2 = self.vx**2 + self.vy**2 + self.vz**2
        K = np.sum(0.5 * np.abs(self.iqom * self.q) * v2)

        npart = v2.size
        
        U = 0
        for j in range(0,npart):
            rj = np.sqrt( (self.x - self.x[j])**2 + (self.y - self.y[j])**2 + (self.z - self.z[j])**2)
            valid = rj != 0
            # pay attention to the 0.5 factor to avoid double counting the contribution of particles
            U += np.sum(0.5 * self.q[valid] * self.q[j] / rj[valid])
        
        #these lines do the same as the previous lines, but the code is slower, even if more readable
        #U2 = 0
        #for i in range(0,npart):
        #    for j in range(0,npart):
        #        rij = np.sqrt( (self.x[i] - self.x[j])**2 + (self.y[i] - self.y[j])**2 + (self.z[i] - self.z[j])**2)
        #        if rij != 0:
        #            U2 += 0.5 * self.q[i] * self.q[j] / rij

        return K + U

    def momentum(self):

        """
        Method to compute the total linear momentum of the system
        Complete this method and call it from main.py
        """
        return float('nan')



    