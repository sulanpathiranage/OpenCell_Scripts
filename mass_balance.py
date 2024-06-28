#Mass-Balance class
import serial
import re
import statistics
import time


class balance:

    def __init__(self, port, baudrate):
        #DEFINE variables 
        self.port = port
        self.baudrate = baudrate
        self.timeArray = []
        self.massArray=[]    
        self.sensor = serial.Serial(port, baudrate)
        self.initialTime = time.time()
        self.flowrate = [0,0,0,0,0,0,0,0,0,0]

    def readBalance(self):
        line = self.sensor.readline().decode().strip()
        x=re.findall(r"[-+]?\d*\.?\d+|\d+",line)
        mass = float(x[0])
        self.massArray.append(mass)
        measureTime = time.time()
        self.deltaTime = measureTime-self.initialTime
        self.timeArray.append(self.deltaTime)
        return mass
    def readFlow(self):
        if len(self.massArray) > 10:
            k = len(self.massArray)-1
            avgFlowrate = 60*((self.massArray[k]-self.massArray[k-10])/(self.timeArray[k]-self.timeArray[k-10]))
            #self.flowrate.append(60*((self.massArray[k]-self.massArray[k-10])/(self.timeArray[k]-self.timeArray[k-10])))
            #self.massArray = self.massArray[-10:]
        else: 
            avgFlowrate = 0
        #mostRecentFlow = self.flowrate[-10:]
        #avgFlowrate = statistics.mean(mostRecentFlow)
        return avgFlowrate

    
