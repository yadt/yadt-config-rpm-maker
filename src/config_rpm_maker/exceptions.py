class BaseConfigRpmMakerException(Exception):
    error_info = "Generic Error:\n"
    
    def __str__(self):
        return self.error_info + self.message 