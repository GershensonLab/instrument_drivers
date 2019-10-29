from .ATS import AlazarTech_ATS, Buffer
from .utils import TraceParameter
from qcodes.utils import validators
import  time

import matplotlib.pyplot as plt
import numpy as np

from ctypes import *
from contextlib import contextmanager

import ctypes 

class AlazarTech_ATS9870(AlazarTech_ATS):
    """
    This class is the driver for the ATS9870 board
    it inherits from the ATS base class

    It creates all necessary parameters for the Alazar card
    """
    def __init__(self, name, TD_dll_path = None, AVG_dll_path = None, **kwargs):
        dll_path = 'C:\\WINDOWS\\System32\\ATSApi.dll'
#        dll_path = 'C:\\WINDOWS\\system32\\ATS_Average_DLL.dll'  #additional dll for specific needs (ie GetAverregedBuffer)
        
        
#        if alt_dll_path == None: # check if alt_dll has been chosen
#            alt_dll_path = dll_path   
#
        super().__init__(name, dll_path=dll_path, TD_dll_path = TD_dll_path, AVG_dll_path =  AVG_dll_path, **kwargs)
        # add parameters
        
        self.delta_frequency = 3.030303e7 

        # ----- Parameters for the configuration of the board -----
        self.add_parameter(name='clock_source',
                           parameter_class=TraceParameter,
                           label='Clock Source',
                           unit=None,
                           initial_value='INTERNAL_CLOCK',
                           val_mapping={'INTERNAL_CLOCK': 1,
                                        'SLOW_EXTERNAL_CLOCK': 4,
                                        'EXTERNAL_CLOCK_AC': 5,
                                        'EXTERNAL_CLOCK_10_MHz_REF': 7})
        
        self.add_parameter(name='external_sample_rate',
                           get_cmd=None,
                           parameter_class=TraceParameter,
                           label='External Sample Rate',
                           unit='S/s',
                           vals=validators.Enum(1000_000_000),
                           initial_value=None)
        
        self.add_parameter(name='sample_rate',
                           parameter_class=TraceParameter,
                           label='Sample Rate',
                           unit='S/s',
                           initial_value=1000000000,
                           val_mapping={
                               1000: 0x1,
                               2000: 0x2,
                               5000: 0x4,
                               10000: 0x8,
                               20000: 0xA,
                               50000: 0xC,
                               100000: 0xE,
                               200000: 0x10,
                               500000: 0x12,
                               1000000: 0x14,
                               2000000: 0x18,
                               5000000: 0x1A,
                               10000000: 0x1C,
                               20000000: 0x1E,
                               50000000: 0x22,
                               100000000: 0x24,
                               250000000: 0x2B,
                               500000000: 0x30,
                               1000000000: 0x35,
                               'EXTERNAL_CLOCK': 0x40,
                               '1GHz_REFERENCE_CLOCK': 1000000000})

        self.add_parameter(name='clock_edge',
                           parameter_class=TraceParameter,
                           label='Clock Edge',
                           unit=None,
                           initial_value='CLOCK_EDGE_RISING',
                           val_mapping={'CLOCK_EDGE_RISING': 0,
                                        'CLOCK_EDGE_FALLING': 1})

        self.add_parameter(name='decimation',
                           parameter_class=TraceParameter,
                           label='Decimation',
                           unit=None,
                           initial_value=0,
                           vals=validators.Ints(0, 100000))

        for i in ['1', '2']:
            self.add_parameter(name='coupling' + i,
                               parameter_class=TraceParameter,
                               label='Coupling channel ' + i,
                               unit=None,
                               initial_value='AC',
                               val_mapping={'AC': 1, 'DC': 2})
            self.add_parameter(name='channel_range' + i,
                               parameter_class=TraceParameter,
                               label='Range channel ' + i,
                               unit='V',
                               initial_value=4,
                               val_mapping={0.04: 2,
                                            0.1: 5,
                                            0.2: 6,
                                            0.4: 7,
                                            1.0: 10,
                                            2.0: 11,
                                            4.0: 12})
            self.add_parameter(name='impedance' + i,
                               parameter_class=TraceParameter,
                               label='Impedance channel ' + i,
                               unit='Ohm',
                               initial_value=50,
                               val_mapping={1000000: 1,
                                            50: 2})
            self.add_parameter(name='bwlimit' + i,
                               parameter_class=TraceParameter,
                               label='Bandwidth limit channel ' + i,
                               unit=None,
                               initial_value='DISABLED',
                               val_mapping={'DISABLED': 0,
                                            'ENABLED': 1})

        self.add_parameter(name='trigger_operation',
                           parameter_class=TraceParameter,
                           label='Trigger Operation',
                           unit=None,
                           initial_value='TRIG_ENGINE_OP_J',
                           val_mapping={'TRIG_ENGINE_OP_J': 0,
                                        'TRIG_ENGINE_OP_K': 1,
                                        'TRIG_ENGINE_OP_J_OR_K': 2,
                                        'TRIG_ENGINE_OP_J_AND_K': 3,
                                        'TRIG_ENGINE_OP_J_XOR_K': 4,
                                        'TRIG_ENGINE_OP_J_AND_NOT_K': 5,
                                        'TRIG_ENGINE_OP_NOT_J_AND_K': 6})
        for i in ['1', '2']:
            self.add_parameter(name='trigger_engine' + i,
                               parameter_class=TraceParameter,
                               label='Trigger Engine ' + i,
                               unit=None,
                               initial_value='TRIG_ENGINE_' + ('J' if i == 0 else 'K'),
                               val_mapping={'TRIG_ENGINE_J': 0,
                                            'TRIG_ENGINE_K': 1})
            self.add_parameter(name='trigger_source' + i,
                               parameter_class=TraceParameter,
                               label='Trigger Source ' + i,
                               unit=None,
                               initial_value='DISABLE',
                               val_mapping={'CHANNEL_A': 0,
                                            'CHANNEL_B': 1,
                                            'EXTERNAL': 2,
                                            'DISABLE': 3})
            self.add_parameter(name='trigger_slope' + i,
                               parameter_class=TraceParameter,
                               label='Trigger Slope ' + i,
                               unit=None,
                               initial_value='TRIG_SLOPE_POSITIVE',
                               val_mapping={'TRIG_SLOPE_POSITIVE': 1,
                                            'TRIG_SLOPE_NEGATIVE': 2})
            self.add_parameter(name='trigger_level' + i,
                               parameter_class=TraceParameter,
                               label='Trigger Level ' + i,
                               unit=None,
                               initial_value=128,
                               vals=validators.Ints(0, 255))

        self.add_parameter(name='external_trigger_coupling',
                           parameter_class=TraceParameter,
                           label='External Trigger Coupling',
                           unit=None,
                           initial_value='AC',
                           val_mapping={'AC': 1,
                                        'DC': 2})
        self.add_parameter(name='external_trigger_range',
                           parameter_class=TraceParameter,
                           label='External Trigger Range',
                           unit=None,
                           initial_value='ETR_5V',
                           val_mapping={'ETR_5V': 0,
                                        'ETR_1V': 1})
        self.add_parameter(name='trigger_delay',
                           parameter_class=TraceParameter,
                           label='Trigger Delay',
                           unit='Sample clock cycles',
                           initial_value=0,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='timeout_ticks',
                           parameter_class=TraceParameter,
                           label='Timeout Ticks',
                           unit='10 us',
                           initial_value=0,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='aux_io_mode',
                           parameter_class=TraceParameter,
                           label='AUX I/O Mode',
                           unit=None,
                           initial_value='AUX_IN_AUXILIARY',
                           val_mapping={'AUX_OUT_TRIGGER': 0,
                                        'AUX_IN_TRIGGER_ENABLE': 1,
                                        'AUX_IN_AUXILIARY': 13})

        self.add_parameter(name='aux_io_param',
                           parameter_class=TraceParameter,
                           label='AUX I/O Param',
                           unit=None,
                           initial_value='NONE',
                           val_mapping={'NONE': 0,
                                        'TRIG_SLOPE_POSITIVE': 1,
                                        'TRIG_SLOPE_NEGATIVE': 2})


        # ----- Parameters for the acquire function -----
        self.add_parameter(name='mode',
                           label='Acquisition mode',
                           unit=None,
                           initial_value='NPT',
                           get_cmd=None,
                           set_cmd=None,
                           val_mapping={'NPT': 0x200, 'TS': 0x400, 'AVG':0x600})

        # samples_per_record must be a multiple of of some number (64 in the
        # case of ATS9870) and and has some minimum (256 in the case of ATS9870)
        # These values can be found in the ATS-SDK programmar's guide
        self.add_parameter(name='samples_per_record',
                           label='Samples per Record',
                           unit=None,
                           initial_value=96000,
                           get_cmd=None,
                           set_cmd=None,
                           vals=validators.Multiples(
                                divisor=64, min_value=256))

        self.add_parameter(name='records_per_buffer',
                           label='Records per Buffer',
                           unit=None,
                           initial_value=1,
                           get_cmd=None,
                           set_cmd=None,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='buffers_per_acquisition',
                           label='Buffers per Acquisition',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value=1,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='channel_selection',
                           label='Channel Selection',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='AB',
                           val_mapping={'A': 1, 'B': 2, 'AB': 3})
        self.add_parameter(name='transfer_offset',
                           label='Transfer Offset',
                           unit='Samples',
                           get_cmd=None,
                           set_cmd=None,
                           initial_value=0,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='external_startcapture',
                           label='External Startcapture',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='ENABLED',
                           val_mapping={'DISABLED': 0X0,
                                        'ENABLED': 0x1})
        self.add_parameter(name='enable_record_headers',
                           label='Enable Record Headers',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='DISABLED',
                           val_mapping={'DISABLED': 0x0,
                                        'ENABLED': 0x8})
        self.add_parameter(name='alloc_buffers',
                           label='Alloc Buffers',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='DISABLED',
                           val_mapping={'DISABLED': 0x0,
                                        'ENABLED': 0x20})
        self.add_parameter(name='fifo_only_streaming',
                           label='Fifo Only Streaming',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='DISABLED',
                           val_mapping={'DISABLED': 0x0,
                                        'ENABLED': 0x800})
        self.add_parameter(name='interleave_samples',
                           label='Interleave Samples',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='DISABLED',
                           val_mapping={'DISABLED': 0x0,
                                        'ENABLED': 0x1000})
        self.add_parameter(name='get_processed_data',
                           label='Get Processed Data',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value='DISABLED',
                           val_mapping={'DISABLED': 0x0,
                                        'ENABLED': 0x2000})
        self.add_parameter(name='allocated_buffers',
                           label='Allocated Buffers',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value=1,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='buffer_timeout',
                           label='Buffer Timeout',
                           unit='ms',
                           get_cmd=None,
                           set_cmd=None,
                           initial_value=1000,
                           vals=validators.Ints(min_value=0))
        self.add_parameter(name='dmaBufferCount',
                           label='dma Buffer Count',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value=8,
                           vals=validators.Ints(min_value=2))
        self.add_parameter(name='number_of_averaging',
                           label='number of averaging',
                           unit=None,
                           get_cmd=None,
                           set_cmd=None,
                           initial_value=1,
                           vals=validators.Ints(min_value=1))        


        model = self.get_idn()['model']
        if model != 'ATS9870':
            raise Exception("The Alazar board kind is not 'ATS9870',"
                            " found '" + str(model) + "' instead.")
            
            
    def get_averaged_old(self, N_pts, N_avg):
        
        """
        function is obsolate, use get_prepared - start_capture - get_averaged
        """
        output = int()    
        
