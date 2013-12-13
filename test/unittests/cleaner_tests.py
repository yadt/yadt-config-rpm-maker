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

from mock import Mock, patch

from unittest_support import UnitTests

from config_rpm_maker.svnservice import SvnService
from config_rpm_maker.cleaner import clean_up_deleted_hosts_data


class CleanerTests(UnitTests):

    @patch('config_rpm_maker.cleaner.rmtree')
    def test_should_pass_through_if_change_set_is_empty(self, mock_rmtree):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_deleted_paths.return_value = []

        clean_up_deleted_hosts_data(mock_svn_service, '42')

        mock_svn_service.get_deleted_paths.assert_called_with('42')

    @patch('config_rpm_maker.cleaner.rmtree')
    def test_should_delete_config_viewer_host_directory_when_change_set_contains_delete_path_to_host_dir(self, mock_rmtree):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_deleted_paths.return_value = ['host/devweb01']

        clean_up_deleted_hosts_data(mock_svn_service, '42')

        mock_rmtree.assert_called_with('target/tmp/configviewer/hosts/devweb01')

    @patch('config_rpm_maker.cleaner.rmtree')
    def test_should_not_delete_config_viewer_host_directory_when_change_set_contains_delete_of_a_file_in_host_directory(self, mock_rmtree):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_deleted_paths.return_value = ['host/devweb01/host_specific_file']

        clean_up_deleted_hosts_data(mock_svn_service, '42')

        self.assert_mock_never_called(mock_rmtree)

    @patch('config_rpm_maker.cleaner.rmtree')
    def test_should_delete_two_config_viewer_host_directories_when_change_set_contains_two_deleted_paths(self, mock_rmtree):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_deleted_paths.return_value = ['host/devweb01', 'host/tuvweb01']

        clean_up_deleted_hosts_data(mock_svn_service, '42')

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/devweb01')
        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/tuvweb01')

    @patch('config_rpm_maker.cleaner.rmtree')
    def test_should_delete_three_config_viewer_host_directories_when_change_set_contains_three_deleted_paths(self, mock_rmtree):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_deleted_paths.return_value = ['host/devweb01', 'host/tuvweb01', 'host/tuvweb02']

        clean_up_deleted_hosts_data(mock_svn_service, '42')

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/devweb01')
        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/tuvweb01')
        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/tuvweb02')
