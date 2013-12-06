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

__version__ = '2.0'

import traceback

from logging import DEBUG, INFO, getLogger
from os import getenv
from sys import argv

from config_rpm_maker import config
from config_rpm_maker.argumentvalidation import ensure_valid_repository_url, ensure_valid_revision
from config_rpm_maker.config import (ENVIRONMENT_VARIABLE_KEY_KEEP_WORKING_DIRECTORY,
                                     DEFAULT_NO_CLEAN_UP,
                                     KEY_SVN_PATH_TO_CONFIG,
                                     KEY_NO_CLEAN_UP,
                                     ConfigException)
from config_rpm_maker.configrpmmaker import ConfigRpmMaker
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.exitprogram import start_measuring_time, exit_program
from config_rpm_maker.logutils import (create_console_handler,
                                       create_sys_log_handler,
                                       log_configuration,
                                       log_process_id)
from config_rpm_maker.svnservice import SvnService
from config_rpm_maker.returncodes import (RETURN_CODE_CONFIGURATION_ERROR,
                                          RETURN_CODE_UNKOWN_EXCEPTION_OCCURRED,
                                          RETURN_CODE_EXCEPTION_OCCURRED,
                                          RETURN_CODE_SUCCESS,
                                          RETURN_CODE_EXECUTION_INTERRUPTED_BY_USER)
from config_rpm_maker.parsearguments import ARGUMENT_REPOSITORY, ARGUMENT_REVISION, OPTION_DEBUG, OPTION_NO_SYSLOG,\
    parse_arguments, apply_arguments_to_config

LOGGER = getLogger(__name__)

MESSAGE_SUCCESS = "Success."


def main():
    """
        This function will be called by the command line interface.
    """
    LOGGER.setLevel(DEBUG)

    try:
        arguments = parse_arguments(argv[1:], version='yadt-config-rpm-maker %s' % __version__)

        initialize_logging_to_console(arguments)
        repository_url, revision = extract_repository_url_and_revision_from_arguments(arguments)
        initialize_logging_to_syslog(arguments, revision)
        initialize_configuration(arguments)

        start_measuring_time()
        log_additional_information()
        start_building_configuration_rpms(repository_url, revision)

    except ConfigException as e:
        log_exception_message(e)
        return exit_program('Configuration error!', return_code=RETURN_CODE_CONFIGURATION_ERROR)

    except BaseConfigRpmMakerException as e:
        log_exception_message(e)
        return exit_program('An exception occurred!', return_code=RETURN_CODE_EXCEPTION_OCCURRED)

    except Exception:
        traceback.print_exc(5)
        return exit_program('An unknown exception occurred!', return_code=RETURN_CODE_UNKOWN_EXCEPTION_OCCURRED)

    except KeyboardInterrupt:
        return exit_program('Execution interrupted by user!', return_code=RETURN_CODE_EXECUTION_INTERRUPTED_BY_USER)

    exit_program(MESSAGE_SUCCESS, return_code=RETURN_CODE_SUCCESS)


def initialize_logging_to_console(arguments):
    """ Initializes the logging to console and
        appends the console handler to the root logger """
    console_log_level = determine_console_log_level(arguments)
    append_console_logger(LOGGER, console_log_level)


def initialize_configuration(arguments):
    """ Load the configuration file and applies the given arguments to the configuration. """
    config.load_configuration_file()
    apply_arguments_to_config(arguments)
    apply_environment_variables_to_configuration()


def apply_environment_variables_to_configuration():
    """ Will add configuration properties for the environment variables """

    if getenv(ENVIRONMENT_VARIABLE_KEY_KEEP_WORKING_DIRECTORY, DEFAULT_NO_CLEAN_UP):
        config.set_property(KEY_NO_CLEAN_UP, True)
    else:
        config.set_property(KEY_NO_CLEAN_UP, False)


def extract_repository_url_and_revision_from_arguments(arguments):
    """ Extracts the repository url and the revision from the given
        arguments ensuring that they have valid values. """
    repository_url = ensure_valid_repository_url(arguments[ARGUMENT_REPOSITORY])
    revision = ensure_valid_revision(arguments[ARGUMENT_REVISION])
    return repository_url, revision


def initialize_logging_to_syslog(arguments, revision):
    """ Initializes the logging to syslog and
        appends the syslog handler to the root logger if not omitted by the --no-syslog option """
    if not arguments[OPTION_NO_SYSLOG]:
        sys_log_handler = create_sys_log_handler(revision)
        LOGGER.addHandler(sys_log_handler)


def start_building_configuration_rpms(repository, revision):
    """ This function will start the process of building configuration rpms
        for the given configuration repository and the revision. """
    path_to_config = config.get(KEY_SVN_PATH_TO_CONFIG)
    svn_service = SvnService(base_url=repository, path_to_config=path_to_config)
    ConfigRpmMaker(revision=revision, svn_service=svn_service).build()  # first use case is post-commit hook. repo dir can be used as file:/// SVN URL


def determine_console_log_level(arguments):
    """ Determines the log level based on arguments and configuration """
    if arguments[OPTION_DEBUG]:
        log_level = DEBUG
    else:
        log_level = INFO

    return log_level


def append_console_logger(logger, console_log_level):
    """ Creates and appends a console log handler with the given log level """
    console_handler = create_console_handler(console_log_level)
    logger.addHandler(console_handler)

    if console_log_level == DEBUG:
        logger.debug("DEBUG logging is enabled")


def log_additional_information():
    """ Logs additional information as the process id and the configuration. """
    log_process_id(LOGGER.info)
    log_configuration(LOGGER.debug, config.get_properties(), config.get_file_path_of_loaded_configuration())


def log_exception_message(message):
    """ Logs the given multiline message line by line. """
    for line in str(message).split("\n"):
        LOGGER.error(line)