#        getavg_start = time.time()
        
        
#        channelMask = self.channel_selection.raw_value #A - 1, B - 2, AB -3 
#        samples_per_record = self.samples_per_record.raw_value
#        recordsPerBuffer = self.records_per_buffer.raw_value
#        numberofBuffers = self.buffers_per_acquisition.raw_value
#        dmaBufferCount = self.dmaBufferCount.raw_value
#        timeout_ms = self.buffer_timeout.raw_value
        
        
        channelMask = 3 
#        channel_selection = 3
        
        
        samples_per_record = N_pts
        number_of_averaging =  N_avg
 
#        samples_per_record = 512
#        number_of_averaging =   1        


        number_of_buffers = 1


        dmaBufferCount = 1
        timeout_ms = 100
        
        number_of_channels = 2        
        
        # bytes per sample
        max_s, bps = self._get_channel_info(self._handle)
        # TODO(JHN) Why +7 I guess its to do ceil division?
        bytes_per_sample = (bps + 7) // 8
        # bytes per record
        bytes_per_record = bytes_per_sample * samples_per_record

        # channels
#        channels_binrep = self.channel_selection.raw_value
#        number_of_channels = self.get_num_channels(channels_binrep)




        # bytes per buffer
        bytes_per_buffer =  (bytes_per_record *   number_of_channels)
        
       
        


        sample_type = c_uint8
        if bytes_per_sample > 1:
            sample_type = c_uint16

        self.clear_buffers()

