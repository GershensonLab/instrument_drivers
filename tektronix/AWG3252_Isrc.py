# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 15:14:17 2019

@author: KelvinOX25
"""

import pyvisa
import time
import logging
import numpy as np
import struct
from qcodes import VisaInstrument, validators as vals
from qcodes.instrument_drivers.tektronix.AWG3252 import Tektronix_AWG3252

class AWG3252_Isrc(Tektronix_AWG3252):
    
    def __init__(self, name, address, R_bias, Attn,  **kw):

            super().__init__(name, address, **kw)
    
            self._Attn = Attn
            self._R_bias = R_bias
            self.I_to_V = lambda i: i*self._R_bias*self._Attn
            
            self.add_parameter('I',
                   label='Current',
                   unit = 'A',
                   get_cmd = None,
                   set_cmd= self.V.set,
                   vals=vals.Numbers(-4/self._R_bias/self._Attn, 4/self._R_bias/self._Attn),
                   set_parser= self.I_to_V)

    def set_R_Attn(self, R_bias, Attn):  
        self._Attn = Attn
        self._R_bias = R_bias
        self.I_to_V = lambda i: i*self._R_bias*self._Attn
        self.I.vals = vals.Numbers(-4/self._R_bias/self._Attn, 4/self._R_bias/self._Attn)
          
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
