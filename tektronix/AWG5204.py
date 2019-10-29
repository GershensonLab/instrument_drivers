# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 15:27:03 2019

@author: measPC
"""

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