#        # make sure that allocated_buffers <= buffers_per_acquisition
#        allocated_buffers = self.allocated_buffers.raw_value
#        buffers_per_acquisition = self.buffers_per_acquisition.raw_value
#
#        if allocated_buffers > buffers_per_acquisition:
##            logger.warning("'allocated_buffers' should be <= "
##                            "'buffers_per_acquisition'. Defaulting 'allocated_buffers'"
##                            f" to {buffers_per_acquisition}")
#            self.allocated_buffers.set(buffers_per_acquisition)
#
#        allocated_buffers = self.allocated_buffers.raw_value
##        buffer_recycling = buffers_per_acquisition > allocated_buffers
        
        self.clear_buffers()
        for k in range(number_of_buffers):
            try:
                self.buffer_list.append(Buffer(sample_type, bytes_per_buffer))
            except:
                self.clear_buffers()
                raise
        

        buffers_completed = 0
        bytes_transferred = 0


#        print('\nGetAVG buffer prep time \t', time.time() - getavg_start) 
        
        
        try:
            while (buffers_completed < number_of_buffers):
    
               
                buf = self.buffer_list[buffers_completed % number_of_buffers]
                bufferSize_samples = buf.size_bytes
    

 
                try:
                    self._call_dll('ATS_StopCapture',  #in manual
                                  self._handle)
