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

from unittest import TestCase
from mock import Mock

from config_rpm_maker.svnservice import SvnServiceException, SvnService


class SvnServiceTests(TestCase):

    def test_should_ensure_that_all_returned_host_names_are_ordinary_strings(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = '/path to repository/config'
        mock_svn_service.client = Mock()
        item0 = Mock()
        item0.repos_path = "get_hosts removes the first element - so this will never show up"
        item1 = Mock()
        item1.repos_path = "bar"
        item2 = Mock()
        item2.repos_path = u"spam"
        mock_svn_service.client.list.return_value = [(item0,), (item1,), (item2,)]

        actual_host_names = SvnService.get_hosts(mock_svn_service, 123)

        self.assert_is_ordinary_string(actual_host_names[0])
        self.assert_is_ordinary_string(actual_host_names[1])

    def assert_is_ordinary_string(self, text):
        self.assertTrue(isinstance(text, str), '"%s" is NOT a ordinary string!' % text)


class GetLogsForRevision(TestCase):

    def test_should_raise_exception_when_pysvn_client_fails_to_log(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = 'svn://url/for/configuration/repository'
        mock_svn_service.path_to_config = '/config'
        mock_svn_service.client = Mock()
        mock_svn_service.client.log.side_effect = Exception("Aaarrrgggghh...")

        self.assertRaises(SvnServiceException, SvnService.get_logs_for_revision, mock_svn_service, '1980')

    def test_should_return_logs_for_revision(self):
        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = 'svn://url/for/configuration/repository'
        mock_svn_service.path_to_config = '/config'
        mock_svn_service.client = Mock()
        mock_logs = Mock()
        mock_svn_service.client.log.return_value = mock_logs

        actual = SvnService.get_logs_for_revision(mock_svn_service, '1980')

        self.assertEqual(mock_logs, actual)


class GetChangedPathsWithActionTests(TestCase):

    def test_should_return_list_with_empty_string_and_action_string_when_configuration_directory_has_been_created_in_commit(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = 'svn://url/for/configuration/repository'
        mock_svn_service.path_to_config = '/config'
        mock_info = Mock()
        mock_path_object = Mock()
        mock_path_object.path = '/config/'
        mock_path_object.action = 'A'
        mock_info.changed_paths = [mock_path_object]
        mock_svn_service.get_logs_for_revision.return_value = [mock_info]

        actual = SvnService.get_changed_paths_with_action(mock_svn_service, '1980')

        self.assertEqual([('', 'A')], actual)

    def test_should_return_list_with_directory_name_and_action_for_path_to_file_when_a_file_has_been_added(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = 'svn://url/for/configuration/repository'
        mock_svn_service.path_to_config = '/config'
        mock_svn_service.client = Mock()
        mock_info = Mock()
        mock_path_object_1 = Mock()
        mock_path_object_1.path = '/config/'
        mock_path_object_1.action = 'A'
        mock_info.changed_paths = [mock_path_object_1]
        mock_path_object_2 = Mock()
        mock_path_object_2.path = '/config/spam.egg'
        mock_path_object_2.action = 'A'
        mock_info.changed_paths = [mock_path_object_1, mock_path_object_2]
        mock_svn_service.get_logs_for_revision.return_value = [mock_info]

        actual = SvnService.get_changed_paths_with_action(mock_svn_service, '1980')

        self.assertEqual([('', 'A'), ('spam.egg', 'A')], actual)

    def test_should_return_list_with_tuples_including_one_tuple_which_has_a_delete_action(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = 'svn://url/for/configuration/repository'
        mock_svn_service.path_to_config = '/config'
        mock_svn_service.client = Mock()
        mock_info = Mock()
        mock_path_object_1 = Mock()
        mock_path_object_1.path = '/config/'
        mock_path_object_1.action = 'A'
        mock_info.changed_paths = [mock_path_object_1]
        mock_path_object_2 = Mock()
        mock_path_object_2.path = '/config/spam.egg'
        mock_path_object_2.action = 'A'
        mock_path_object_3 = Mock()
        mock_path_object_3.path = '/config/foo.bar'
        mock_path_object_3.action = 'D'
        mock_info.changed_paths = [mock_path_object_1, mock_path_object_2, mock_path_object_3]
        mock_svn_service.get_logs_for_revision.return_value = [mock_info]

        actual = SvnService.get_changed_paths_with_action(mock_svn_service, '1980')

        self.assertEqual([('', 'A'), ('spam.egg', 'A'), ('foo.bar', 'D')], actual)


class GetChangedPathsTests(TestCase):

    def test_should_return_list_with_empty_string_when_configuration_directory_has_been_created_in_commit(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('', 'A')]

        actual = SvnService.get_changed_paths(mock_svn_service, '1980')

        self.assertEqual([''], actual)

    def test_should_return_list_with_directory_name_and_path_to_file_when_a_file_has_been_added(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('', 'A'), ('spam.egg', 'A')]

        actual = SvnService.get_changed_paths(mock_svn_service, '1980')

        self.assertEqual(['', 'spam.egg'], actual)

    def test_should_return_list_with_directory_name_and_path_to_file_when_a_file_has_been_added_and_another_has_been_deleted(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('', 'A'), ('spam.egg', 'A'), ('foo.bar', 'D')]

        actual = SvnService.get_changed_paths(mock_svn_service, '1980')

        self.assertEqual(['', 'spam.egg', 'foo.bar'], actual)


class GetDeletedPathsTests(TestCase):

    def test_should_return_empty_list_empty_when_configuration_directory_has_been_created_in_commit(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('', 'A')]

        actual = SvnService.get_deleted_paths(mock_svn_service, '1980')

        self.assertEqual([], actual)

    def test_should_return_list_with_directory_name_and_path_to_file_when_a_file_has_been_added(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('spam.egg', 'D')]

        actual = SvnService.get_deleted_paths(mock_svn_service, '1980')

        self.assertEqual(['spam.egg'], actual)

    def test_should_only_return_list_with_directory_name_and_path_to_file_when_a_file_has_been_added(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('foo.bar', 'A'), ('spam.egg', 'D')]

        actual = SvnService.get_deleted_paths(mock_svn_service, '1980')

        self.assertEqual(['spam.egg'], actual)

    def test_should_only_return_list_with_directory_name_and_path_to_file_when_several_files_have_been_added_and_deleted(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.get_changed_paths_with_action.return_value = [('', 'A'), ('example', 'D'), ('foo.bar', 'A'), ('spam.egg', 'D'), ('test/123', 'A')]

        actual = SvnService.get_deleted_paths(mock_svn_service, '1980')

        self.assertEqual(['example', 'spam.egg'], actual)
