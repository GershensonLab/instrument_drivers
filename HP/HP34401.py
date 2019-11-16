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

class HP34401(VisaInstrument):
    
    def __init__(self, name, address,  **kw):

            super().__init__(name, address, **kw)
    
            self.add_parameter('Vraw',
                   label='Voltage',
                   unit = 'V',
                   get_cmd='READ?\n',
                   set_cmd = None,
                   get_parser=float)

    def init(self, reso, highZ = True):

        if highZ:
            self.write_raw('INP:IMP:AUTO ON\n')
        else:
            self.write_raw('INP:IMP:AUTO OFF\n')
        time.sleep(0.2)

        resodic = { 'slow 4' : ['*CLS\n*RST\n',
                                'CONF:VOLT:DC 1, 1E-4\n',
                                'VOLT:DC:NPLC 1\n',
                                'VOLT:RANG:AUTO ON\n'],
        
                    'fast 5' : ['*CLS\n*RST\n',
                                'CONF:VOLT:DC 10, 1E-5\n',
                                'VOLT:DC:NPLC 0.2\n',
                                'VOLT:RANG:AUTO ON\n'],
        
                    'fast 6' : ['*CLS\n*RST\n',
                                'CONF:VOLT:DC 10, 1E-5\n',
                                'VOLT:DC:NPLC 10\n',
                                'VOLT:RANG:AUTO ON\n'],
                            
                    'slow 6' : ['*CLS\n*RST\n',
                                'CONF:VOLT:DC 10, 1E-5\n',
                                'VOLT:DC:NPLC 100\n',
                                'VOLT:RANG:AUTO ON\n']}    
        try:
            for l in resodic[reso]:
                self.write_raw(l)
                time.sleep(0.2)
        except KeyError:
            print ('Allowed options: \'slow 4\', \'fast 5\', \'fast 6\', \'slow 6\'')
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
#meter = HP34401('meter', 'GPIB0::8::INSTR')
##meter.init('fast 6')
#print(meter.V.get())