#                                  ,
#                                  channelMask, 
#                                  samples_per_record, 
#                                  number_of_averaging, 
##                                  numberofBuffers, 
#                                  dmaBufferCount)
                    print('void')
                    
                except RuntimeError:
                   pass
                finally: 
                    
  
#                    start = time.time()
                    

#                    self._call_dll('ATS_ConfigCapture',  #in manual
                    self._call_dll('ATS_StartCapture',  #in manual
                                      self._handle,
                                      channelMask,
                                      samples_per_record, 
                                      number_of_averaging, 
#                                      number_of_buffers, 
                                      dmaBufferCount)

#                    self._call_dll('ATS_StartCapture',  #in manual
#                                      1652,
#                                      3,
#                                      8192, 
#                                      4000, 
#                                      8)
                  
 

                  
                   
#                    print('\nATS_StartCapture \t', time.clock() - start)                      
#                    start = time.time()
                    
                    try:
                        self._call_dll('ATS_GetAverageBuffer',     #in manual
                                      self._handle,
                                      cast(buf.addr, c_void_p),
                                      bufferSize_samples,
                                      timeout_ms)
                        
#                        print('ATS_GetAverageBuffer \t', time.clock() - start) 
#                        start = time.time()
                            
                    except:
                       print('\nATS_GEt_averged FAILED\n')
                    finally:
    
                        self._call_dll('ATS_StopCapture',  #in manual
                                      self._handle)
