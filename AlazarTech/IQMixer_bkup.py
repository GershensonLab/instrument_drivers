# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 18:12:01 2019

@author: kvk
"""
from contextlib import contextmanager

from qcodes.instrument.base import Instrument
from qcodes.utils.validators import Numbers
import qcodes.utils.validators as vals
import time

#from .ATS import AlazarTech_ATS, Buffer
import ctypes 

#from qcodes.plots.pyqtgraph import QtPlot

#from qcodes.instrument_drivers.AlazarTech.ATS import *

import numpy as np
#import qcodes as qc


import matplotlib.pyplot as plt

def fff():
    return 3

class IQMixer(Instrument):
    """
    some constnats here
    

    """
        
    def __init__(self, name: str, ats,  sgen1 , sgen2, aeroflex, **kwargs ):
                 
                 
#                 dll_path: str=None, alt_dll_path: str=None, **kwargs) -> None:
        super().__init__(name, **kwargs)
        



#        self.N_avg =  4000
        
        self.sgen1 = sgen1
        self.sgen2 = sgen2
        
        self.aeroflex = aeroflex
        self.aeroflex_CH_map = {'In' : 'CH1', 'Out': 'CH2'}
        
        self.ats = ats


        self.N_pts =  ats.samples_per_record

        self.delta_frequency = 3.0303e7 
        
#        self.S21_ = S21_ampl_phase(ats)  
#        self.S21_.N_pts = self.N_pts
#        self.S21_.delta_frequency = self.delta_frequency
        
        
        self.add_parameter(name='frequency',        
                           label='fprobe',
                           unit='Hz',
                           get_cmd=None,     # get freq in MHz
                           set_cmd = self.set_IQfrequency , #set greq in range F1 in GHz
                           vals=Numbers(min_value=1e3,
                                        max_value=40e9))


        self.add_parameter(name='S21',        
                           label='S21',
#                           unit='Hz',
                           get_cmd = self.get_S21,     
                           set_cmd = None) 
        
        self.add_parameter(name='S21_ampl',        
                   label='S21 amplitude',
                           unit='V',
                   get_cmd =  self.get_S21ampl,     
                   set_cmd = None) 


        self.add_parameter(name='S21_phase',        
                   label='S21 phase',
                           unit='rad',
                   get_cmd =  self.get_S21phase,     
                   set_cmd = None) 
        
        self.add_parameter(name='S21_I',        
                   label='S21 I',
                           unit='V',
                   get_cmd =  self.get_S21I,     
                   set_cmd = None) 


        self.add_parameter(name='S21_Q',        
                   label='S21 Q',
                           unit='V',
                   get_cmd =  self.get_S21Q,     
                   set_cmd = None) 
                

        for io, ch in self.aeroflex_CH_map.items():
            self.add_parameter('att{}'.format(io),
                           label='att {}'.format(io),
                           unit = 'dB',
                           get_cmd= getattr(self.aeroflex,
                                            'attenuation{}'.format(ch)).get,     # 
                           set_cmd= getattr(self.aeroflex,
                                            'attenuation{}'.format(ch)).set,     # 
                           vals=vals.Enum(*np.arange(0, 60.1, 2).tolist() ))
                
 
        
    def set_IQfrequency(self, fr):
        
        self.sgen1.frequency.set(fr)
        self.sgen2.frequency.set(fr - self.delta_frequency)
        time.sleep(0.05)

    
    def plot_raw(self):
        
        data = self.ats.get_averaged()
        
        print('avg data acquired')
        f, a = plt.subplots()
        plt.plot(data)
        print('aa')
        
        return data
        
    
    def get_S21(self ):
        
        
        N_pts = self.N_pts
#        N_avg = self.N_avg
        
        s = self.ats.sample_rate.get()
    
        t = np.arange(N_pts)
        
        I = np.cos(2*np.pi*self.delta_frequency*t/s)
        Q = np.sin(2*np.pi*self.delta_frequency*t/s)
        
#        out = np.array([])
        



            
        data = self.ats.get_averaged()


        
        dataCHA = data[:N_pts]
        dataCHB = data[N_pts:]
        
        rangeCHA = self.ats.channel_range1.get()
        rangeCHB = self.ats.channel_range2.get()
        
#        if (any(dataCHA) > 254 ) or (any(dataCHA) < 2):
#            print ('Data overranged, please check CHA range')
        
        voltCHA = (dataCHA - 127.5)/127.5*rangeCHA
        voltCHB = (dataCHB - 127.5)/127.5*rangeCHB
    
    
        I_CHA = np.sum(I * voltCHA)/N_pts
        Q_CHA = np.sum(Q * voltCHA)/N_pts
    
        I_CHB = np.sum(I * voltCHB)/N_pts
        Q_CHB = np.sum(Q * voltCHB)/N_pts
        
        amplitude_CHA = np.absolute (I_CHA + 1j*Q_CHA)
        phase_CHA = np.angle (I_CHA + 1j*Q_CHA)
    
#        amplitude_CHB = np.absolute (I_CHB + 1j*Q_CHB)
        phase_CHB = np.angle (I_CHB + 1j*Q_CHB)
    
        self.S21.ampl = 2*amplitude_CHA  # coeff 2 is taken from calibration
        self.S21.phase =  phase_CHA -  phase_CHB
        
        
        
#        plt.plot(data)
        
        return self.S21
    
    def get_S21ampl( self ):  

        return self.get_S21().ampl

    
    def get_S21phase(self ):  
        return self.get_S21().phase
    
    
    def get_S21I( self ): 
        
        S21 = self.get_S21()

        return S21.ampl * np.sin( S21.phase )

    
    def get_S21Q( self ): 
        
        S21 = self.get_S21()

        return S21.ampl * np.cos( S21.phase )
    
 
    
    
    def calc_IQ(self, data, start = 0, windowsize = None):
        
        
        
        N_pts =  len(data)
        
        if windowsize is None:
            windowsize = N_pts
            
            
            
        dataCHA = data[:N_pts]
        dataCHB = data[N_pts:]

        dataCHA_w = dataCHA [start : start + windowsize]
        dataCHB_w = dataCHA [start : start + windowsize]

        
        
        s = self.ats.sample_rate.get()
    
        t = np.arange(windowsize)
        


        I = np.cos(2*np.pi*self.delta_frequency*t/s)
        Q = np.sin(2*np.pi*self.delta_frequency*t/s)
        
        

        
        rangeCHA = self.ats.channel_range1.get()
        rangeCHB = self.ats.channel_range2.get()
        
#        if (any(dataCHA) > 254 ) or (any(dataCHA) < 2):
#            print ('Data overranged, please check CHA range')
        
        voltCHA = (dataCHA_w - 127.5)/127.5*rangeCHA
        voltCHB = (dataCHB_w - 127.5)/127.5*rangeCHB
    
    
        I_CHA = np.sum(I * voltCHA)/N_pts
        Q_CHA = np.sum(Q * voltCHA)/N_pts
    
        I_CHB = np.sum(I * voltCHB)/N_pts
        Q_CHB = np.sum(Q * voltCHB)/N_pts
        
        amplitude_CHA = np.absolute (I_CHA + 1j*Q_CHA)
        phase_CHA = np.angle (I_CHA + 1j*Q_CHA)
    
#        amplitude_CHB = np.absolute (I_CHB + 1j*Q_CHB)
        phase_CHB = np.angle (I_CHB + 1j*Q_CHB)
    
        self.S21.ampl = 2*amplitude_CHA  # coeff 2 is taken from calibration
        self.S21.phase =  phase_CHA -  phase_CHB    
            
        
        
    
    
    
    @contextmanager    
    def get_prepared_TD(self, N_windows,  windowsize = 512):

        channelMask = 3 
        
        self.N_windows = N_windows
#        self.number_of_averaging =  1
#        self.number_of_buffers =  1
# 
        self.windowsize = windowsize
        
        N_pts = windowsize*N_windows
    
        dmaBufferCount = 8
        
        ats = self.ats
        acqperiod = ats.sample_rate.get()
        
        rangeCHA = ats.channel_range1.get()
        rangeCHB = ats.channel_range2.get()

        ats._call_dll('TD_ATS_ConfigCapture',  #from ATS_Average_IQTimeDomain_DLL
                          ats._handle,
                          channelMask,
                          N_pts, 
                          1,
                          1,
                          dmaBufferCount,
                          int(self.delta_frequency), 
                          acqperiod ,
                          self.windowsize, 
                          ctypes.c_float(rangeCHA),
                          ctypes.c_float(rangeCHB) )
        
        self.Prepared = True


        try:
            yield 
        finally:
            ats._call_dll('TD_ATS_StopCapture',  #from ATS_Average_IQTimeDomain_DLL
                                  ats._handle)
            ats.Prepared = False
            print('\n Card resources were released\n')       

        
    def start_capturing_TD(self):

        ats = self.ats
        ats._call_dll('AlazarStartCapture',  #from ATSApi
                       ats._handle)  
        




    """
    read captured and averaged value from ats
    """
    def do_TD(self):   

        c_I = ctypes.c_float   * int( self.N_windows) 
        c_Q = ctypes.c_float   * int( self.N_windows)  
        
        ats = self.ats
        

        timeout_ms = 5000
#        number_of_channels = 2  
        

        if self.Prepared:


#            c_sample_type =  ctypes.c_float
#            size_bytes = 4 
#            npSampleType = np.float32
#            
#            bytes_per_point = size_bytes * self.N_windows
#            
#            ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_float
#            
#            MEM_COMMIT = 0x1000
#            PAGE_READWRITE = 0x4
#            
#            tI_addr = ctypes.windll.kernel32.VirtualAlloc(
#                0, ctypes.c_float(bytes_per_point), MEM_COMMIT, PAGE_READWRITE)
#            
#            tQ_addr = ctypes.windll.kernel32.VirtualAlloc(
#                0, ctypes.c_float(bytes_per_point), MEM_COMMIT, PAGE_READWRITE)
#            
#            ctypes_arrayI = (c_sample_type * self.N_windows ).from_address(tI_addr)
#            ctypes_arrayQ = (c_sample_type * self.N_windows).from_address(tQ_addr)
#            
#            self.npI = np.frombuffer(ctypes_arrayI, dtype=npSampleType)
#            self.npQ = np.frombuffer(ctypes_arrayQ, dtype=npSampleType)

            
            try:
#                ats._call_dll('TD_ATS_GetAverageBuffer',     #from ATS_Average_NPT_custom_DLL
#                              ats._handle,
#                              ctypes.cast(tI_addr, ctypes.c_float),
#                              ctypes.cast(tQ_addr, ctypes.c_float),
#                              timeout_ms)
#                
#                    
#                outputI = self.npI
#                outputQ = self.npQ
                
                
                ats._call_dll('TD_ATS_GetAverageBuffer',     #from ATS_Average_NPT_custom_DLL
                              ats._handle,
                              ctypes.byref (c_I),
                              ctypes.byref( c_Q),
                              timeout_ms)
 

#                print(  outputI.value , outputQ.value )


            finally:
#                
#                MEM_RELEASE = 0x8000
#                ctypes.windll.kernel32.VirtualFree.restype = ctypes.c_float
#                ctypes.windll.kernel32.VirtualFree(ctypes.c_float(tI_addr), 0, MEM_RELEASE)
#                ctypes.windll.kernel32.VirtualFree(ctypes.c_float(tQ_addr), 0, MEM_RELEASE)
                
                print('I and Q memory have been released')  
        else:
            print('Board is not prepared for capturing')        
        
        
        outputI = []
        outputQ = []
        
        
        for i in range(self.N_windows):
            outputI.append( c_I[i].value )
            outputQ.append( c_Q[i].value )

             
        return np.array(outputI) , np.array(outputQ)
      
        
        
    def get_ampl_TD(self):
            
        I, Q = self.do_TD()
        
        return (I**2 + Q**2)**0.5


        
        

        

    