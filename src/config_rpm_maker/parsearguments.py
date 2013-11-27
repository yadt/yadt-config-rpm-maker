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

from optparse import OptionParser
from sys import stdout, exit

from config_rpm_maker.returncodes import RETURN_CODE_NOT_ENOUGH_ARGUMENTS, RETURN_CODE_VERSION
from config_rpm_maker.config import KEY_RPM_UPLOAD_COMMAND, KEY_CONFIG_VIEWER_ONLY, setvalue


ARGUMENT_REPOSITORY = '<repository-url>'
ARGUMENT_REVISION = '<revision>'

USAGE_INFORMATION = """Usage: %prog repo-url revision [options]

Arguments:
  repo-url    URL to subversion repository or absolute path on localhost
  revision    subversion revision for which the configuration rpms are going to be built"""

OPTION_DEBUG = '--debug'
OPTION_DEBUG_HELP = "force DEBUG log level on console"

OPTION_NO_SYSLOG = '--no-syslog'
OPTION_NO_SYSLOG_HELP = "switch logging of debug information to syslog off"

OPTION_VERSION = '--version'
OPTION_VERSION_HELP = "show version"

OPTION_RPM_UPLOAD_CMD = '--rpm-upload-cmd'
OPTION_RPM_UPLOAD_CMD_HELP = 'Overwrite rpm_upload_config in config file'

OPTION_CONFIG_VIEWER_ONLY = '--config-viewer-only'
OPTION_CONFIG_VIEWER_ONLY_HELP = 'Only generated files for config viewer. Skip RPM build and upload.'


def parse_arguments(argv, version):
    """
        Parses the given command line arguments.

        if -h or --help is given it will display the print the help screen and exit
        if OPTION_VERSION is given it will display the version information and exit

        Otherwise it will return a dictionary containing the keys and values for
            OPTION_DEBUG: boolean, True if option --debug is given
            OPTION_NO_SYSLOG: boolean, True if option --no-syslog is given
            ARGUMENT_REPOSITORY: string, the first argument
            ARGUMENT_REVISION: string, the second argument
    """

    usage = USAGE_INFORMATION
    parser = OptionParser(usage=usage)
    parser.add_option("", OPTION_DEBUG,
                      action="store_true", dest="debug", default=False,
                      help=OPTION_DEBUG_HELP)
    parser.add_option("", OPTION_NO_SYSLOG,
                      action="store_true", dest="no_syslog", default=False,
                      help=OPTION_NO_SYSLOG_HELP)
    parser.add_option("", OPTION_VERSION,
                      action="store_true", dest="version", default=False,
                      help=OPTION_VERSION_HELP)
    parser.add_option("", OPTION_RPM_UPLOAD_CMD,
                      dest='rpm_upload_command', default=False,
                      help=OPTION_RPM_UPLOAD_CMD_HELP)
    parser.add_option("", OPTION_CONFIG_VIEWER_ONLY,
                      action="store_true", dest='config_viewer_only', default=False,
                      help=OPTION_CONFIG_VIEWER_ONLY_HELP)
    values, args = parser.parse_args(argv)

    if values.version:
        stdout.write(version + '\n')
        return exit(RETURN_CODE_VERSION)

    if len(args) < 2:
        parser.print_help()
        return exit(RETURN_CODE_NOT_ENOUGH_ARGUMENTS)

    arguments = {OPTION_DEBUG: values.debug or False,
                 OPTION_NO_SYSLOG: values.no_syslog or False,
                 OPTION_RPM_UPLOAD_CMD: values.rpm_upload_command,
                 OPTION_CONFIG_VIEWER_ONLY: values.config_viewer_only,
                 ARGUMENT_REPOSITORY: args[0],
                 ARGUMENT_REVISION: args[1]}

    return arguments


def apply_arguments_to_config(arguments):
    """ Overrides configuration properties if command line options are specified. """

    if arguments[OPTION_RPM_UPLOAD_CMD]:
        setvalue(KEY_RPM_UPLOAD_COMMAND, arguments[OPTION_RPM_UPLOAD_CMD])

    if arguments[OPTION_CONFIG_VIEWER_ONLY]:
        setvalue(KEY_CONFIG_VIEWER_ONLY, arguments[OPTION_CONFIG_VIEWER_ONLY])
