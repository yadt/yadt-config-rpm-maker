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

Arguments:
  repository    absolute path to your subversion repository
  revision      subversion revision number for which the configuration rpms are going to be built

Options:
  -h --help     Show this screen.
  --version     Show version.
  --debug       Force DEBUG log level.
"""
import traceback

from docopt import docopt
from logging import DEBUG, Formatter, StreamHandler, getLogger
from math import ceil
from sys import exit, stderr
from time import time

from config_rpm_maker import config
from config_rpm_maker.configRpmMaker import ConfigRpmMaker
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.svn import SvnService

ARGUMENT_REVISION = '<revision>'
ARGUMENT_REPOSITORY = '<repository>'

OPTION_DEBUG = '--debug'

LOGGING_FORMAT = "[%(levelname)5s] %(message)s"
ROOT_LOGGER_NAME = __name__

MESSAGE_SUCCESS = "Success."

LOGGER = None


timestamp_at_start = 0


def create_root_logger(log_level=config.DEFAULT_LOG_LEVEL):
    """ Returnes a root_logger which logs to the console using the given log_level. """
    formatter = Formatter(LOGGING_FORMAT)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger = getLogger(ROOT_LOGGER_NAME)
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    return root_logger


def log_configuration():
    LOGGER.debug('Loaded configuration file "%s"', config.configuration_file_path)

    keys = sorted(config.configuration.keys())
    max_length = len(max(keys, key=len))

    for key in keys:
        indentet_key = key.ljust(max_length)
        LOGGER.debug('Configuraton property %s = "%s"', indentet_key, config.configuration[key])


def start_measuring_time():
    global timestamp_at_start
    timestamp_at_start = time()


def exit_program(message, return_code):
    """ Logs the given message and exits with given return code.

    feedback is a tuple: (message, return_code)
    """
    elapsed_time_in_seconds = time() - timestamp_at_start
    elapsed_time_in_seconds = ceil(elapsed_time_in_seconds * 100) / 100
    LOGGER.info('Elapsed time: {0}s'.format(elapsed_time_in_seconds))

    if return_code == 0:
        LOGGER.info(message)
    else:
        LOGGER.error(message)

    exit(return_code)


def main():
    arguments = docopt(__doc__, version='yadt-config-rpm-maker 2.0')
    start_measuring_time()

    global LOGGER
    try:
        config.load_configuration_file()

        if arguments[OPTION_DEBUG]:
            LOGGER = create_root_logger(DEBUG)
            LOGGER.debug("DEBUG logging is enabled")
        else:
            log_level = config.get_log_level()
            LOGGER = create_root_logger(log_level)

    except config.ConfigException as e:
        stderr.write(str(e) + "\n")
        exit(1)

    LOGGER.debug('Argument repository is "%s"', str(arguments[ARGUMENT_REPOSITORY]))
    LOGGER.debug('Argument revision is "%s"', str(arguments[ARGUMENT_REVISION]))

    log_configuration()

    revision = arguments[ARGUMENT_REVISION]
    if not revision.isdigit():
        exit_program('Given revision "%s" is not a integer.' % revision, return_code=1)

    repository = arguments[ARGUMENT_REPOSITORY]

    try:
        # first use case is post-commit hook. repo dir can be used as file:/// SVN URL
        svn_service = SvnService(base_url='file://{0}'.format(repository),
                                 path_to_config=config.get('svn_path_to_config'))
        ConfigRpmMaker(revision=revision, svn_service=svn_service).build()

    except BaseConfigRpmMakerException as e:
        for line in str(e).split("\n"):
            LOGGER.error(line)
        exit_program('An exception occurred!', return_code=2)

    except Exception:
        traceback.print_exc(5)
        exit_program('An unknown exception occurred!', return_code=3)

    exit_program(MESSAGE_SUCCESS, return_code=0)
