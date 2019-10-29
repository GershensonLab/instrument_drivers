# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 18:12:01 2019

@author: kvk
"""

from qcodes.instrument.base import Instrument
from qcodes.utils.validators import Numbers
import qcodes.utils.validators as vals
#from qcodes.plots.pyqtgraph import QtPlot

#from qcodes.instrument_drivers.AlazarTech.ATS import *

import numpy as np


import matplotlib.pyplot as plt
#import time
#import ctypes, os
#from qcodes.logger.logger import start_all_logging
#from RU_meas import *

#def call_dll(func_name,*args_out):
#    func = getattr(atsr._ATS_dll, func_name)
#    return_code = func(*args_out)


class IQMixer(Instrument):
    """
    some constnats here
    

    """
        
    def __init__(self, name: str, ats,  sgen1 , sgen2, aeroflex, **kwargs ):
                 
                 
#                 dll_path: str=None, alt_dll_path: str=None, **kwargs) -> None:
        super().__init__(name, **kwargs)

        self.N_pts =  8192
        self.N_avg =  4000
        
        self.sgen1 = sgen1
        self.sgen2 = sgen2
        
        self.aeroflex = aeroflex
        self.aeroflex_CH_map = {'In' : 'CH1', 'Out': 'CH2'}
        
        self.ats = ats

        self.delta_frequency = 3.0303e7 
        
        self.add_parameter(name='frequency',        
                           label='Frequency',
                           unit='Hz',
                           get_cmd=None,     # get freq in MHz
                           set_cmd = self.set_IQfrequency , #set greq in range F1 in GHz
                           vals=Numbers(min_value=1e3,
                                        max_value=40e9))


        self.add_parameter(name='S21',        
                           label='S21',
#                           unit='Hz',
                           get_cmd = self.get_S21,     # get freq in MHz
                           set_cmd = None) 


        for io, ch in self.aeroflex_CH_map.items():
            self.add_parameter('att{}'.format(io),
                           label='att {}'.format(io),
                           get_cmd= getattr(self.aeroflex,
                                            'attenuation{}'.format(ch)).get,     # 
                           set_cmd= getattr(self.aeroflex,
                                            'attenuation{}'.format(ch)).set,     # 
                           vals=vals.Enum(*np.arange(0, 60.1, 2).tolist() ))
                
 
        
    def set_IQfrequency(self, fr):
        
        self.sgen1.frequency.set(fr)
        self.sgen2.frequency.set(fr - self.delta_frequency)

        
    def get_S21(self ):
        
        
        N_pts = self.N_pts
#        N_avg = self.N_avg
        
        s = self.ats.sample_rate.get()
    
        t = np.arange(N_pts)
        
        I = np.cos(2*np.pi*self.delta_frequency*t/s)
        Q = np.sin(2*np.pi*self.delta_frequency*t/s)
        
#        out = np.array([])
        



            
        data = self.ats.get_averaged_new()



       
#        plt.plot(data)
        
        dataCHA = data[:N_pts]
        dataCHB = data[N_pts:]
        
        rangeCHA = self.ats.channel_range1.get()
        rangeCHB = self.ats.channel_range2.get()
        
        voltCHA = (dataCHA - 127.5)/127.5*rangeCHA
        voltCHB = (dataCHB - 127.5)/127.5*rangeCHB
    
    
        I_CHA = np.sum(I * voltCHA)/N_pts
        Q_CHA = np.sum(Q * voltCHA)/N_pts
    
        I_CHB = np.sum(I * voltCHB)/N_pts
        Q_CHB = np.sum(Q * voltCHB)/N_pts
        
        amplitude_CHA = np.absolute (I_CHA + 1j*Q_CHA)
        phase_CHA = np.angle (I_CHA + 1j*Q_CHA)
    
#        amplitude_CHB = np.absolute (I_CHB + 1j*Q_CHB)
        phase_CHB = np.angle (I_CHB + 1j*Q_CHA)
    
        self.S21.ampl = amplitude_CHA
        self.S21.phase =  phase_CHA -  phase_CHB
        
#        plt.plot(data)
        
        return self.S21