#                        ,
#                                      channelMask, 
#                                      samples_per_record, 
#                                      number_of_averaging, 
##                                      number_of_buffers, 
#                                      dmaBufferCount)
#            
    
#                        print('ATS_StopCapture \t', time.clock() - start) 
#                        start = time.time()    
    
                output += buf.buffer
    
                buffers_completed += 1
                bytes_transferred += buf.size_bytes


                
        
        finally:
            self.clear_buffers()
           
        


             
        return output / number_of_buffers
      
 
    """
    context manager for allocation/releasing memory
    ConfigCapture prepeares card, but doesnt start capturing
    """
       
    @contextmanager    
    def get_prepared(self, N_pts, N_avg, N_buf = 1):

#        print('hello world world')
        
        channelMask = 3 
        
        self.samples_per_record = N_pts
        self.number_of_averaging =  N_avg
        self.number_of_buffers =  N_buf
 
        dmaBufferCount = 8
        
        
#        self.ref_sc = 
        
        
        
        
        
        t = np.arange( N_pts )
        s = self.sample_rate.get()

#        s = 1e9
        
#        df = 3.030303e7 
        
        ref_sin = np.int8(  127 * np.sin( 2*np.pi*self.delta_frequency*t/s ) ) #np.cos(2*np.pi*self.delta_frequency*t/s)
        ref_cos = np.int8(  127 * np.cos( 2*np.pi*self.delta_frequency*t/s ) ) #np.sin(2*np.pi*self.delta_frequency*t/s) 

#        ref_sin = np.int8(  127 * np.sin( 2*np.pi*df*t/s ) ) #np.cos(2*np.pi*self.delta_frequency*t/s)
#        ref_cos = np.int8(  127 * np.cos( 2*np.pi*df*t/s ) ) #np.sin(2*np.pi*self.delta_frequency*t/s) 

        
        self.ref_IQ = np.array ([ref_sin, ref_cos, ref_cos, ref_sin])




        number_of_channels = 2  
        
        samples_per_record = self.samples_per_record
        number_of_buffers = self.number_of_buffers  
        
        max_s, bps = self._get_channel_info(self._handle)
        bytes_per_sample = (bps + 7) // 8
        bytes_per_record = bytes_per_sample * samples_per_record
        bytes_per_buffer =  (bytes_per_record *   number_of_channels)
        
        sample_type = c_uint8
        if bytes_per_sample > 1:
            sample_type = c_uint16
 
        self.clear_buffers()


#        print('N buff', number_of_buffers)
        for k in range(number_of_buffers):
            try:
                self.buffer_list.append( Buffer( sample_type, bytes_per_buffer ))
#                print('Buffer appended')
            except:
                self.clear_buffers()
                raise        




        self._call_dll('AVG_ATS_ConfigCapture',  #from ATS_Average_NPT_custom_DLL
                          self._handle,
                          channelMask,
                          self.samples_per_record, 
                          self.number_of_averaging,
                          self.number_of_buffers,
                          dmaBufferCount)
        
        self.Prepared = True


        try:
            yield 
        finally:
            self.clear_buffers()
            
            self._call_dll('AVG_ATS_StopCapture',  #from ATS_Average_NPT_custom_DLL
                                  self._handle)
            self.Prepared = False
#            print('\n Card resources were released\n')
        


    """
    actual start of capturing, trigger event might do the same job in ext_trigg mode
    """
    def start_capturing(self):

        self._call_dll('AlazarStartCapture',  #from ATSApi
                       self._handle)  
        




    """
    read captured and averaged value from ats
    """
    def get_averaged(self):   

#        start = time.clock()
        
        output = int()    
        

        timeout_ms = 5000
#        number_of_channels = 2  
        
#        samples_per_record = self.samples_per_record
        number_of_buffers = self.number_of_buffers  
        
        
