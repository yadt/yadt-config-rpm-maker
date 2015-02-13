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

"""
    This module contains functions which were created for performance
    tweaking. The test coverage of this module is low since it's main
    purpose is to add logging information.
"""

from functools import wraps
from logging import getLogger
from time import time
from os import walk
from os.path import join, getsize

from config_rpm_maker.configuration import get_thread_count

LOGGER = getLogger(__name__)

LOG_EACH_MEASUREMENT = False

_execution_time_summary = {}


def measure_execution_time(original_function):

    def process_measurement(elapsed_time_in_seconds, args, kwargs):
        arguments = ', '.join([str(arg) for arg in args[1:]])

        key_word_arguments = ""
        if kwargs:
            key_word_arguments = ", " + str(kwargs)

        if len(args) > 0:
            function_name = "%s.%s" % (args[0].__class__.__name__, original_function.__name__)
        else:
            function_name = original_function.__name__

        if function_name not in _execution_time_summary.keys():
            _execution_time_summary[function_name] = [elapsed_time_in_seconds, 1]
        else:
            _execution_time_summary[function_name][0] += elapsed_time_in_seconds
            _execution_time_summary[function_name][1] += 1

        if LOG_EACH_MEASUREMENT:
            function_call = '%s(%s%s)' % (function_name, arguments, key_word_arguments)
            LOGGER.debug('Took %.2fs to perform %s', elapsed_time_in_seconds, function_call)

    @wraps(original_function)
    def wrapped_function(*args, **kwargs):
        start_time = time()

        return_value_from_function = original_function(*args, **kwargs)

        end_time = time()

        elapsed_time_in_seconds = end_time - start_time

        process_measurement(elapsed_time_in_seconds, args, kwargs)

        return return_value_from_function

    return wrapped_function


def log_execution_time_summaries(logging_function):
    logging_function('Execution times summary (keep in mind thread_count was set to %s):', get_thread_count())

    for function_name in sorted(_execution_time_summary.keys()):
        summary_of_function = _execution_time_summary[function_name]
        elapsed_time = summary_of_function[0]
        average_time = summary_of_function[0] / summary_of_function[1]

        logging_function('    %5s times with average %5.2fs = sum %7.2fs : %s',
                         summary_of_function[1], average_time, elapsed_time, function_name)


def log_directories_summary(logging_function, start_path):

    directories_summary = {}
    directories = walk(start_path).next()[1]

    absolute_count_of_files = 0
    absolute_total_size = 0

    for file_name in walk(start_path).next()[2]:
        file_path = join(start_path, file_name)
        file_size = getsize(file_path)
        absolute_total_size += file_size
        absolute_count_of_files += 1

    directories_summary[start_path] = (absolute_count_of_files, absolute_total_size)

    for directory in directories:
        total_size = 0
        count_of_files = 0
        directory_path = join(start_path, directory)
        for dirpath, dirnames, filenames in walk(directory_path):
            for file_name in filenames:
                file_path = join(dirpath, file_name)
                file_size = getsize(file_path)
                total_size += file_size
                absolute_total_size += file_size
                count_of_files += 1
                absolute_count_of_files += 1

        directories_summary[directory_path] = (count_of_files, total_size)

    logging_function('Found %d files in directory "%s" with a total size of %d bytes', absolute_count_of_files, start_path, absolute_total_size)
    for directory in sorted(directories_summary.keys()):
        count_of_files = directories_summary[directory][0]
        total_size = directories_summary[directory][1]
        logging_function('    %5d files with total size of %10d bytes in directory "%s"', count_of_files, total_size, directory)
