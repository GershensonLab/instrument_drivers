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
from qcodes.instrument_drivers.HP.HP34401 import HP34401

class HP34401_DL1201(HP34401):
    
    def __init__(self, name, address, Gain,  **kw):

            super().__init__(name, address, **kw)
  
            self._Gain = Gain
            self.V_to_Vdut = lambda x: float(x)/self._Gain
            
            self.add_parameter('V',
                   label='Voltage',
                   unit = 'V',
                   get_cmd='READ?\n',
                   set_cmd = None,
                   get_parser=self.V_to_Vdut)

    def set_Gain(self, Gain):  
        self._Gain = Gain
        self.V_to_Vraw = lambda V: V/self._Gain
#        self.I.vals = vals.Numbers(1,1000)
          
##Testing our codes
#from qcodes.instrument.base import Instrument
#try:
#    Instrument.close_all()
#except KeyError:
#    pass    
#except NameError:
#    pass  
#
#meter = HP34401_1201('meter3', 'GPIB0::8::INSTR', 100)
##meter.init('fast 6')
#print(meter2.V.get())