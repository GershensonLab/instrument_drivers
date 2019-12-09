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

class Keithley_6220(VisaInstrument):
    
    def __init__(self, name, address,  **kw):

            super().__init__(name, address, **kw)
    
            self.add_parameter('I',
                   label='Current',
                   unit = 'A',
                   get_cmd = None,
                   set_cmd='SOUR:CURR:AMPL '+'{}',
                   vals=vals.Numbers(-1e-6, 1e-6),
                   set_parser=float)

    def init(self):
        lines = ['*RST;',
                 'SOUR:CURR:RANG:AUTO OFF',
                 'SOUR:CURR:RANG 1e-6',
                 'SOUR:CURR:COMP 21',
                 'SOUR:CURR:AMPL 0',
                 'OUTP ON']

        for l in lines:
            self.write_raw(l)
            time.sleep(0.2)
            
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
#gen = Tektronix_AWG3252('gen', 'TCPIP0::192.168.13.32::inst0::INSTR')
#gen.init()
#gen.V.set(0.324)