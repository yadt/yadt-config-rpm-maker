#   yadt-config-rpm-maker
#   Copyright (C) 2011-2013 Immobilien Scout GmbH
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from logging import DEBUG, Formatter, StreamHandler, getLogger
from logging.handlers import SysLogHandler
from os import getpid

from config_rpm_maker.configuration.properties import get_log_format, is_verbose_enabled
from config_rpm_maker.configuration import get_properties, get_file_path_of_loaded_configuration


LOGGER = getLogger(__name__)

SYS_LOG_ADDRESS = "/dev/log"
SYS_LOG_FACILITY = SysLogHandler.LOG_USER
SYS_LOG_LEVEL = DEBUG

# When initializing the syslog handler {0} will be replaced with the revision.
SYS_LOG_FORMAT = "config_rpm_maker[{0}]: [%(levelname)5s] %(message)s"


class MutedLogger(object):

    def info(self, *args):
        pass

    def warn(self, *args):
        pass

    def error(self, *args):
        pass

    def debug(self, *args):
        pass


_muted_logger = MutedLogger()


def verbose(logger):
    """ returns the given logger if verbose is configured or it will return _muted_logger """

    if is_verbose_enabled():
        return logger

    return _muted_logger


def create_console_handler(log_level):
    """ returns a root_logger which logs to the console using the given log_level. """

    formatter = Formatter(get_log_format.default)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    return console_handler


def create_sys_log_handler(revision):
    """ creates a logger handler which logs to syslog and uses the given revision within the log format """

    syslog_format = SYS_LOG_FORMAT.format(revision)
    formatter = Formatter(syslog_format)

    sys_log_handler = SysLogHandler(address=SYS_LOG_ADDRESS, facility=SYS_LOG_FACILITY)
    sys_log_handler.setFormatter(formatter)
    sys_log_handler.setLevel(SYS_LOG_LEVEL)

    return sys_log_handler


def log_configuration(logging_function, configuration, path):
    """ Logs the path to configuration file and the properties including their value and value type """

    logging_function('Loaded configuration file "%s"', path)

    properties = sorted(configuration.keys())
    if len(properties) == 0:
        logging_function('Configuration file was empty!')
        return

    max_length = len(max(properties, key=lambda property: len(property.key)).key) + 2  # two is for quotes on left and right side

    for property in properties:
        indented_key = ('"%s"' % property.key).ljust(max_length)
        value = configuration[property]
        logging_function('Configuration property %s = "%s" (%s)', indented_key, value, type(value).__name__)


def log_elements_of_list(logging_function, summary_message, unsorted_list):
    """ Uses the given logging function to log all elements of a unsorted list in
        a sorted way. Each element to one line. """

    sorted_list = sorted(unsorted_list)

    count_of_elements = len(sorted_list)
    if count_of_elements == 0:
        logging_function(summary_message, 0)
        return

    logging_function(summary_message + ' Listing in sorted order:', count_of_elements)
    for i in range(count_of_elements):
        logging_function('    #%s: %s', i, sorted_list[i])


def log_process_id(logging_function):
    """ Calls the given logging function to log the current process id """

    process_id = getpid()
    logging_function("Process ID is %s", process_id)


def append_console_logger(logger, console_log_level):
    """ Creates and appends a console log handler with the given log level """

    console_handler = create_console_handler(console_log_level)
    logger.addHandler(console_handler)

    if console_log_level == DEBUG:
        logger.debug("DEBUG logging is enabled")


def log_additional_information():
    """ Logs additional information as the process id and the configuration. """

    log_process_id(LOGGER.info)
    log_configuration(LOGGER.debug, get_properties(), get_file_path_of_loaded_configuration())


def log_exception_message(message):
    """ Logs the given multi line message line by line. """

    for line in str(message).split("\n"):
        LOGGER.error(line)
