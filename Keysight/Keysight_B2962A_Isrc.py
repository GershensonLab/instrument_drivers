# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:04:01 2020

@author: KelvinOX25
"""



import pyvisa
import time
import logging
import numpy as np
import struct
from qcodes import VisaInstrument, validators as vals
from qcodes.instrument_drivers.Keysight.Keysight_B2962A import B2962A

class B2962A_Isrc(B2962A):
    
    def __init__(self, name, address):

            super().__init__(name, address)
            
            self.ch1.source_mode.set('current')
            
            self.ch2.enable.set('off')
            
            
            self.add_parameter('I_limit',
                   get_cmd = self.ch1.current_limit.get,
                   get_parser=float,
                   set_cmd= self.ch1.current_limit.set,
                   unit='A')

            self.add_parameter('enable',
                           get_cmd= self.ch1.enable.get,
                           set_cmd= self.ch1.enable.set)
    
            
            self.add_parameter('I',
                   label='Current',
                   unit = 'A',
                   get_cmd = self.ch1.source_current.get,
                   set_cmd= self.ch1.source_current.set)
            
            self.ch2.enable.set('off')

    def set_R_Attn( self, R_bias, Attn ):
        pass
          
##Testing our codes
#from qcodes.instrument.base import Instrument
#try:
#    Instrument.close_all()
#except KeyError:
#    pass    
#except NameError:
#    pass  
#
#gen = AWG3252_Isrc('gen', 'TCPIP0::192.168.13.32::inst0::INSTR',  R_bias = 1e9, Attn=1)
#gen.I.set(1e-9) #we expected to see 1V from AWG
#gen.set_R_bias (1e8, Attn=10)
#time.sleep(1)
#gen.I.set(0.3e-8) #we expected to see 3V from AWG
#gen.set_R_bias (1e9, Attn=1)
#time.sleep(1)
#gen.I.set(0)
