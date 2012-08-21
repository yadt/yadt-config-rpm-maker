import logging
import sys

from tokenreplacer import TokenReplacer, MissingTokenException

def init_logging ():
    logging.basicConfig(format="%(asctime)s %(levelname)5s [%(name)s] - %(message)s")
    logging.getLogger().setLevel(logging.DEBUG)

def error (message, exit_code=0):
    sys.stderr.write("ERROR %s: %s\n" % (sys.argv[0], message))
    sys.exit(exit_code)

def validate_command_line_arguments ():
    if len(sys.argv) < 2:
        error("Missing directory.", 1)

    if len(sys.argv) < 3:
        error("Missing VARIABLES directory.", 1)

    return (sys.argv[1], sys.argv[2])

def filter_tokens_in_rpm_sources ():
    try:
        directory, variables_directory = validate_command_line_arguments() 
        TokenReplacer.filter_directory(directory, variables_directory)
    except Exception as e:
        error(str(e),1)

def filter_tokens_in_configviewer_sources ():
    directory, variables_directory = validate_command_line_arguments()
    
    def configviewer_token_replacer (token, replacement):
        filtered_replacement = replacement.rstrip()
        return '-ltrepme-strong title="%s"-gtrepme-%s-ltrepme-/strong-gtrepme-' % (token, filtered_replacement)
        
    try:
        TokenReplacer.filter_directory(directory, variables_directory, 
                                       replacer_function=configviewer_token_replacer)
    except Exception as e:
        error(str(e),1)
