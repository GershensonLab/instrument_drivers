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

class Tektronix_AWG3252(VisaInstrument):
    
    def __init__(self, name, address,  **kw):

            super().__init__(name, address, **kw)
    
            self.add_parameter('V',
                   label='Voltage',
                   unit = 'V',
                   get_cmd = None,
                   set_cmd=':SOUR1:VOLT:OFFS '+'{}'+'V;',
                   vals=vals.Numbers(-4, 4),
                   set_parser=float)

    def init(self):
        lines = ['*RST;',
                 ':SOUR1:FUNC:SHAP DC;',
                 ':SOUR1:VOLT:OFFS 0V;',
                 ':OUTP1:IMP INF;',
                 ':OUTP1:STAT on;']

        for l in lines:
            self.write_raw(l)
            time.sleep(0.2)

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