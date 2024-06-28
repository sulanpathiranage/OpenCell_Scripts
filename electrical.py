# AD2 FUNCTIONS
import numpy as np
import math as m
from sklearn.preprocessing import StandardScaler
import scipy.signal

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

def czt(x, m=None, w=None, a=None):
    n = len(x)

    if m is None: m = n
    if w is None: w = np.exp(-2j * np.pi / m)
    if a is None: a = 1.

    w_exponents_1 =   np.arange(    0   , n) ** 2 / 2.0    # n elements         [ 0 .. (n - 1) ]
    w_exponents_2 = - np.arange(-(n - 1), m) ** 2 / 2.0    # m + n - 1 elements [ -(n - 1) .. +(m - 1) ]
    w_exponents_3 =   np.arange(    0   , m) ** 2 / 2.0    # m elements         [ 0        ..  (m - 1) ]

    xx = x * a ** -np.arange(n) * w ** w_exponents_1

    # Determine next-biggest FFT of power-of-two.
    nfft = 1
    while nfft < (m + n - 1):
        nfft += nfft

    # Perform CZT.
    fxx = np.fft.fft(xx, nfft)
    ww = w ** w_exponents_2
    fww = np.fft.fft(ww, nfft)
    fyy = fxx * fww
    yy = np.fft.ifft(fyy, nfft)

    # Select output.
    yy = yy[n - 1 : m + n - 1]
    y = yy * w ** w_exponents_3

    return y

def czt_range(x, m, fmin, fmax, fs=None):
    if fs is not None:
        fmin /= fs
        fmax /= fs

    a = np.exp(fmin * 2 * np.pi * 1j)  # first frequency
    w = np.exp(-(fmax - fmin) / (m - 1) * 2 * np.pi * 1j)  # frequency step

    return czt(x, m, w, a)

def frequency(voltage:list, samplingRate):
    v= np.array(voltage)
    demeanedV = v - np.mean(v)
    N = len(demeanedV)
    v_jw = np.fft.fft(demeanedV)
    idx_peak = np.argmax(np.abs(v_jw[:N//2]))
    freqAxis = np.fft.fftfreq(N, 1/samplingRate)[:N//2]
    freqPeak = freqAxis[idx_peak]
    return freqPeak

def czt_wrapper(x, m, fmin, fmax, fs):
    a = np.exp(fmin*2*np.pi*1j)
    w = np.exp(-(fmax-fmin)/(m-1)*2*np.pi*1j)
    freqAxis = np.linspace(fmin, fmax, m)
    return scipy.signal.czt(x, m, w, a), freqAxis

def frequencyCZT(voltage:list, fmin, fmax, samplingRate):
    v = np.array(voltage)
    demeanedV = v - np.mean(v)
    m = 4096  # Ensure m is an integer

    chirpTransform, freqAxis = czt_wrapper(demeanedV, m, fmin, fmax, samplingRate)  # Corrected: Pass m instead of N
    idx_peak = np.argmax(np.abs(chirpTransform))
    freq = freqAxis[idx_peak]
    return freq


def impedance(voltage_1: list, voltage_2: list):
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

def zAng(voltage_1: list, voltage_2: list):
    if len(voltage_1) == 0 or len(voltage_2) == 0:
        raise ValueError("Input voltage lists must not be empty")

    v1 = np.array(voltage_1)
    v2 = np.array(voltage_2)
    avg1 = np.mean(v1)
    avg2 = np.mean(v2)
    
    sum1 = 0
    sum2 = 0
    sum12 = 0
    
    for i in range(len(v1)):
        sum1 += (v1[i] - avg1) * (v1[i] - avg1)
        sum2 += (v2[i] - avg2) * (v2[i] - avg2)
        sum12 += (v1[i] - avg1) * (v2[i] - avg2)
    
    # Avoid division by zero
    if sum1 == 0 or sum2 == 0:
        raise ValueError("Variance of input voltage lists must not be zero")

    Zang = np.arccos(sum12 / np.sqrt(sum1 * sum2)) * (180 / np.pi)
    return Zang

def zMag(voltage_1:list, voltage_2:list, phase):
    v1 = np.array(voltage_1)
    v2 = np.array(voltage_2)
    vP2P = (10 * np.ptp(v1))  - np.ptp(v2)
    iP2P = np.ptp(v2)
    zReal = (vP2P/iP2P) * np.cos(phase)
    zImg =  (vP2P/iP2P) * np.sin(phase) * (-1)
    Zmag = np.sqrt((zReal**2)*(zImg**2))
    return Zmag

def calcPhase(voltage_1:list, voltage_2:list):
    v1 = np.array(voltage_1)
    v2 = np.array(voltage_2) 
    rdata = np.zeros((len(v1), 2))
    rdata[:,0] = v1
    rdata[:,1] = v2
    scaler = StandardScaler()
    scaler.fit(rdata)
    data = scaler.transform(rdata)
    c = np.cov(np.transpose(data))
    phi = np.arccos(c[0, 1])
    phaseDiffDeg = phi/np.pi*180

    return phaseDiffDeg
  
def power(voltage_1:list, voltage_2:list, phase):
    v1 = np.array(voltage_1)
    v2 = np.array(voltage_2)
    vP2P = 10 * np.ptp(v1)  - np.ptp(v2)
    iP2P = np.ptp(v2)
    powerMeasure = vP2P * iP2P * np.cos(phase*np.pi/180)/8
    return powerMeasure
    