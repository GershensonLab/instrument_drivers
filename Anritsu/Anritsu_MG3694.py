# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 14:02:12 2019

@author: kvk
"""

#from qcodes.instrument_drivers.AlazarTech.ATS9870 import *
#from qcodes.instrument_drivers.AlazarTech.ATS_acquisition_controllers import *
#from qcodes.instrument_drivers.AlazarTech.ATS import *
#
#from qcodes.instrument_drivers.HP.HP_83650A import *


from qcodes import VisaInstrument
from qcodes.utils.validators import Numbers
import numpy as np
import qcodes as qc
#import matplotlib.pyplot as plt


class Anritsu(VisaInstrument):
    """
    This is the code for Anritsu MG3694 Signal Generator
    """

    def __init__(self, name, address, reset=False,  **kwargs):
        super().__init__(name, address,  terminator='\n', **kwargs)
# general commands
        self.add_parameter(name='frequency',
                           label='Frequency',
                           unit='Hz',
                           get_cmd='OF1',     # get freq in MHz
                           set_cmd='CF1 {} GH', #set greq in range F1 in GHz
                           set_parser= lambda x: x/1e9,
                           get_parser= lambda x: float(x)*1e6 ,
                           vals=Numbers(min_value=1e3,
                                        max_value=40e9))
        self.add_parameter(name='power',
                           label='Power',
                           unit='dBm',
                           get_cmd='OL1',
                           set_cmd='XL1 {} DM',
                          get_parser=float,
                           vals=Numbers(min_value=-999,
                                        max_value=20))
        self.add_parameter('mode',
                           label='Mode',
                           set_cmd='{}',
#                           get_cmd='FREQ:MODE?',
                           val_mapping = {  'Pulse' : 'XP', 'CW' : 'P0' } )   # ON/OFF pulse modulation
        self.add_parameter('rf_switch',
                           label='Rf_switch',
#                           unit='ns',
                           set_cmd='{}',
#                           get_cmd=!'PULM:INT:PWID?',
                           val_mapping ={ 'ON' : 'RF1', 'OFF' :'RF0'})  # ON/OFF RF signal
        
      ############## 
    

#        
#    def RFswitch(self,option):
#        if option=='ON':
#            self.write('RF1')
#        else:
#            self.write('RF0')
#    def setMode(self, mode='CW'):
#
#        if mode =='CW':
#            self.write('P0')
#        elif mode =='PUL':
#            self.write('XP')
#        else:
#            raise ValueError('mode not in list')
##        self.write('PTR PTG4') # trigger on rising edge
##        self.write('PMD1') # single pulse mode
##        self.write('PW 100 MS')
#            
