# AD2 FUNCTIONS
import numpy as np
import math as m
from sklearn.preprocessing import StandardScaler
import scipy.signal
import constants as c




def czt_wrapper(x, sampling_freq=None): 
    #interface for accessing chirp Z transform via scipy function (fastest option)
    if sampling_freq is not None:
        c.MIN_FREQ /= sampling_freq
        c.MAX_FREQ /= sampling_freq
    m = c.MAX_FREQ-c.MIN_FREQ
    a = np.exp(c.MIN_FREQ * 2 * np.pi * 1j)  # first frequency
    w = np.exp(-(c.MAX_FREQ - c.MIN_FREQ) / (m - 1) * 2 * np.pi * 1j)  # frequency step
    frequencies = np.linspace(c.MIN_FREQ, c.MAX_FREQ, m)
    return scipy.signal.czt(x, m, w, a), frequencies


def frequencyCZT(voltage:list, sampling_rate):
    #find frequency via CZT (10 Hz bins)
    v = np.array(voltage)
    demeanedV = v - np.mean(v)
    chirp_transform, freq_axis = czt_wrapper(demeanedV, sampling_rate) 
    idx_peak = np.argmax(np.abs(chirp_transform))
    freq = freq_axis[idx_peak]
    return freq

def impCZT(voltage1:list, voltage2:list, freq, samplingRate):
    #complex valued impedance via CZT, returns abs(Z), angle(Z) evaluated at current freq
    v = np.array(voltage1) #channel 1
    i = np.array(voltage2) #channel 2

    demeaned_V = v - np.mean(v)
    demeaned_I = i - np.mean(i)

    V_jw, freqAxis = czt_wrapper(demeaned_V, samplingRate) 
    I_jw, freqAxis = czt_wrapper(demeaned_I, samplingRate) 
    Z_jw = V_jw/I_jw

    idx_peak = np.argmax(np.abs(V_jw))
    Z_freq = Z_jw[idx_peak]  #complex impedance evaluated at freq
    resistance = np.abs(Z_freq)
    reactance = np.angle(Z_freq) 
    return resistance, reactance



  
def power(voltage_1:list, voltage_2:list, phase):
    v1 = np.array(voltage_1)
    v2 = np.array(voltage_2)
    vP2P = 10 * np.ptp(v1)  - np.ptp(v2)
    iP2P = np.ptp(v2)
    power_Measure = vP2P * iP2P * np.cos(phase*np.pi/180)/8
    return power_Measure

def impedance_WF(voltage_1: list, voltage_2: list):
    v1 = np.array(voltage_1[192:])
    v2 = np.array(voltage_2[192:])
    
    avg1 = np.mean(v1)
    avg2 = np.mean(v2)
    
    sum1 = np.sum((v1 - avg1) ** 2)
    sum2 = np.sum((v2 - avg2) ** 2)
    sum12 = np.sum((v1 - avg1) * (v2 - avg2))
    
    phase = np.degrees(np.arccos(sum12 / m.sqrt(sum1 * sum2)))

    vP2P = (10 * np.ptp(v1))  - np.ptp(v2)
    iP2P = np.ptp(v2)
    
    ZReal = (vP2P / iP2P) * m.cos(m.radians(phase))
    Zj = (vP2P / iP2P) * m.sin(m.radians(phase)) * -1
    Z = m.sqrt(ZReal ** 2 + Zj ** 2)
    
    return Z, phase

def impedance_fft(voltage_1:list, voltage_2:list):
#FFT to get impedance data(INPUT: Voltage streams)
    v1 = np.array(voltage_1[192:])
    v2 = np.array(voltage_2[192:])
    V_jw = np.fft.fftshift(v1) #V(jw) = fft(V(t))
    I_jw = np.fft.fftshift(v2) #Ch2 uses 1Ohm R : V = IR, V = 1I, V = I | I(jw) = fft(I(t))
    zComplex = V_jw/I_jw #Z(jw) = V(jw)/I(jw)
    zRArray = abs(zComplex)
    phaseArray = np.angle(zComplex)
    zRFinal = np.mean(zRArray)
    phaseRad = np.mean(phaseArray)
    phaseDegrees = np.degrees(phaseRad)
    
    return zRFinal, phaseDegrees