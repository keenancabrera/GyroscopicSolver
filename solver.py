import matplotlib as mpl
import numpy
import json
from physics import *
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import odeint
import ffmpeg
import os

class solver:
    def __init__(self, jsonPath):
        self.parameters = {}
        self.solverParameters = {}
        self.initialState = {}
        self.animationParameters = {}
        self.solution = []
        self.soln_path = 'output/gyroscope.csv'
        self.animation_path = 'output/gyroscope.mov'
        self.frame_path = 'output/images'
        self.frameName = "output/images/gyroscope_%03i"

        if not os.path.exists(self.frame_path):
            os.makedirs(self.frame_path)

        try: 
            f = open(jsonPath)
            input = json.load(f)
            input = self.convert_numbers(input)

            if input['parameters']: self.parameters = input['parameters']
            if input['solverParameters']:
                self.solverParameters = input['solverParameters']
                self.solverParameters['numpoints'] = int(self.solverParameters['stoptime'] * self.solverParameters['fps'])
            if input['initialState']: 
                self.initialState = input['initialState']
                self.initialState['pTheta'] = self.parameters['a']**2 + self.initialState['thetaVel'] + np.sin(self.initialState['phi'])**2 + self.parameters['a']**2*np.cos(self.initialState['phi'])*(self.initialState['thetaVel']*np.cos(self.initialState['phi'] + self.initialState['psiVel']))
                self.initialState['pPhi'] = self.parameters['a']**2 * self.initialState['thetaVel'] * np.cos(self.initialState['psi'])
                self.initialState['pPsi'] = self.parameters['a'] ** 2 * (self.initialState['theta'] * np.cos(self.initialState['phi']) + self.initialState['psiVel'])
            if input['animationParameters']: self.animationParameters = input['animationParameters']

            f.close()
            pass
        except Exception as e:
            print(f'JSON failed to load: {e}')
    
    def convert_numbers(self, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str):
                    # Try to convert the string to an int or float
                    try:
                        obj[key] = int(value) if value.isdigit() else float(value)
                    except ValueError:
                        pass
                elif isinstance(value, dict):
                    self.convert_numbers(value)
        return obj

    def solveODE(self, engine):
        t = [self.solverParameters["stoptime"] * float(i) / (self.solverParameters["numpoints"] - 1) for i in range(self.solverParameters["numpoints"])]

        # Call the ODE solver and record solution.
        solution = odeint(engine, 
                          [self.initialState['theta'],
                           self.initialState['phi'],
                           self.initialState['psi'],
                           self.initialState['pTheta'],
                           self.initialState['pPhi'],
                           self.initialState['pPsi']], 
                          t, 
                          args=(self.parameters,),
                          atol=self.solverParameters["abserr"], 
                          rtol=self.solverParameters["relerr"],
                          full_output=True
                          )

        self.solution = {
            "t" : t,
            "theta" : [elem[0] for elem in solution[0]],
            "phi" : [elem[1] for elem in solution[0]],
            "psi" : [elem[2] for elem in solution[0]], 
            "pTheta": [elem[3] for elem in solution[0]], 
            "pPhi": [elem[4] for elem in solution[0]], 
            "pPsi": [elem[5] for elem in solution[0]]
        }

        self.dataFrame = pd.DataFrame.from_dict(self.solution)
        self.solveInfo = solution[1]
        self.dataFrame.to_csv(self.soln_path)
        
    def generateFrames(self, transformMethod):

        L = self.parameters['l'] 
        a = self.parameters['a']
        h = self.parameters['h']
        g = self.parameters['g']

        fig = plt.figure()
        nSample = 45 # Per half of cylinder
        x1 = []
        x2 = []
        y1 = []
        y2 = []


        ax = fig.add_subplot(111, projection='3d')
        ax.set_axis_off()
        
        for i in range(self.solverParameters['numpoints']):

            ax.clear() # comment out if placing ax definition in animate()
            ax.axis("off") # comment out if placing ax definition in animate()
            ax.plot([-L/2,L/2],[0,0],[0,0], color = "gray") 
            ax.plot([0, 0],[-L/2,L/2],[0,0], color = "gray")
        #    ax.plot([0, 0],[0,0],[-L/4,3*L/2], linestyle='dashed', color = "gray") 
            ax.set_xlim3d(-L,L)
            ax.set_ylim3d(-L,L)
            ax.set_zlim3d(-L,L)

            name = self.frameName%i

            # Read in phi and theta from ODE soln. Move the cylinders accordingly.

            # Generate coordinates that will define cylinder
            x1 = []
            x2 = []
            y1 = []
            y2 = []


            for j in range(nSample + 1):
                x1.append(a*numpy.cos(self.solution['psi'][i] + j * numpy.pi/nSample)) 
                x2.append(-a*numpy.cos(self.solution['psi'][i] + j * numpy.pi/nSample))
                y1.append(a*numpy.sin(self.solution['psi'][i] + j * numpy.pi/nSample)) 
                y2.append(-a*numpy.sin(self.solution['psi'][i] + j * numpy.pi/nSample))

            z1 = numpy.linspace(L-h/2, L+h/2, len(x1))
            z2 = numpy.linspace(L-h/2, L+h/2, len(x2))

            # Convert to meshgrid for plotting
            xc1, zc1 = numpy.meshgrid(x1, z1)
            xc2, zc2 = numpy.meshgrid(x2, z2)
            yc1, zc1 = numpy.meshgrid(y1, z1)
            yc2, zc2 = numpy.meshgrid(y2, z2)


            x1Moved, y1Moved, z1Moved = transformMethod(xc1, yc1, zc1, self.solution['theta'][i], self.solution['phi'][i]) 
            x2Moved, y2Moved, z2Moved = transformMethod(xc2, yc2, zc2, self.solution['theta'][i], self.solution['phi'][i]) 
            
            # Plot both halves of the cylinder, and the rod.
            rod = ax.plot([0, 5*L/4*numpy.sin(self.solution['phi'][i])*numpy.cos(self.solution['theta'][i])],[0, 5*L/4*numpy.sin(self.solution['phi'][i])*numpy.sin(self.solution['theta'][i])],[0,5*L/4*numpy.cos(self.solution['phi'][i])], color = "black")
            cylinderHalf = ax.plot_surface(x1Moved, y1Moved, z1Moved, alpha=self.animationParameters['transparency'], rstride=self.animationParameters['rstride'], cstride=self.animationParameters['cstride'], color = "red")
            cylinderHalf2 = ax.plot_surface(x2Moved, y2Moved, z2Moved, alpha=self.animationParameters['transparency'], rstride=self.animationParameters['rstride'], cstride=self.animationParameters['cstride'])

            fig.savefig(name, dpi = self.animationParameters['dpi'])

            ax.clear()
            if numpy.mod(i,20) == 0:
                print("    " + str(i) + " of " + str(self.solverParameters['numpoints']) + " frames saved")
        return
        
    def stitchVideo(self):
        if os.path.exists(self.animation_path):
            os.remove(self.animation_path)

        (
        ffmpeg
        .input(f'{self.frame_path}/*.png', pattern_type='glob', framerate=self.solverParameters['fps'])
        .output(f'{self.animation_path}', pix_fmt = "yuv420p")
        .run()
        )




SIM = solver('input.json')
SIM.solveODE(gyroscope)
SIM.generateFrames(eulerRotation)
SIM.stitchVideo()