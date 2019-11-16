# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 15:27:03 2019

@author: measPC
"""

import pyvisa
import time
import logging
import numpy as np
import struct
from qcodes import VisaInstrument, validators as vals

from .AWG70000A import AWG70000A

class AWG5204(AWG70000A):
    """
    The QCoDeS driver for Tektronix AWG5204
    """

    def __init__(self, name: str, address: str,
                 timeout: float=10, **kwargs) -> None:
        """
        Args:
            name: The name used internally by QCoDeS in the DataSet
            address: The VISA resource name of the instrument
            timeout: The VISA timeout time (in seconds).
        """

        super().__init__(name, address, num_channels=4,
                         timeout=timeout, **kwargs)
    def init(self):
        lines = ['*RST;',
                 'INST:MODE FGEN;',
                 'FGEN:CHAN1:TYPE DC;',
                 'FGEN:CHAN1:PATH DCHV;',
                 'FGEN:CHAN1:DCL 0;',
                 'OUTP1:STAT ON;']

        for i,l in enumerate(lines):
            self.write_raw(l)
            if i <= 2:
                time.sleep(12)
            else:
                time.sleep(2)