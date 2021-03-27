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


class IQMixer(Instrument):
    """
    Class containing all ingredients (two signal gerenrtors, attenuator, digitizing card) for measuring S21 parameter by ATS
    in heterodyne regime
    Parameters:
        ats : ATS_Alazar digitizing card Instrument
        sgen1 : probe tone generator Instrument
        sgen2 : heterodyne for downconverion Instrument
        aeroflex : attenuator Instrument

    """
        
    def __init__(self, name: str, ats,  sgen1 , sgen2, aeroflex, **kwargs ):
                 
        super().__init__(name, **kwargs)
        self.sgen1 = sgen1
        self.sgen2 = sgen2
        
        self.aeroflex = aeroflex
        self.aeroflex_CH_map = {'In' : 'CH1', 'Out': 'CH2'}
        
        self.ats = ats
        self.delta_frequency = ats.delta_frequency

        self.rangeCHA = self.ats.channel_range1.get()
        self.rangeCHB = self.ats.channel_range2.get()

        self.add_parameter(name='frequency',        
                           label='fprobe',
                           unit='Hz',
                           get_cmd=None,     # get freq in MHz
                           set_cmd = self.set_IQfrequency , #set freq in range F1 in GHz
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

    
    def plot_raw(self, ch = 'A'):
        
        data = self.ats.get_averaged()
        
        N_pts = int(len(data)/2)
        
        print('avg data acquired')
        f, ax = plt.subplots()
        if ch == 'A':
            ax.plot(data[:N_pts], 'x-')
        if ch == 'B':

            ax.plot(data[N_pts:], 'x-')
        return data

    def calc_IQ_verbose(self, data,  N_pts = None, N_w = 1):
        
                                      # data - [chA, chB]  
        ats = self.ats
        if N_pts is None:
            N_pts =  int( len(data) / 2)  
            
        self.N_pts_w = N_pts #points per window
        
        data2 = np.tile(data , (1,2) ) #[[chA, chB, chA, chB]] 

        print ('tile  ',data2)
        fig, ax = plt.subplots()        
        ax.plot(data2[0,:])
        
        data3 = np.reshape(data2, (4,N_w, N_pts )) #[ [chA_0],[chA_1].. [chB_0],[chB_1].., [chA_0],[chA_1].. [chB_0],[chB_1]..]
        
        print ('rehape tile', data3)

        fig, ax = plt.subplots()        
        ref = np.reshape(ats.ref_IQ, (4,N_w, N_pts ) )

        print ( 'ref  ', ref )

        for k in range(2):
            ax.plot(data3 [k,0,:], c = 'C{}'.format(k))
            ax.plot(ref [k,0,:] , c = 'C{}'.format(k))        

        data_prod = data3 * ref

        fig, ax = plt.subplots()        
        ax.plot(data_prod[0,0,:])
        ax.plot(data_prod[2,0,:])
        print ('after product  ',  data_prod )

        dataIQ = np.sum( data_prod, axis = 2 )

        print ('after summ',  dataIQ )

        out  = dataIQ# np.transpose( np.reshape(dataIQ, (4, N_w) ))
        I_CHA, Q_CHB , Q_CHA, I_CHB = dataIQ
        
        print('ICHA, QCHA',  I_CHA,  Q_CHA)
        print( 'np.abs  ',    np.absolute (I_CHA + 1j*Q_CHA) )

        return out #[[I_a0, Q_b0,Q_a0, I_b0], [I_a1, Q_b1,Q_a1, I_b1] ...] 
        


    def calc_IQ(self, data,  N_pts = None, N_w = 1):
        
                                      # data - [chA, chB]  
        ats = self.ats
        
        if N_pts is None:
            N_pts =  int( len(data) / 2)  
            
        self.N_pts_w = N_pts #points per window
        
        data2 = np.tile(data, (1,2) ) #[chA, chB, chA, chB] 
        data3 = np.reshape(data2, (4,N_w, N_pts )) #[ [chA_0],[chA_1].. [chB_0],[chB_1].., [chA_0],[chA_1].. [chB_0],[chB_1]..]

        ref = np.reshape(ats.ref_IQ, (4, N_w, N_pts ) )
        
        dataIQ = np.sum( data3 * ref, axis = 2 ) 
        
        out  = dataIQ# np.transpose( np.reshape(dataIQ, (4, N_w) ))

        return out #[[I_a0, Q_b0,Q_a0, I_b0], [I_a1, Q_b1,Q_a1, I_b1] ...] 

    def norm(self):
        
        rA = self.rangeCHA
        rB = self.rangeCHB

        norm = np.array([rA, rB, rA, rB ]) / 128**2 / self.N_pts_w
        return norm
    

    def calcS21_fromIQ(self, I_CHA, Q_CHB , Q_CHA, I_CHB):

        amplitude_CHA = np.absolute (I_CHA + 1j*Q_CHA)
        phase_CHA = np.angle (I_CHA + 1j*Q_CHA)
        phase_CHB = np.angle (I_CHB + 1j*Q_CHB)
    
        ampl = 1.0*amplitude_CHA  # coeff 1.25 is taken from calibration
        phase =  phase_CHA -  phase_CHB 
        
        return ampl, phase

    def get_S21( self ):
        data = self.ats.get_averaged()
        rawIQ = np.mean(self.calc_IQ( data ) , axis = 1)

        I_CHA, Q_CHB , Q_CHA, I_CHB  =  rawIQ * self.norm()
        ampl, phase = self.calcS21_fromIQ( I_CHA, Q_CHB , Q_CHA, I_CHB )
        
        self.S21.ampl = ampl 
        self.S21.phase =  phase

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

#    @contextmanager    
#    def get_prepared_TD(self, N_windows,  windowsize = 512):
#
#        channelMask = 3 
#        
#        self.N_windows = N_windows
##        self.number_of_averaging =  1
##        self.number_of_buffers =  1
## 
#        self.windowsize = windowsize
#        
#        N_pts = windowsize*N_windows
#    
#        dmaBufferCount = 8
#        
#        ats = self.ats
#        acqperiod = ats.sample_rate.get()
#        
#        rangeCHA = ats.channel_range1.get()
#        rangeCHB = ats.channel_range2.get()
#
#        ats._call_dll('TD_ATS_ConfigCapture',  #from ATS_Average_IQTimeDomain_DLL
#                          ats._handle,
#                          channelMask,
#                          N_pts, 
#                          1, #avg
#                          1, #buffer
#                          dmaBufferCount,
#                          int(self.delta_frequency), 
#                          acqperiod ,
#                          self.windowsize, 
#                          ctypes.c_float(rangeCHA),
#                          ctypes.c_float(rangeCHB) )
#        
#        self.Prepared = True
#
#
#        try:
#            yield 
#        finally:
#            ats._call_dll('TD_ATS_StopCapture',  #from ATS_Average_IQTimeDomain_DLL
#                                  ats._handle)
#            ats.Prepared = False
##            print('\n Card resources were released\n')       
#
#        
#    def start_capturing_TD(self):
#
#        ats = self.ats
#        ats._call_dll('AlazarStartCapture',  #from ATSApi
#                       ats._handle)  
#        
#
#
#
#
#    """
#    read captured and averaged value from ats
#    """
#    def do_TD(self): 
#        
#        
#        empty = [0 for i in range( self.N_windows)]
#        
#        c_I = (ctypes.c_float * int( self.N_windows)) (*empty)
#        c_Q = (ctypes.c_float * int( self.N_windows) )(*empty) 
#        
#        ats = self.ats
#        
#
#        timeout_ms = 5000
#
#        if self.Prepared:
#
#
#
#                
#                
#            ats._call_dll('TD_ATS_GetAverageBuffer',     #from ATS_Average_NPT_custom_DLL
#                          ats._handle,
#                          ctypes.byref (c_I),
#                          ctypes.byref( c_Q),
#                          timeout_ms)
# 
#        else:
#            print('Board is not prepared for capturing')        
#        
#        
#        outputI = []
#        outputQ = []
#        
#        
#        for i in range(self.N_windows):
#            outputI.append( c_I[i] )
#            outputQ.append( c_Q[i] )
#
#             
#        return np.array(outputI) , np.array(outputQ)
#      
#        
#        
#    def get_ampl_TD(self):
#            
#        I, Q = self.do_TD()
#        
#        return (I**2 + Q**2)**0.5
#
#
#        
#        

        

    