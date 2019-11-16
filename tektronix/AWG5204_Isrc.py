# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 15:27:03 2019

@author: measPC
"""

from qcodes.instrument_drivers.tektronix.AWG5204 import AWG5204
from qcodes import VisaInstrument, validators as vals

class AWG5204_Isrc(AWG5204):
    """
    The QCoDeS driver for Tektronix AWG5204
    """

    def __init__(self, name: str, address: str, ch:int, R_bias, Attn,
                 timeout: float=10, **kwargs) -> None:
        """
        Args:
            name: The name used internally by QCoDeS in the DataSet
            address: The VISA resource name of the instrument
            timeout: The VISA timeout time (in seconds).
        """
#num_channels=4
        super().__init__(name, address,
                         timeout=timeout, **kwargs)
        self._Attn = Attn
        self._R_bias = R_bias
        self.I_to_V = lambda i: i*self._R_bias*self._Attn/2
        
        self.add_parameter('I',
               label='Current',
               unit = 'A',
               get_cmd = None,
#               set_cmd= self.ch1.fgen_dclevel.set,
               set_cmd = getattr(self, f'ch{ch}').fgen_dclevel.set,
#               set_cmd= 'self.ch{}.fgen_dclevel.set'.format(ch),
               vals=vals.Numbers(-4/self._R_bias/self._Attn, 4/self._R_bias/self._Attn),
               set_parser= self.I_to_V)

    def set_R_Attn(self, R_bias, Attn):  
        self._Attn = Attn
        self._R_bias = R_bias
        self.I_to_V = lambda i: i*self._R_bias*self._Attn
        self.I.vals = vals.Numbers(-4/self._R_bias/self._Attn, 4/self._R_bias/self._Attn)
        
        
    