from qcodes.instrument.visa import VisaInstrument
from qcodes.utils import validators as vals
import numpy as np


class Weinschel_8320(VisaInstrument):
    '''
    QCodes driver for the stepped attenuator
    Weinschel is formerly known as Aeroflex/Weinschel
    '''

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r', **kwargs)

        self.add_parameter('attenuation', unit='dB',
                           set_cmd='CHAN1;ATTN {};',
                           get_cmd='CHAN1;ATTN?',
                           vals=vals.Enum(*np.arange(0, 60.1, 2).tolist()),
                           get_parser=float)

        self.connect_message()



if __name__ == "__main__":


      try:
            Instrument.close_all()
      except KeyError:
            pass    
    
      Aeroflex = Weinschel_8320(name = "Aeroflex", address = "GPIB::10::INSTR") 
      
      
      Aeroflex.attenuation.set(20)
      
      print( Aeroflex.attenuation.get() )