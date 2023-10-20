import numpy as np

def gyroscope(stateVector, t, parameters):
#       Arguments:
#           stateVector: [qTheta, qPhi, qPsi, pTheta, pPhi, pPsi]
#                    t :  time
#                   p  :  vector of the parameters:
#                  p = [L, a, h, g]
    theta, phi, psi, thetaVel, phiVel, psiVel = stateVector
    L = parameters['l'] 
    a = parameters['a']
    h = parameters['h']
    g = parameters['g']
    

    # time derivative of the state vector (Hamilton's Equations)
    soln = [thetaVel,
    phiVel,
    psiVel,
    0,
    L**2 * np.cos(phi) * np.sin(phi) * thetaVel**2 - a**2 * thetaVel * np.sin(phi) * (thetaVel * np.cos(phi) + psiVel) + L * g * np.sin(phi),
    0]
    return soln

# Rotates an x,y,z coordinates by precession theta and nutation phi.
def eulerRotation(x, y, z, theta, phi):
    # Columns of the matrix representing the linear transfomation that rotates the cylinder into places. 
    #   (The rotation given by psi (doesn't move the CM of the object) will be calculated in the drawing of the cylinder)
    Rx = [-np.sin(theta),   np.cos(theta),   0]
    Ry = [-np.cos(theta)*np.cos(phi),   -np.sin(theta)*np.cos(phi),   np.sin(phi)]
    Rz = [np.cos(theta)*np.sin(phi),   np.sin(theta)*np.sin(phi),   np.cos(phi)]
    X = Rx[0]*x + Ry[0]*y + Rz[0]*z
    Y = Rx[1]*x + Ry[1]*y + Rz[1]*z
    Z = Rx[2]*x + Ry[2]*y + Rz[2]*z
    return (X, Y, Z)
