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


import traceback

from logging import DEBUG, Formatter, StreamHandler, getLogger
from logging.handlers import SysLogHandler
from math import ceil
from optparse import OptionParser
from sys import argv, exit, stderr, stdout
from time import time

from config_rpm_maker import config
from config_rpm_maker.config import DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL, DEFAULT_SYS_LOG_ADDRESS, DEFAULT_SYS_LOG_FORMAT
from config_rpm_maker.configRpmMaker import ConfigRpmMaker
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.svn import SvnService

ROOT_LOGGER_NAME = __name__

ARGUMENT_REPOSITORY = '<repository>'
ARGUMENT_REVISION = '<revision>'

USAGE_INFORMATION = """Usage: %prog repository revision [options]

Arguments:
  repository  absolute path to your subversion repository
  revision    subversion revision for which the configuration rpms are going to be built"""
OPTION_DEBUG = '--debug'
OPTION_DEBUG_HELP = "force DEBUG log level"
OPTION_VERSION = '--version'
OPTION_VERSION_HELP = "show version"

MESSAGE_SUCCESS = "Success."

RETURN_CODE_SUCCESS = 0
RETURN_CODE_VERSION = RETURN_CODE_SUCCESS
RETURN_CODE_NOT_ENOUGH_ARGUMENTS = 1
RETURN_CODE_REVISION_IS_NOT_AN_INTEGER = 2
RETURN_CODE_CONFIGURATION_ERROR = 3
RETURN_CODE_EXCEPTION_OCCURRED = 4
RETURN_CODE_UNKOWN_EXCEPTION_OCCURRED = 5

LOGGER = None


timestamp_at_start = 0


def create_root_logger(log_level=DEFAULT_LOG_LEVEL):
    """ Returnes a root_logger which logs to the console using the given log_level. """
    formatter = Formatter(DEFAULT_LOG_FORMAT)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    root_logger = getLogger(ROOT_LOGGER_NAME)
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    if log_level == DEBUG:
        root_logger.debug("DEBUG logging is enabled")
    return root_logger


def create_sys_log_handler(revision):
    """ Create a logger handler which logs to sys log and uses the given revision within the format """
    sys_log_handler = SysLogHandler(address=DEFAULT_SYS_LOG_ADDRESS)
    formatter = Formatter(DEFAULT_SYS_LOG_FORMAT.format(revision))
    sys_log_handler.setFormatter(formatter)

    return sys_log_handler


def log_configuration_to_logger(logger):
    logger.debug('Loaded configuration file "%s"', config.configuration_file_path)

    keys = sorted(config.configuration.keys())
    max_length = len(max(keys, key=len))

    for key in keys:
        indentet_key = key.ljust(max_length)
        logger.debug('Configuraton property %s = "%s"', indentet_key, config.configuration[key])


def start_measuring_time():
    """ Start measuring the time. This is required to calculate the elapsed time. """
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


def parse_arguments(argv, version):
    """
        Parses the given command line arguments.

        if -h or --help is given it will display the print the help screen and exit
        if OPTION_VERSION is given it will display the version information and exit

        Otherwise it will return a dictionary containing the keys and values for
            OPTION_DEBUG: boolean, True if option --debug is given
            ARGUMENT_REPOSITORY: string, the first argument
            ARGUMENT_REVISION: string, the second argument
    """

    usage = USAGE_INFORMATION
    parser = OptionParser(usage=usage)
    parser.add_option("", OPTION_DEBUG,
                      action="store_true", dest="debug", default=False,
                      help=OPTION_DEBUG_HELP)
    parser.add_option("", OPTION_VERSION,
                      action="store_true", dest="version", default=False,
                      help=OPTION_VERSION_HELP)
    values, args = parser.parse_args(argv)

    if values.version:
        stdout.write(version + '\n')
        return exit(RETURN_CODE_VERSION)

    if len(args) < 2:
        parser.print_help()
        return exit(RETURN_CODE_NOT_ENOUGH_ARGUMENTS)

    arguments = {OPTION_DEBUG: values.debug or False,
                 ARGUMENT_REPOSITORY: args[0],
                 ARGUMENT_REVISION: args[1]}

    return arguments


def determine_log_level(arguments):
    """ Determines the log level based on arguments and configuration """
    try:
        if arguments[OPTION_DEBUG]:
            log_level = DEBUG
        else:
            log_level = config.get_log_level()

    except config.ConfigException as e:
        stderr.write(str(e) + "\n")
        exit(RETURN_CODE_CONFIGURATION_ERROR)

    return log_level


def build_configuration_rpms_from(repository, revision):
    try:
        base_url = 'file://{0}'.format(repository)
        path_to_config = config.get('svn_path_to_config')
        svn_service = SvnService(base_url=base_url, path_to_config=path_to_config)
        ConfigRpmMaker(revision=revision, svn_service=svn_service).build()  # first use case is post-commit hook. repo dir can be used as file:/// SVN URL

    except BaseConfigRpmMakerException as e:
        for line in str(e).split("\n"):
            LOGGER.error(line)
        exit_program('An exception occurred!', return_code=RETURN_CODE_EXCEPTION_OCCURRED)

    except Exception:
        traceback.print_exc(5)
        exit_program('An unknown exception occurred!', return_code=RETURN_CODE_UNKOWN_EXCEPTION_OCCURRED)

    exit_program(MESSAGE_SUCCESS, return_code=RETURN_CODE_SUCCESS)


def main():
    start_measuring_time()
    arguments = parse_arguments(argv[1:], version='yadt-config-rpm-maker 2.0')
    config.load_configuration_file()
    log_level = determine_log_level(arguments)

    global LOGGER
    LOGGER = create_root_logger(log_level)
    LOGGER.debug('Argument repository is "%s"', str(arguments[ARGUMENT_REPOSITORY]))
    LOGGER.debug('Argument revision is "%s"', str(arguments[ARGUMENT_REVISION]))
    log_configuration_to_logger(LOGGER)

    revision = arguments[ARGUMENT_REVISION]
    if not revision.isdigit():
        exit_program('Given revision "%s" is not an integer.' % revision, return_code=RETURN_CODE_REVISION_IS_NOT_AN_INTEGER)

    sys_log_handler = create_sys_log_handler(revision)
    LOGGER.addHandler(sys_log_handler)

    repository = arguments[ARGUMENT_REPOSITORY]

    build_configuration_rpms_from(repository, revision)
