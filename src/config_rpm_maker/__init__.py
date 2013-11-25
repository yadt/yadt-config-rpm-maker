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

from logging import DEBUG, getLogger
from sys import argv, exit, stderr

from config_rpm_maker import config
from config_rpm_maker.argumentvalidation import ensure_valid_repository_url, ensure_valid_revision
from config_rpm_maker.config import KEY_SVN_PATH_TO_CONFIG
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
                                          RETURN_CODE_SUCCESS)
from config_rpm_maker.parsearguments import ARGUMENT_REPOSITORY, ARGUMENT_REVISION, OPTION_DEBUG, OPTION_NO_SYSLOG,\
    parse_arguments, apply_arguments_to_config

LOGGER = getLogger(__name__)

MESSAGE_SUCCESS = "Success."


def determine_console_log_level(arguments):
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
        path_to_config = config.get(KEY_SVN_PATH_TO_CONFIG)
        svn_service = SvnService(base_url=repository, path_to_config=path_to_config)
        ConfigRpmMaker(revision=revision, svn_service=svn_service).build()  # first use case is post-commit hook. repo dir can be used as file:/// SVN URL

    except BaseConfigRpmMakerException as e:
        for line in str(e).split("\n"):
            LOGGER.error(line)
        return exit_program('An exception occurred!', return_code=RETURN_CODE_EXCEPTION_OCCURRED)

    except Exception:
        traceback.print_exc(5)
        return exit_program('An unknown exception occurred!', return_code=RETURN_CODE_UNKOWN_EXCEPTION_OCCURRED)

    exit_program(MESSAGE_SUCCESS, return_code=RETURN_CODE_SUCCESS)


def append_console_logger(logger, console_log_level):
    """ Creates and appends a console log handler with the given log level """
    console_handler = create_console_handler(console_log_level)
    logger.addHandler(console_handler)

    if console_log_level == DEBUG:
        logger.debug("DEBUG logging is enabled")


def main():
    LOGGER.setLevel(DEBUG)

    arguments = parse_arguments(argv[1:], version='yadt-config-rpm-maker %s' % __version__)

    config.load_configuration_file()
    console_log_level = determine_console_log_level(arguments)
    append_console_logger(LOGGER, console_log_level)
    apply_arguments_to_config(arguments)

    repository_url = ensure_valid_repository_url(arguments[ARGUMENT_REPOSITORY])
    revision = ensure_valid_revision(arguments[ARGUMENT_REVISION])

    if not arguments[OPTION_NO_SYSLOG]:
        sys_log_handler = create_sys_log_handler(revision)
        LOGGER.addHandler(sys_log_handler)

    start_measuring_time()
    log_process_id(LOGGER.info)
    log_configuration(LOGGER.debug, config._configuration, config.configuration_file_path)

    build_configuration_rpms_from(repository_url, revision)
