from qcodes import VisaInstrument, validators as vals
import numpy as np
from qcodes.utils.validators import Numbers



class K213(VisaInstrument):
    """
    This is the code for Keithley 213 Quad Voltage Source
    """

    def __init__(self, name, address, reset=False,  **kwargs):
        super().__init__(name, address,  terminator='\n', **kwargs)
# general commands
#        self.add_parameter(name='voltAutoRange',
#                           label='Voltage Auto Range setting',
#                           unit='V',
#                           get_cmd='P2 A? X',
#                           set_cmd='P2 A1 X',
#                           get_parser=float,
#                           vals=Numbers(min_value=0,
#                                        max_value=1))
#        self.add_parameter('rf_switch',
#                   label='Rf_switch',
#                           unit='ns',
#                   set_cmd='{}',
#                           get_cmd=!'PULM:INT:PWID?',
#                   val_mapping ={ 'ON' : 'RF1', 'OFF' :'RF0'})  # ON/OFF RF signal
        self.add_parameter(name='voltage',
                           label='Vgate',
                           unit='V',
                           get_cmd='P2 V? X',
                           set_cmd='P2 V{} X',
                           get_parser = lambda s: float(s[1:]),
#                           set_parser= lambda x: x/1e9,
#                           get_parser= lambda x: float(x)*1e6 ,                           
                           vals=Numbers(min_value=-10,
                                        max_value=10))

# reset values after each reconnect
#        self.power(0)
#        self.power_offset(0)
#        self.connect_message()
#        self.add_function('reset', call_cmd='*RST')

 
if __name__ == "__main__":
 
    try:
#            ats_inst.close()
#            acquisition_controller.close()
            Instrument.close_all()
    except KeyError:
        pass    
    except NameError:
        pass    
    
    Vgate =  K213(name = 'Vgate', address = "GPIB::3::INSTR")
    Vgate.voltage.set(0.04 + 1*0.62)
    print ("voltage =", Vgate.voltage.get(), "V")
#    Instrument.close_all()