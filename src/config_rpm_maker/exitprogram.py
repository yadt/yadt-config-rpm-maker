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

LOGGER = getLogger(__name__)

timestamp_at_start = 0


def start_measuring_time():
    """ Start measuring the time. This is required to calculate the elapsed time. """

    LOGGER.info("Starting to measure time at %s", strftime(DEFAULT_DATE_FORMAT))

    global timestamp_at_start
    timestamp_at_start = time()


def exit_program(message, return_code):
    """ Logs the given message and exits with given return code. """

    elapsed_time_in_seconds = time() - timestamp_at_start
    elapsed_time_in_seconds = ceil(elapsed_time_in_seconds * 100) / 100
    LOGGER.info('Elapsed time: {0}s'.format(elapsed_time_in_seconds))

    if return_code == RETURN_CODE_SUCCESS:
        LOGGER.info(message)
    else:
        LOGGER.error(message)

    exit(return_code)
