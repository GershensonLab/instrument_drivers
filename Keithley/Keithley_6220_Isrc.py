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

class Keithley_6220_Isrc(VisaInstrument):
    
    def __init__(self, name, address,  Rsh, Rb, Vmeter, **kw):
            """
            child of KE6220 with R-divider and corrected I
            Args:
                Vmeter : device used for meas V across jj
                Rsh : shunt resistor across the source
                Rb : biasing resistor in series with jj
            """

            super().__init__(name, address, **kw)
            
            
            self.Vmeter = Vmeter
            self.Rsh = Rsh
            self.Rb = Rb 
            


    
            self.add_parameter('I',
                   label='Current',
                   unit = 'A',
                   get_cmd = 'SOUR:CURR?',
                   set_cmd = 'SOUR:CURR:AMPL '+'{}',
                   vals=vals.Numbers(-10e-6, 10e-6),
                   set_parser = self.set_I,
                   get_parser = self.get_I)
            
            self.add_parameter('Irange',
                   label='Current',
                   unit = 'A',
                   get_cmd = 'SOUR:CURR:RANG ?',
                   set_cmd = 'SOUR:CURR:RANG '+'{}',
                   vals=vals.Numbers(1e-9, 10e-6),
                   set_parser=float,
                   get_parser=float)

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
        print('set R Attn is not implemented')
        pass




    def set_I(self, I):
        
        I = float(I)
        
        r = self.Rsh
        R = self.Rb
       
        return I*(R+r)/r
    # Ideally R should be replaced with R+R_DUT
    # For example, if R_DUT = R = 100Mohm and r = 1Mohm, 
    # for 25pA flowing through DUT, we asked for (from set_I) 
    # I = 25pA*101 = 2.525nA
            
    def get_I(self, I):
        
        ib = float(I)
        
        Voff = self.Vmeter.Voff
        v = self.Vmeter.V.get() - Voff
        

        r = self.Rsh
        R = self.Rb
        
        
        return (ib*r - v)/(R+r)
    # if Ib = 2.525nA, get_I received 
    # (2.525nA*1Mohm - v)/101Mohm


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