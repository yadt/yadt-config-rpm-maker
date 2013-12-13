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

from logging import getLogger
from os import sep as PATH_SEPARATOR
from os.path import exists
from shutil import rmtree

from config_rpm_maker.config import build_config_viewer_host_directory
from config_rpm_maker.segment import Host
from config_rpm_maker.logutils import verbose

LOGGER = getLogger(__name__)


def clean_up_deleted_hosts_data(svn_service, revision):
    """ Deletes host directories within config viewer data
        when svn change set deletes host directory """

    deleted_paths = svn_service.get_deleted_paths(revision)

    if deleted_paths:
        LOGGER.debug("Change set contains %d deleted path(s).", len(deleted_paths))
        _delete_host_directories(deleted_paths)
    else:
        verbose(LOGGER).debug("Change set did not contain any deleted paths.")


def _delete_host_directories(deleted_paths):
    """ checks for each given path if it contains the svn_prefix for a host
        and if it does it will check if the rest of the path is a host name
        if so it will delete the corresponding directory """

    svn_prefix = Host().get_svn_prefix()
    svn_prefix_length = len(svn_prefix)

    for deleted_path in deleted_paths:
        if deleted_path.startswith(svn_prefix):
            host_name = deleted_path[svn_prefix_length:]
            if _is_a_host_name_and_not_a_path(host_name):
                _delete_host_directory(host_name)


def _is_a_host_name_and_not_a_path(host_name):
    """ checks if the given string contains a path separator character """

    return host_name.find(PATH_SEPARATOR) == -1


def _delete_host_directory(host_name):
    """ deletes the config viewer data for the given host name """

    host_directory = build_config_viewer_host_directory(host_name)
    if exists(host_directory):
        LOGGER.info('Deleting config viewer data for host "%s"', host_name)
        rmtree(host_directory)
    else:
        verbose(LOGGER).debug('Wanted to delete host directory "%s", but it did not exist.' % host_directory)
