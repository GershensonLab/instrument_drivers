# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 17:56:44 2019

@author: KelvinOX25
"""

import time
import numpy as np
import matplotlib.pyplot as plt
from qcodes.instrument_drivers.tektronix.AWG3252_Isrc import AWG3252_Isrc
from qcodes.instrument_drivers.HP.HP34401 import HP34401

from qcodes.instrument.base import Instrument
try:
    Instrument.close_all()
except KeyError:
    pass    
except NameError:
    pass  

Isrc = AWG3252_Isrc('gen', 'TCPIP0::192.168.13.32::inst0::INSTR',  R_bias = 1e9)
Vmeter = HP34401('meter', 'GPIB0::8::INSTR')
Vmeter.init('fast 6')

I_setpt = np.linspace(0, 4E-10,101)
V_rdg = []

for i in I_setpt:
    Isrc.I.set(i)
    time.sleep(0.050)
    V_rdg.append(Vmeter.v.get())
    
    
fig, ax = plt.subplots()
ax.plot(I_setpt, V_rdg, '.')    

#slopeN, interceptN, r_valueN, p_valueN, std_errN = stats.linregress()