import tkinter as tk
from tkinter import ttk
import time
import numpy as np
import datetime
from AnalogDiscovery2 import AD2_sensor
from mass_balance import balance
import electrical as e
import csv
import scope, device
from device import error

# Variables
MASS_BALANCE_PORT = "COM3"
BAUDRATE = 9600
SAMPLE_RATE_AD2 = 100
MEASURE_AD2_TIME = 1/SAMPLE_RATE_AD2
SAMPLE_RATE_BALANCE = 11
MEASURE_BALANCE_TIME = 1/SAMPLE_RATE_BALANCE
DISPLAY_LOOP_TIME = 0.5  # Display values every 1/2 second
MINIMUM_FREQ = 80000
MAXIMUM_FREQ = 120000

filename = input("Please name CSV file: ")

file = filename + ".csv"
text = open(file, 'w', newline='')
writer = csv.writer(text)
writer.writerow(['Timestamp', 'Elapsed Time', 'Frequency', 'Mass', 'Flowrate', 'Phase', 'Impedance', 'Power', 'Voltage', 'Current'])
text.close()

class LiveDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Data Display")

        self.label_phase = ttk.Label(root, text="Phase: ")
        self.label_phase.grid(row=0, column=0)
        self.value_phase = ttk.Label(root, text="")
        self.value_phase.grid(row=0, column=1)

        self.label_impedance = ttk.Label(root, text="Impedance: ")
        self.label_impedance.grid(row=1, column=0)
        self.value_impedance = ttk.Label(root, text="")
        self.value_impedance.grid(row=1, column=1)

        self.label_power = ttk.Label(root, text="Power: ")
        self.label_power.grid(row=2, column=0)
        self.value_power = ttk.Label(root, text="")
        self.value_power.grid(row=2, column=1)

        self.label_voltage = ttk.Label(root, text="Voltage: ")
        self.label_voltage.grid(row=3, column=0)
        self.value_voltage = ttk.Label(root, text="")
        self.value_voltage.grid(row=3, column=1)

        self.label_frequency = ttk.Label(root, text="Frequency: ")
        self.label_frequency.grid(row=4, column=0)
        self.value_frequency = ttk.Label(root, text="")
        self.value_frequency.grid(row=4, column=1)

        self.label_flowrate = ttk.Label(root, text="Flow Rate: ")
        self.label_flowrate.grid(row=5, column=0)
        self.value_flowrate = ttk.Label(root, text="")
        self.value_flowrate.grid(row=5, column=1)

    def update_values(self, zAng, zMag, power, voltage, freq, flowReading):
        self.value_phase.config(text=str(zAng))
        self.value_impedance.config(text=str(zMag))
        self.value_power.config(text=str(power))
        self.value_voltage.config(text=str(voltage))
        self.value_frequency.config(text=str(freq))
        self.value_flowrate.config(text=str(flowReading))
        self.root.update()

try:
    AD2 = device.open()
    scope.open(AD2, amplitude_range=5, sampling_frequency=20000000)
    scope.trigger(AD2, enable=True, source=scope.trigger_source.analog, channel=1, level=0)
    massBalance = balance(MASS_BALANCE_PORT, BAUDRATE)
    print("Connected!")

    # Initialize Tkinter
    root = tk.Tk()
    gui = LiveDisplay(root)

    startTime = time.time()
    nextMeasureAD2Time = startTime
    nextMeasureBalanceTime = startTime
    nextDisplayTime = startTime

    while True:
        currentTime = time.time()
        if currentTime >= nextMeasureAD2Time:
            buffer1 = scope.record(AD2, 1)
            buffer2 = scope.record(AD2, 2)

            m = 40000
            samplingRate = scope.data.sampling_frequency
            czt_voltage = e.czt_range(buffer1, m, MINIMUM_FREQ, MAXIMUM_FREQ, samplingRate)
            frequencies = np.linspace(MINIMUM_FREQ, MAXIMUM_FREQ, m)
            idx_peak = np.argmax(np.abs(czt_voltage))
            freq = round(frequencies[idx_peak] - 10)
            zMag, zAng = e.impedance(buffer1, buffer2)
            power = e.power(buffer1, buffer2, zAng)
            nextMeasureAD2Time = currentTime + MEASURE_AD2_TIME

        if currentTime >= nextMeasureBalanceTime:
            systemTime = datetime.datetime.now()
            timestampString = systemTime.strftime("%H:%M:%S.%f")[:-3]
            voltageCh1 = scope.measure(AD2, channel=1)
            voltageCh2 = scope.measure(AD2, channel=2)
            massReading = massBalance.readBalance()
            flowReading = massBalance.readFlow()
            nextMeasureBalanceTime = currentTime + MEASURE_BALANCE_TIME
            deltaTime = time.time() - startTime
            text = open(file, 'a', newline='')
            writer2 = csv.writer(text)
            writer2.writerow([timestampString, deltaTime, freq, massReading, flowReading, zAng, zMag, power, voltageCh1, voltageCh2])
            text.close()

        if currentTime >= nextDisplayTime:
            voltageCh1 = scope.measure(AD2, channel=1)
            voltageCh2 = scope.measure(AD2, channel=2)
            massReading = massBalance.readBalance()
            flowReading = massBalance.readFlow()
            gui.update_values(zAng, zMag, power, abs(np.ptp(buffer1)), freq, flowReading)
            nextDisplayTime = currentTime + DISPLAY_LOOP_TIME

        root.update_idletasks()
        root.update()

except error as e:
    print(e)
    # Close connection
    AD2.close()
