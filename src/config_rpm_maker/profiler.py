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


from functools import wraps
from logging import getLogger
from math import ceil
from time import time
from os import walk
from os.path import join, getsize

from config_rpm_maker.config import KEY_THREAD_COUNT, get

LOGGER = getLogger(__name__)

NUMBER_OF_LARGEST_FILES_TO_LOG = 10
LOG_EACH_MEASUREMENT = False

_summary = {}


def round_to_two_decimals_after_dot(elapsed_time_in_seconds):
    return ceil(elapsed_time_in_seconds * 100) / 100


def measure_execution_time(original_function):

    def process_measurement(elapsed_time_in_seconds, args, kwargs):
        arguments = ', '.join(map(lambda arg: arg if type(arg) == str else str(arg), args[1:]))

        if len(kwargs.keys()) == 0:
            key_word_arguments = ""
        else:
            key_word_arguments = ", " + str(kwargs)

        if len(args) > 0:
            function_name = "%s.%s" % (args[0].__class__.__name__, original_function.__name__)
        else:
            function_name = original_function.__name__

        if function_name not in _summary.keys():
            _summary[function_name] = [elapsed_time_in_seconds, 1]
        else:
            _summary[function_name][0] += elapsed_time_in_seconds
            _summary[function_name][1] += 1

        if LOG_EACH_MEASUREMENT:
            function_call = '%s(%s%s)' % (function_name, arguments, key_word_arguments)
            rounded_elapsed_time_in_seconds = round_to_two_decimals_after_dot(elapsed_time_in_seconds)
            LOGGER.debug('Took %ss to perform %s', rounded_elapsed_time_in_seconds, function_call)

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
    logging_function('Execution times summary (keep in mind thread_count was set to %s):', get(KEY_THREAD_COUNT))

    for function_name in sorted(_summary.keys()):
        summary_of_function = _summary[function_name]
        rounded_elapsed_time = round_to_two_decimals_after_dot(summary_of_function[0])
        average_time = round_to_two_decimals_after_dot(summary_of_function[0] / summary_of_function[1])

        logging_function('    %5s times with average %5ss = sum %7ss : %s',
                         summary_of_function[1], average_time, rounded_elapsed_time, function_name)


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
