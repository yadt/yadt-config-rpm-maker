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


from subprocess import call
from integration_test_support import IntegrationTest, IntegrationTestException

from config_rpm_maker.config import KEY_SVN_PATH_TO_CONFIG, build_config_viewer_host_directory
from config_rpm_maker.configrpmmaker import ConfigRpmMaker, config
from config_rpm_maker.cleaner import clean_up_deleted_hosts_data
from config_rpm_maker.svnservice import SvnService


class CleanerIntegrationTests(IntegrationTest):

    def test_should_config_viewer_host_directory_when_directory_has_been_deleted_in_repository(self):

        svn_service = SvnService(base_url=self.repo_url, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        ConfigRpmMaker('1', svn_service).build()

        if call('svn delete -q -m "deleting host devweb01" %s/config/host/devweb01' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not delete test data.')

        clean_up_deleted_hosts_data(svn_service, '3')

        self.assert_path_exists(build_config_viewer_host_directory('berweb01'))
        self.assert_path_exists(build_config_viewer_host_directory('tuvweb01'))
        self.assert_path_does_not_exist(build_config_viewer_host_directory('devweb01'))

    def test_should_not_delete_host_directory_when_a_file_has_been_deleted_in_repository_host_directory(self):

        svn_service = SvnService(base_url=self.repo_url, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        ConfigRpmMaker('1', svn_service).build()

        if call('svn delete -q -m "deleting hostspecific file devweb01" %s/config/host/devweb01/host_specific_file' % self.repo_url, shell=True):
            raise IntegrationTestException('Could not delete test data.')

        clean_up_deleted_hosts_data(svn_service, '3')

        self.assert_path_exists(build_config_viewer_host_directory('berweb01'))
        self.assert_path_exists(build_config_viewer_host_directory('tuvweb01'))
        self.assert_path_exists(build_config_viewer_host_directory('devweb01'))




