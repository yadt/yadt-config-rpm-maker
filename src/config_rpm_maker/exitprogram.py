# coding=utf-8
#
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

from logging import getLogger
from math import ceil
from sys import exit
from time import time, strftime

from config_rpm_maker.config import DEFAULT_DATE_FORMAT
from config_rpm_maker.returncodes import RETURN_CODE_SUCCESS
from config_rpm_maker.profiler import log_execution_time_summaries

LOGGER = getLogger(__name__)

_timestamp_at_start = None


def start_measuring_time():
    """ Start measuring the time. This is required to calculate the elapsed time. """

    LOGGER.info("Starting to measure time at %s", strftime(DEFAULT_DATE_FORMAT))

    global _timestamp_at_start
    _timestamp_at_start = time()


def get_timestamp_from_start():
    """ Returns the timestamp which has been set by start_measuring_time. """
    return _timestamp_at_start


def exit_program(message, return_code):
    """ Logs the given message and exits with given return code. """

    timestamp_from_start = get_timestamp_from_start()
    if timestamp_from_start is not None:
        log_execution_time_summaries(LOGGER.debug)

        elapsed_time_in_seconds = time() - timestamp_from_start
        elapsed_time_in_seconds = ceil(elapsed_time_in_seconds * 100) / 100

        LOGGER.info('Elapsed time: {0}s'.format(elapsed_time_in_seconds))

    if return_code == RETURN_CODE_SUCCESS:
        LOGGER.info(message)
    else:
        LOGGER.error(message)

    exit(return_code)
