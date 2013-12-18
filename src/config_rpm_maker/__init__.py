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
from sys import argv

from config_rpm_maker.cli.argumentvalidation import ensure_valid_repository_url, ensure_valid_revision
from config_rpm_maker.cli.exitprogram import start_measuring_time, exit_program
from config_rpm_maker.cli.returncodes import (RETURN_CODE_CONFIGURATION_ERROR,
                                              RETURN_CODE_UNKOWN_EXCEPTION_OCCURRED,
                                              RETURN_CODE_EXCEPTION_OCCURRED,
                                              RETURN_CODE_SUCCESS,
                                              RETURN_CODE_EXECUTION_INTERRUPTED_BY_USER)
from config_rpm_maker.cli.parsearguments import (ARGUMENT_REPOSITORY,
                                                 ARGUMENT_REVISION,
                                                 OPTION_NO_SYSLOG,
                                                 apply_arguments_to_config,
                                                 determine_console_log_level,
                                                 parse_arguments)
from config_rpm_maker.configuration import get_svn_path_to_config, ConfigurationException
from config_rpm_maker.configrpmmaker import ConfigRpmMaker
from config_rpm_maker.cleaner import clean_up_deleted_hosts_data
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.utilities.logutils import (append_console_logger,
                                                 create_sys_log_handler,
                                                 log_additional_information,
                                                 log_exception_message)
from config_rpm_maker.svnservice import SvnService

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
        building_configuration_rpms_and_clean_host_directories(repository_url, revision)

    except ConfigurationException as e:
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
    configuration.load_configuration_file()
    apply_arguments_to_config(arguments)


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


def building_configuration_rpms_and_clean_host_directories(repository, revision):
    """ This function will start the process of building configuration rpms
        for the given configuration repository and the revision. """

    path_to_config = get_svn_path_to_config()
    svn_service = SvnService(base_url=repository, path_to_config=path_to_config)
    svn_service.log_change_set_meta_information(revision)
    ConfigRpmMaker(revision=revision, svn_service=svn_service).build()
    clean_up_deleted_hosts_data(svn_service, revision)
