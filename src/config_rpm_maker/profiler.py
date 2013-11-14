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

LOGGER = getLogger(__name__)


def measure_execution_time(original_function):
    @wraps(original_function)
    def wrapped_function(*args, **kwargs):
        start_time = time()

        return_value_from_function = original_function(*args, **kwargs)

        end_time = time()
        elapsed_time_in_seconds = end_time - start_time
        elapsed_time_in_seconds = ceil(elapsed_time_in_seconds * 100) / 100

        arguments = ', '.join(map(lambda arg: arg if type(arg) == str else str(arg), args[1:]))

        if len(kwargs.keys()) == 0:
            key_word_arguments = ""
        else:
            key_word_arguments = ", " + str(kwargs)

        if len(args) > 0:
            function_name = "%s.%s" % (args[0].__class__.__name__, original_function.__name__)
        else:
            function_name = original_function.__name__
        function_call = '%s(%s%s)' % (function_name, arguments, key_word_arguments)
        LOGGER.info('Took %ss to perform %s', elapsed_time_in_seconds, function_call)

        return return_value_from_function

    return wrapped_function
