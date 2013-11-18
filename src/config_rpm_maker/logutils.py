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

from logging import Formatter, StreamHandler, getLogger
from logging.handlers import SysLogHandler
from os import getpid

from config_rpm_maker.config import (DEFAULT_LOG_FORMAT,
                                     DEFAULT_LOG_LEVEL,
                                     DEFAULT_SYS_LOG_ADDRESS,
                                     DEFAULT_SYS_LOG_FORMAT,
                                     DEFAULT_SYS_LOG_LEVEL)

LOGGER = getLogger(__name__)


def create_console_handler(log_level=DEFAULT_LOG_LEVEL):
    """ Returnes a root_logger which logs to the console using the given log_level. """
    formatter = Formatter(DEFAULT_LOG_FORMAT)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    return console_handler


def create_sys_log_handler(revision):
    """ Create a logger handler which logs to sys log and uses the given revision within the format """
    format = DEFAULT_SYS_LOG_FORMAT.format(revision)
    formatter = Formatter(format)

    sys_log_handler = SysLogHandler(address=DEFAULT_SYS_LOG_ADDRESS)
    sys_log_handler.setFormatter(formatter)
    sys_log_handler.setLevel(DEFAULT_SYS_LOG_LEVEL)

    return sys_log_handler


def log_configuration_to_logger(logger, configuration, path):
    """ Logs the path to configuration file and the properties """

    logger.debug('Loaded configuration file "%s"', path)

    keys = sorted(configuration.keys())
    max_length = len(max(keys, key=len)) + 2  # two is for quotes on left and right side

    for key in keys:
        indentet_key = ('"%s"' % key).ljust(max_length)
        value = configuration[key]
        logger.debug('Configuraton property %s = "%s" (%s)', indentet_key, value, type(value).__name__)


def log_elements_of_list(summary_message, unsorted_list):
    """ Logs all elements of a unsorted list in a sorted way. Each element to one line. """
    sorted_list = sorted(unsorted_list)
    count_of_elements = len(sorted_list)
    LOGGER.debug(summary_message + ' Listing in sorted order:', count_of_elements)
    for i in range(count_of_elements):
        LOGGER.debug('    #%s: %s', i, sorted_list[i])


def log_process_id(logging_function):
    """ Calls the given logging function to log the current process id """
    process_id = getpid()
    logging_function("Process ID is %s", process_id)
