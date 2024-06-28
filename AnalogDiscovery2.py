#Abstract AD2 sensor

import device
import scope
import signalProcessing as dsp


class AD2_sensor:
    def __init__(self):
        self.device = device.open()
        scope.open(self.device)
        scope.trigger(self.device, enable=True, source=scope.trigger_source.analog, channel=1, level=0)
        self.voltage_list_1 = []
        self.voltage_list_2 = []
        self.sampling_rate = scope.data.sampling_frequency

    def getVoltageReading(self):
        #Retrieve voltage readings from AD2 using scope.measure()
        #INPUT
        self.voltage_1 = scope.measure(self.device, channel=1)
        self.voltage_2 = scope.measure(self.device, channel=2)
        return self.voltage_1, self.voltage_2
    
    def getVoltageArray(self):
        self.buffer_ch1 = scope.record(self.device, 1)
        self.buffer_ch2 = scope.record(self.device, 2) 


        return self.buffer_ch1, self.buffer_ch2
        
    def getFreq(self, voltage:list):
        freq = dsp.frequencyCZT(voltage, self.sampling_rate)
        return freq
    
    def getFreqImpPower(self):
        buffer_ch1 = scope.record(self.device, 1)
        buffer_ch2 = scope.record(self.device, 2)     
        freq = dsp.frequencyCZT(buffer_ch1, self.sampling_rate)
        zMag, zAng =  dsp.impCZT(buffer_ch1, buffer_ch2, freq, self.sampling_rate)
        power = dsp.power(buffer_ch1, buffer_ch2, zAng)
        return freq, zMag, zAng, power

    
