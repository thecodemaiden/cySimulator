class Radio(object):
    """A very simple radio implementation"""
    def __init__(self, rx_sens=1e-10, tx_pow=0.1):
        self.rx_sensitivity = rx_sens # in W
        self.tx_power = tx_pow