#        print ('ini', 1e6*(time.clock() - start) )
#        start = time.time()
        
        if self.Prepared:
        
           
            
            # bytes per sample
#            max_s, bps = self._get_channel_info(self._handle)
#            bytes_per_sample = (bps + 7) // 8
#            bytes_per_record = bytes_per_sample * samples_per_record
#            bytes_per_buffer =  (bytes_per_record *   number_of_channels)
#            
#            sample_type = c_uint8
#            if bytes_per_sample > 1:
#                sample_type = c_uint16
# 
#            self.clear_buffers()
#
#            for k in range(number_of_buffers):
#                try:
#                    self.buffer_list.append( Buffer( sample_type, bytes_per_buffer ))
#                except:
#                    self.clear_buffers()
#                    raise
            
    
            buffers_completed = 0
            bytes_transferred = 0        
            
            
            try:
                while (buffers_completed < number_of_buffers):
#                    print ('buffers prep0',1e6*(time.clock() - start) )        
#                    print(len(self.buffer_list))
                    buf = self.buffer_list[buffers_completed % number_of_buffers]
                    bufferSize_samples = buf.size_bytes
        
#                    print ('buffers prep',1e6*(time.clock() - start) )
#                    start = time.time()
                    
                    self._call_dll('AVG_ATS_GetAverageBuffer',     #from ATS_Average_NPT_custom_DLL
                                  self._handle,
                                  cast(buf.addr, c_void_p),
                                  bufferSize_samples,
                                  timeout_ms)
                    
#                    print ('get buff',1e6*(time.clock() - start))
#                    start = time.time()
                    
                    output += buf.buffer
        
                    buffers_completed += 1
                    bytes_transferred += buf.size_bytes
            
            finally:
#                self.clear_buffers()
                pass
           
        else:
            print('Board is not prepared for capturing')
#        print ('rest',1e6*(time.clock() - start))
#        return output / self.number_of_buffers -127#np.int8(output / self.number_of_buffers-127)
            
            
#        print('out type ', type(output[0]))
#        
#        print(output)
#        print (np.int16(output - 127.0))
            
        return np.int16(output - 127.0) # / self.number_of_buffers
#        return np.uint8(output ) # / self.number_of_buffers
      
        
        
        
    """
    read captured and averaged value from ats
    """
    def get_averaged_upd(self):   

        output = int()    
       

        
        
        
        
        timeout_ms = 0# 5000
        number_of_channels = 2  
        
        samples_per_record = self.samples_per_record
#        number_of_buffers = 1  
        
        if self.Prepared:
        
           
            
#            # bytes per sample
#            max_s, bps = self._get_channel_info(self._handle)
#            bytes_per_sample = (bps + 7) // 8
#            bytes_per_record = bytes_per_sample * samples_per_record
#            bytes_per_buffer =  (bytes_per_record *   number_of_channels)
#            
#            sample_type = c_uint8
#            if bytes_per_sample > 1:
#                sample_type = c_uint16
# 
#            self.clear_buffers()

            bufferSize_samples = 8 * 2*samples_per_record
            empty = [0 for i in range( 2*samples_per_record)]
            output = (ctypes.c_float * int( 2*samples_per_record)) (*empty)
                    
            
            try:

        
#                   
#                    buf = Buffer( sample_type, bytes_per_buffer )
#                    bufferSize_samples = buf.size_bytes
        
    
     
                    self._call_dll('AVG_ATS_GetAverageBuffer',     #from ATS_Average_NPT_custom_DLL
                                  self._handle,
                                  ctypes.byref (output) ,
                                  bufferSize_samples,
                                  timeout_ms)
                    
                    
#                    output += buf.buffer
        

            finally:
                self.clear_buffers()
           
        else:
            print('Board is not prepared for capturing')
             
#        return output / self.number_of_buffers -127#np.int8(output / self.number_of_buffers-127)
        return np.uint8(output)
      

        
        

#        

