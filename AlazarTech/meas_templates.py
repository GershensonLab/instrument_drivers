# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 16:56:45 2019

@author: measPC
"""

import numpy as np
import matplotlib.pyplot as plt
import time,  datetime, math
import ctypes, os, csv, sys

from scipy.signal import savgol_filter
from IPython.display import clear_output

from progressbar import *
from tqdm import tqdm, tqdm_notebook

import qcodes as qc
from qcodes import Station
from qcodes.instrument.base import Instrument
from qcodes.dataset.experiment_container import (Experiment,
                                                 load_last_experiment,
                                                 new_experiment)
from qcodes.dataset.database import initialise_database
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id, get_data_by_id
from qcodes.dataset.data_export import get_shaped_data_by_runid


    
    
    
    
def set_state ( **kwargs ):
    """
        Setting of certain values to the Instrument parameters
        args:
            **kwargs:   dict of InstNicknames and values to be set
           
    """
    for var, val in kwargs.items():
        eval(var).set(val)



def vset_state ( **kwargs):
    """
        Verbose setting of certain values to the Instrument parameters
        args:
            **kwargs:   dict of InstNicknames and values to be set
           
    """
    for var, val in kwargs.items():
        eval(var).set(val)
        tqdm.write('{} is set to {}{}'.format(var.label, eng( val ), device.unit) )
        
        
def set_meas(dep, fast_indep, slow_indep = None, setup = setup, cleanup = cleanup):
    """
       Regestration of the parameters and setting up before/after run procedure
        
       args:
            dep: InstParameter to be regestered as dependent var 
            fast_indep: InstParameter to be regestered as fast independent var 
            slow_indep: InstParameter to be regestered as second independent var (if any) 
            setup: Procedure to be done before run
            cleanup: Procedure to be done after run
            
        returns:
        meas: Measurement() object
           
    """    
                   
    meas = Measurement()
    meas.register_parameter( fast_indep )  # register the fast independent parameter

    
    if slow_indep is not None:
        meas.register_parameter( slow_indep )  # register the first independent parameter
        meas.register_parameter( dep , setpoints = ( slow_indep,  fast_indep ) ) 
    else:
        meas.register_parameter( dep, setpoints = ( fast_indep , ))
        
    meas.add_before_run(setup, args=())    
    meas.add_after_run(cleanup, args=())    
    meas.write_period = 2
    
    return meas



def probe_scan( datasaver, probe_list, **kwargs):
    """
        DEPRECATE, use more general version S21_scan
        Do scan through probe_list and save result to the datasaver
        
        args:
            datasaver: Datasaver to save results of the measurment
            probe_list: Frequency list to scan through 
            **kwargs: dict of the InstParameters and its values to add to atasaver (have to be defined in set_meas)
            
           
    """ 
    
    
    probe_min = np.min (probe_list)
    probe_max = np.max (probe_list)
    
    pbar = tqdm_notebook(probe_list, desc = '{} to {} GHz scan'.format( probe_min/1e9,probe_max/1e9 ),
                        leave = False)

    with iqmixer.ats.get_prepared(N_pts = 8192, N_avg = 4000):
        for  f in pbar:
            
            iqmixer.frequency.set( f )
            pbar.set_description('{:1.4f}GHz'.format(f/1e9))
            
            iqmixer.ats.start_capturing()                
            S21 =  iqmixer.S21.get()
            
            
            if not kwargs:
                datasaver.add_result(( iqmixer.frequency, f),
                                     ( iqmixer.S21_ampl, S21.ampl))
            else:
                for var, val in kwargs.items():
                    device = var_list[var]
                    datasaver.add_result(( device, val),
                                         ( iqmixer.frequency, f),
                                         ( iqmixer.S21_ampl, S21.ampl))
            
            
def S21_scan(datasaver, y_var, x_var, x_list, **kwargs):
    """
        Do scan through list of values(x_list) of any InstrParameter(x_var), meas any (y_var) adta and save to datasaver
        
        args:
            datasaver: Datasaver to save results of the measurment
            y_var: InstParameter to be measured (tested only on S21.ampl and S21/phase)
            x_var: InstParameter to be scan (indep var)
            x_list: list of values for be scan through
            **kwargs: dict of the InstParameters and its values to add to datasaver (have to be defined in set_meas)
    """     
    ydevice = y_var
    
    xdevice = x_var
    xunit = xdevice.unit
    xlabel = xdevice.label
    
    x_min = np.min (x_list)
    x_max = np.max (x_list)
    
    tx_list = tqdm_notebook(x_list, desc = '{} to {} {} scan'.format( eng(x_min), eng(x_max ), xunit),
                            leave = False)

    with ats.syncing():
        ats.external_trigger_range('ETR_1V')
        ats.aux_io_mode("AUX_IN_TRIGGER_ENABLE")
        ats.aux_io_mode("AUX_OUT_TRIGGER")
        #ats.aux_io_param("TRIG_SLOPE_NEGATIVE")

    
    with iqmixer.ats.get_prepared(N_pts = 8192, N_avg = 4000):
        for  x in tx_list:
            
            xdevice.set( x )
            tx_list.set_description('{} @ {}{}'.format( xlabel, eng(x), xunit ))
            
            iqmixer.ats.start_capturing()                
            S21 = ydevice.get()
            
            
            res = [ ( xdevice, x), ( ydevice, S21 ) ]             
            for var, val in kwargs.items():
                   res = [( eval(var), val)] + res
       
            datasaver.add_result(*res)  



def pump_sweep(y_var,fpump_list, Nsw):
    """
    Do pump sweep with averaging and random delay

    args:
        y_var: InstParameter to be measured (tested only on S21.ampl and S21.phase)
        fpump_list: list of pump freq values for be scan through
        Nsw: number of sweeps for avging

    result:
        list of avged values (standart deviation) of Y_var with the length of fpump_list
    """ 
    

    rnd = np.random.random
    buf = np.zeros(len(fpump_list))
    ydevice = y_var
    
    with iqmixer.ats.get_prepared(N_pts = 8192, N_avg = 400):
        tNsw = tqdm_notebook(range(Nsw), desc = 'pump scan',  leave = False)                
        tNsw.set_description('pump scan @ {}GHz'.format( eng(f_target) ))
        
        for j in tNsw:

            time.sleep(rnd()*0.5 + .100)
            
            for i,fpump in enumerate(fpump_list):
                pump.frequency.set( fpump )
                #pump.frequency.get()
                time.sleep(0.003)

                iqmixer.ats.start_capturing() 
                S21 = ydevice.get()
                
                buf[i] += S21
                

    result = buf / Nsw
    result = (result - np.mean(result))**2
    return result



def pump_autosweep(y_var,fpump_list, Nsw, dt ):
    """
    Do pump sweep with averaging and random delay

    args:
        y_var: InstParameter to be measured (tested only on S21.ampl and S21.phase)
        fpump_list: list of pump freq values for be scan through
        Nsw: number of sweeps for avging

    result:
        list of avged values (standart deviation) of Y_var with the length of fpump_list
    """ 
    

    rnd = np.random.random
    buf = np.zeros(len(fpump_list))
    ydevice = y_var
    
    pump_min = np.min(fpump_list)
    pump_max = np.max(fpump_list)
    Npump = len(fpump_list)
    
    command_list=[ "*RST\n",
                 "*CLS\n",
                 "FREQ:MODE LIST\n",
                 "LIST:TYPE STEP\n",
                 "FREQ:STAR {} GHz\n".format((pump_min)/1e9),
                 "FREQ:STOP {} GHz\n".format((pump_max)/1e9),
                 "SWE:POIN {}\n".format(Npump),
                 #"SWE:POIN 11\n",

                 "SWE:DWEL {} S\n".format(dt),
                 "POW:AMPL 5 dBm\n",
                 "OUTP:STAT ON\n"]#, #Turn source RF state on
 
    
    with ats.syncing():
        ats.external_trigger_range('ETR_1V')
        ats.aux_io_mode("AUX_IN_TRIGGER_ENABLE")
        #ats.aux_io_mode("AUX_OUT_TRIGGER")
        ats.aux_io_param("TRIG_SLOPE_POSITIVE")
    
    with iqmixer.ats.get_prepared(N_pts = 8192, N_avg = 400):
        tNsw = tqdm_notebook(range(Nsw), desc = 'pump scan',  leave = False)                
        tNsw.set_description('pump scan @ {}GHz'.format( eng(f_target) ))
        #iqmixer.ats.start_capturing() 
        for j in tNsw:

            time.sleep(rnd()*0.5 + .100)
            
            for command in command_list:
                    pump.write(command)  
            
            elapsed = np.zeros(Npump)
            for i,fpump in enumerate(fpump_list):
                #pump.frequency.set( fpump )
                #pump.frequency.get()
                #time.sleep(0.003)
                
                
                iqmixer.ats.start_capturing() 
                if i == 0:
                    pump.write("TRIG:SOUR IMM")
                    pump.write("INIT")
                    #pump.write("INIT:CONT ON\n")
                start = time.time()    
                S21 = ydevice.get()
                elapsed[i] = time.time() - start
                buf[i] += S21
            tqdm.write('{}- {}'.format(j, np.mean(elapsed[1:]) ) )   

    result = buf / Nsw
    result = (result - np.mean(result))**2
    return result            
 

def scan_find_steep(datasaver_probe, offset, probe_list,  **kwargs):
    """
        Do probe scan and find a point on the slope _offset_ away from the S21 minimum
        
        args:
            datasaver_probe: Datasaver to save probe scan
            offset: position of the point on the slope , 0 for minS21, 1 for max S21
            probe_list: list of probe freq for be scan through
            **kwargs: dict of the InstParameters and its values to add to datasaver_probe (have to be defined in set_meas)
    """
    
    
    Nprobe = len(probe_list)
    S21_scan(datasaver_probe, S21_ampl, fprobe, probe_list,  **kwargs)
    
    runid = datasaver_probe.run_id
    
    S21_full = get_data_by_id(runid)[0][1]['data']
    S21_raw =  S21_full[-Nprobe:]
    freq_raw = probe_list
    
    window = int( Nprobe/10 )
    try:
        S21_filered = savgol_filter(S21_raw, window, 2)
    except ValueError:
        S21_filered = savgol_filter(S21_raw, window+1, 2)
  
    ind_min, ind_max, f_min, f_max,  S21_min, S21_max = xy_maxmin(freq_raw, S21_filered) 
    
    S21_target = S21_min + (S21_max - S21_min)*offset

    if ind_min < ind_max:
        min_cut  = ind_min 
        max_cut  = ind_max

    else:
        min_cut  = ind_max 
        max_cut  = ind_min
   
    freq_cut = freq_raw[min_cut: max_cut]
    S21_cut = S21_filered[min_cut: max_cut]
    
    f_target = xy_maxmin(freq_cut, np.abs(S21_cut - S21_target) )[2]

    return f_target, S21_target
           