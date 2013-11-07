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

"""yadt-config-rpm-maker

Usage:
  config-rpm-maker <repository> <revision> [--debug]
  config-rpm-maker -h | --help
  config-rpm-maker --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --debug       Set log level to debug.
"""

from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from docopt import docopt

from config_rpm_maker import main

LOGGING_FORMAT = "[%(levelname)5s] %(message)s"
ROOT_LOGGER_NAME = "config_rpm_maker"
OPTION_DEBUG = '--debug'


def initialiaze_root_logger(log_level=INFO):
    """ Returnes a root_logger which logs to the console using the given log_level. """
    formatter = Formatter(LOGGING_FORMAT)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger = getLogger(ROOT_LOGGER_NAME)
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    return root_logger


if __name__ == "__main__":
    arguments = docopt(__doc__, version='yadt-config-rpm-maker 2.0')

    if arguments[OPTION_DEBUG]:
        LOGGER = initialiaze_root_logger(DEBUG)
    else:
        LOGGER = initialiaze_root_logger()

    main(arguments)
