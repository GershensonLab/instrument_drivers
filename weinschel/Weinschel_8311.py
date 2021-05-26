from qcodes.instrument.visa import VisaInstrument
from qcodes.utils import validators as vals
import numpy as np


class Weinschel_8311(VisaInstrument):
    '''
    QCodes driver for the stepped attenuator
    Weinschel is formerly known as Aeroflex/Weinschel
    '''

    def __init__(self, name, address, **kwargs):
        super().__init__(name, address, terminator='\r', **kwargs)

        self.add_parameter('attenuationCH1', unit='dB',
                           set_cmd='CHAN 1;ATTN {};',
                           get_cmd='CHAN 1;ATTN?',
                           vals=vals.Enum(*np.arange(0, 100.1, 2).tolist()),
                           get_parser=float)

        self.add_parameter('attenuationCH2', unit='dB',
                           set_cmd='CHAN 2;ATTN {};',
                           get_cmd='CHAN 2;ATTN?',
                           vals=vals.Enum(*np.arange(0, 100.1, 2).tolist()),
                           get_parser=float)

        self.add_parameter('attenuationCH3', unit='dB',
                           set_cmd='CHAN 3;ATTN {};',
                           get_cmd='CHAN 3;ATTN?',
                           vals=vals.Enum(*np.arange(0, 100.1, 2).tolist()),
                           get_parser=float)
        
        
        self.connect_message()



if __name__ == "__main__":


      try:
            Instrument.close_all()
      except KeyError:
            pass    
    
      Aeroflex = Weinschel_8311(name = "Aeroflex", address = "GPIB::10::INSTR") 
      
      
      Aeroflex.attenuationCH2.set(0)
      Aeroflex.attenuationCH1.set(20)
      
      print( Aeroflex.attenuationCH1.get() )
      print( Aeroflex.attenuationCH2.get() )
      
      Aeroflex.close()