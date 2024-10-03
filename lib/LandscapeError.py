class LandscapeERROR(Exception):
    """
    Landscape generic exception class
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
