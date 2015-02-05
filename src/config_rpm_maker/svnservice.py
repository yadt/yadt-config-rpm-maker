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

import pysvn
import os

from logging import getLogger

from time import ctime
from config_rpm_maker.utilities.logutils import log_elements_of_list
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.utilities.profiler import measure_execution_time

LOGGER = getLogger(__name__)

HOST_NAME_ENCODING = 'ascii'
PYSVN_DELETE_ACTION = 'D'


class SvnServiceException(BaseConfigRpmMakerException):
    error_info = "SVN Service error:\n"


class SvnService(object):

    def __init__(self, base_url, username=None, password=None, path_to_config='/config'):
        self.path_to_config = path_to_config
        self.base_url = base_url
        self.config_url = base_url + path_to_config
        LOGGER.info('Configuration repository is "%s".', self.config_url)
        self._initialize_pysvn_client(username, password)

    def _initialize_pysvn_client(self, username, password):
        self.client = pysvn.Client()
        self.client.set_auth_cache(True)

        if username:
            LOGGER.debug('Setting default username for subversion client to "%s".', username)
            self.client.set_default_username(username)

        if password:
            LOGGER.debug('Setting default password for subversion client.')
            self.client.set_default_password(password)

    def log_change_set_meta_information(self, revision):
        """ Logs the commit message, author and commit date. """

        log_entries = self.get_logs_for_revision(revision)
        for info in log_entries:
            LOGGER.info('Commit message is "%s" (%s, %s)', info.message.strip(), info.author, ctime(info.date))

    def get_logs_for_revision(self, revision):
        """ Returns the logs for the given revision of the repository at the config_url """

        try:
            logs = self.client.log(self.base_url, self._rev(revision), self._rev(revision),
                                   discover_changed_paths=True)
        except Exception as e:
            LOGGER.error('Retrieving change set information for revision "%s" in repository "%s" failed.',
                         revision, self.config_url)
            raise SvnServiceException(str(e))
        return logs

    def get_changed_paths_with_action(self, revision):
        """ Returns a list of all (path, action) tuples from the change set """

        log_entries = self.get_logs_for_revision(revision)

        path_to_config_slash = self.path_to_config + '/'
        start_pos = len(path_to_config_slash)
        action_and_path = []
        for info in log_entries:
            for path_obj in info.changed_paths:
                if not path_obj.path.startswith(path_to_config_slash):
                    continue
                changed_path = path_obj.path[start_pos:]
                action_and_path.append((changed_path, path_obj.action))

        return action_and_path

    def get_deleted_paths(self, revision):
        """ Returns all paths which have been deleted in the given revision"""

        paths_with_action = self.get_changed_paths_with_action(revision)

        return [element[0] for element in paths_with_action if element[1] == PYSVN_DELETE_ACTION]

    @measure_execution_time
    def get_changed_paths(self, revision):
        """ Returns the list of all changed paths from the change set with the given revision """

        path_with_action = self.get_changed_paths_with_action(revision)

        changed_paths_and_action = []
        changed_paths = []
        for path, action in path_with_action:
            changed_paths.append(path)
            changed_paths_and_action.append("%s (%s)" % (path, action))

        log_elements_of_list(LOGGER.debug, 'The commit change set contained %s changed path(s). Listing with svn action.', changed_paths_and_action)
        return changed_paths

    @measure_execution_time
    def get_hosts(self, revision):
        url = self.config_url + '/host'

        items = self.client.list(url, revision=self._rev(revision), depth=pysvn.depth.immediates)

        # remove first item
        items = items[1:]

        repos_paths = [item[0].repos_path.encode(HOST_NAME_ENCODING) for item in items]
        return [os.path.basename(repos_path) for repos_path in repos_paths]

    @measure_execution_time
    def export(self, svn_path, target_dir, revision):
        url = self._get_url(svn_path)

        self.exported_files = []
        self.client.callback_notify = self._callback_notify
        self.client.export(url, target_dir, force=True, revision=self._rev(revision))
        self.client.callback_notify = None

        normalized_length = len(os.path.normpath(target_dir) + os.sep)
        normalized_paths = [file_path[normalized_length:] for file_path in self.exported_files]
        normalized_paths = filter(lambda path: path != '', normalized_paths)

        return [(svn_path, path) for path in normalized_paths]

    @measure_execution_time
    def log(self, svn_path, revision, limit=0):
        url = self._get_url(svn_path)
        return self.client.log(url, pysvn.Revision(pysvn.opt_revision_kind.head), self._rev(revision), discover_changed_paths=True, limit=limit)

    def _rev(self, revision):
        return pysvn.Revision(pysvn.opt_revision_kind.number, int(revision))

    def _callback_notify(self, event):
        if event['action'] == pysvn.wc_notify_action.update_add:
            self.exported_files.append(event['path'])

    def _get_url(self, svn_path):
        if svn_path.startswith('/'):
            return self.base_url + svn_path
        else:
            return self.config_url + '/' + svn_path

    def __str__(self):
        return '{0}(base_url="{1}", path_to_config="{2}")'.format(SvnService.__name__, self.base_url, self.path_to_config)
