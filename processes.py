import matplotlib as mpl
mpl.use('agg')
import numpy
from numpy import loadtxt
from physics import gyroscope
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

def solveODE(engine, initialState, parameters, solverParameters):
    from scipy.integrate import odeint
    abserr, relerr, soln_path, stoptime, numpoints = solverParameters
    L, a, h, g = parameters
    theta, phi, psi, thetaVel, phiVel, psiVel = initialState
    t = [stoptime * float(i) / (numpoints - 1) for i in range(numpoints)]

    # Call the ODE solver and record solution.
    gyroSol = odeint(engine, initialState, t, args=(parameters,),
                  atol=abserr, rtol=relerr)

    with open(soln_path, 'w') as file:
        print>> file, "time", "theta", "psi", "thetaVel", "phiVel", "psiVel"
        for t1, soln in zip(t, gyroSol):
            print >> file, t1, soln[0], soln[1], soln[2], soln[3], soln[4], soln[5]
    return

def generateFrames(theta, phi, psi, transformMethod, parameters, animationParameters):
    L, a, h, g = parameters
    rstride, cstride, nSample, numpoints, frameName = animationParameters

    fig = plt.figure()
    nSample = 45 # Per half of cylinder
    x1 = []
    x2 = []
    y1 = []
    y2 = []

    for i in range(numpoints):
        ax = Axes3D(fig)
        ax.axis("off")
        # ax.clear() # comment out if placing ax definition in animate()
        # ax.axis("off") # comment out if placing ax definition in animate()
        ax.plot([-L/2,L/2],[0,0],[0,0], color = "gray") 
        ax.plot([0, 0],[-L/2,L/2],[0,0], color = "gray")
    #    ax.plot([0, 0],[0,0],[-L/4,3*L/2], linestyle='dashed', color = "gray") 
        ax.set_xlim3d(-L,L)
        ax.set_ylim3d(-L,L)
        ax.set_zlim3d(-L,L)

        name = frameName%i

        # Read in phi and theta from ODE soln. Move the cylinders accordingly.

        # Generate coordinates that will define cylinder
        x1 = []
        x2 = []
        y1 = []
        y2 = []


        for j in range(nSample + 1):
            x1.append(a*numpy.cos(psi[i] + j * numpy.pi/nSample)) 
            x2.append(-a*numpy.cos(psi[i] + j * numpy.pi/nSample))
            y1.append(a*numpy.sin(psi[i] + j * numpy.pi/nSample)) 
            y2.append(-a*numpy.sin(psi[i] + j * numpy.pi/nSample))

        z1 = numpy.linspace(L-h/2, L+h/2, len(x1))
        z2 = numpy.linspace(L-h/2, L+h/2, len(x2))

        # Convert to meshgrid for plotting
        xc1, zc1 = numpy.meshgrid(x1, z1)
        xc2, zc2 = numpy.meshgrid(x2, z2)
        yc1, zc1 = numpy.meshgrid(y1, z1)
        yc2, zc2 = numpy.meshgrid(y2, z2)


        x1Moved, y1Moved, z1Moved = transformMethod(xc1, yc1, zc1, theta[i], phi[i]) 
        x2Moved, y2Moved, z2Moved = transformMethod(xc2, yc2, zc2, theta[i], phi[i]) 
        
        # Plot both halves of the cylinder, and the rod.
        rod = ax.plot([0, 5*L/4*numpy.sin(phi[i])*numpy.cos(theta[i])],[0, 5*L/4*numpy.sin(phi[i])*numpy.sin(theta[i])],[0,5*L/4*numpy.cos(phi[i])], color = "black")
        cylinderHalf = ax.plot_surface(x1Moved, y1Moved, z1Moved, alpha=0.8, rstride=rstride, cstride=cstride, color = "red")
        cylinderHalf2 = ax.plot_surface(x2Moved, y2Moved, z2Moved, alpha=0.8, rstride=rstride, cstride=cstride)
        plt.savefig(name, dpi = 300)

        ax.clear()
        if numpy.mod(i,20) == 0:
            print("    " + str(i) + " of " + str(numpoints) + " frames saved")
    return