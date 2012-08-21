import logging
import re
import os

class InvalidTokenDefinitionException (Exception):
    """
    Exception stating that the value of a given token 
    is invalid, i.e. contains token references
    """
    def __init__ (self, name, value):
        self.name = name
        self.value = value

    def __str__ (self):
        return "Token value for token '%s' is invalid: '%s'" % (self.name, self.value)

class MissingTokenException (Exception):
    """
    Exception stating that a value for a given token 
    has not been found in the token definition. 
    """
    
    def __init__ (self, token, file=None):
        self.token = token
        self.file = file

    def __str__ (self):
        msg = "Missing token '%s'" % self.token
        if self.file:
            msg += " in file '%s'" % self.file
        return msg

class TokenReplacer (object):
    """
    Class that replaces tokens in strings. 
    
    The general syntax is
        @@@TOKEN@@@
    """

    TOKEN_PATTERN = re.compile(r"@@@([A-Za-z0-9_-]*)@@@")

    @classmethod
    def filter_directory (cls, 
                          directory, 
                          variables_definition_directory, 
                          replacer_function=None):
        logging.info("Filtering files in %s", directory)
        
        token_replacer = cls.from_directory(os.path.abspath(variables_definition_directory), 
                                            replacer_function=replacer_function)
        
        for root, _, filenames in os.walk(directory):
            if variables_definition_directory in root:
                continue
            for filename in filenames:
                absolute_filename = os.path.join(root, filename)
                logging.debug("Filtering file %s", absolute_filename)
                token_replacer.filter_file(absolute_filename)

    @classmethod
    def from_directory (cls, directory, replacer_function=None):
        logging.debug("Initializing token replacer of class %s from directory %s",
                      cls.__name__, directory)
        
        result = cls(replacer_function=replacer_function)
        
        absolute_path = os.path.abspath(directory)
        
        for name in os.listdir(absolute_path):
            candidate = os.path.join(absolute_path, name)
            if os.path.isfile(candidate):
                with open(candidate) as property_file:
                    result[name] = property_file.read().strip()
        
        return result

    def __init__ (self, token_values={}, replacer_function=None):
        self.token_values = {}
        
        for token in token_values:
            if TokenReplacer.TOKEN_PATTERN.search(token_values[token]):
                raise InvalidTokenDefinitionException(token, token_values[token])
            self.token_values[token] = token_values[token].strip()
        
        if not replacer_function:
            def replacer_function (token, replacement):
                __pychecker__ = 'unusednames=token'
                return replacement
        else:
            logging.debug("Using custom replacer_function %s", 
                          replacer_function.__name__)
        self.replacer_function = replacer_function
        

    def filter (self, content):
        while True:
            match = TokenReplacer.TOKEN_PATTERN.search(content)
            if not match:
                return content
            token_name = match.group(1)
            if not token_name in self.token_values:
                raise MissingTokenException(token_name)
            replacement = self.replacer_function(token_name, 
                                                 self.token_values[token_name])
            
            content = content.replace("@@@%s@@@" % token_name, replacement)

    def filter_file (self, filename):
        __pychecker__ = "missingattrs=token"
        try:
            with open(filename, "r") as input_file:
                file_content = input_file.read()
                
            file_content_filtered = self.filter(file_content)
            
            with open(filename, "w") as output_file:
                output_file.write(file_content_filtered)
        except MissingTokenException as exception:
            raise MissingTokenException(exception.token, filename)

    def __setitem__ (self, index, value):
        self.token_values[index] = value
