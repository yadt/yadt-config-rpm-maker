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
from mock import Mock, patch
from subprocess import PIPE

from unittest_support import UnitTests

import config_rpm_maker

from config_rpm_maker.hostrpmbuilder import CouldNotBuildRpmException, ConfigDirAlreadyExistsException, CouldNotCreateConfigDirException, HostRpmBuilder


class ConstructorTests(TestCase):

    def setUp(self):

        self.mock_svn_service_queue = Mock()
        self.mock_host_rpm_builder = Mock(HostRpmBuilder)

    def call_constructor(self):

        HostRpmBuilder.__init__(self.mock_host_rpm_builder,
                                thread_name='thread-name',
                                hostname='hostname',
                                revision='3485',
                                work_dir='/tmp',
                                svn_service_queue=self.mock_svn_service_queue)

    def test_should_use_given_thread_name(self):

        self.call_constructor()

        self.assertEqual('thread-name', self.mock_host_rpm_builder.thread_name)

    def test_should_use_given_host_name(self):

        self.call_constructor()

        self.assertEqual('hostname', self.mock_host_rpm_builder.hostname)

    def test_should_use_given_revision(self):

        self.call_constructor()

        self.assertEqual('3485', self.mock_host_rpm_builder.revision)

    def test_should_use_given_working_directory(self):

        self.call_constructor()

        self.assertEqual('/tmp', self.mock_host_rpm_builder.work_dir)

    def test_should_use_no_error_logging_handler_as_default(self):

        self.call_constructor()

        self.assertEqual(None, self.mock_host_rpm_builder.error_logging_handler)

    def test_should_create_logger(self):

        self.call_constructor()

        self.mock_host_rpm_builder._create_logger.assert_called_with()

    def test_should_use_given_svn_service_queue(self):

        self.call_constructor()

        self.assertEqual(self.mock_svn_service_queue, self.mock_host_rpm_builder.svn_service_queue)

    @patch('config_rpm_maker.hostrpmbuilder.get_config_rpm_prefix')
    def test_should_read_config_rpm_prefix_from_configuration(self, mock_config):

        mock_config.return_value = 'config-rpm-prefix'

        self.call_constructor()

        self.assertEqual('config-rpm-prefix', self.mock_host_rpm_builder.config_rpm_prefix)

    def test_should_build_host_configuration_directory_using_working_directory_and_config_rpm_prefix_and_hostname(self):

        self.call_constructor()

        self.assertEqual('/tmp/yadt-config-hostname', self.mock_host_rpm_builder.host_config_dir)

    def test_should_build_variables_directory_using_host_configuration_directory(self):

        self.call_constructor()

        self.assertEqual('/tmp/yadt-config-hostname/VARIABLES', self.mock_host_rpm_builder.variables_dir)

    def test_should_build_path_to_rpm_requires_file_using_variables_directory(self):

        self.call_constructor()

        self.assertEqual('/tmp/yadt-config-hostname/VARIABLES/RPM_REQUIRES', self.mock_host_rpm_builder.rpm_requires_path)

    def test_should_build_path_to_rpm_provides_file_using_variables_directory(self):

        self.call_constructor()

        self.assertEqual('/tmp/yadt-config-hostname/VARIABLES/RPM_PROVIDES', self.mock_host_rpm_builder.rpm_provides_path)

    def test_should_build_path_to_spec_file_using_host_configuration_directory_and_config_rpm_prefix_and_hostname(self):

        self.call_constructor()

        self.assertEqual('/tmp/yadt-config-hostname/yadt-config-hostname.spec', self.mock_host_rpm_builder.spec_file_path)

    @patch('config_rpm_maker.hostrpmbuilder.build_config_viewer_host_directory')
    def test_should_use_hostname_and_revision_to_build_config_viewer_hosts_directory(self, mock_build_config_viewer_host_directory):

        mock_build_config_viewer_host_directory.return_value = 'config-viewer-host-directory'

        self.call_constructor()

        mock_build_config_viewer_host_directory.assert_called_with('hostname', revision='3485')
        self.assertEqual('config-viewer-host-directory', self.mock_host_rpm_builder.config_viewer_host_dir)

    def test_should_build_rpm_build_directory_using_working_directory(self):

        self.call_constructor()

        self.assertEqual('/tmp/rpmbuild', self.mock_host_rpm_builder.rpm_build_dir)

    def test_should_have_error_file_path(self):

        self.call_constructor()

        self.assertEqual('/tmp/hostname.error', self.mock_host_rpm_builder.error_file_path)

    def test_should_have_output_file_path(self):

        self.call_constructor()

        self.assertEqual('/tmp/hostname.output', self.mock_host_rpm_builder.output_file_path)


class BuildTests(TestCase):

    def _create_mock_overlay_segment_method(self):
        def fake_overlay_segment(segment):
            return ['%s-svn-paths' % segment], ['%s-exported-paths' % segment], ['%s-requires' % segment], [
                '%s-provides' % segment]

        mock_overlay_segment = Mock()
        mock_overlay_segment.side_effect = fake_overlay_segment
        return mock_overlay_segment

    def setUp(self):
        self.variables_directory = '/path/to/variables-directory'
        self.rpm_requires_path = '/path/to/rpm-requires'

        mock_host_rpm_builder = Mock(HostRpmBuilder)
        mock_host_rpm_builder.thread_name = 'Mock-Thread'
        mock_host_rpm_builder.hostname = 'devweb01'
        mock_host_rpm_builder.logger = Mock()
        mock_host_rpm_builder.revision = '123'
        mock_host_rpm_builder.host_config_dir = '/foo/bar'
        mock_host_rpm_builder.variables_dir = self.variables_directory
        mock_host_rpm_builder.rpm_requires_path = self.rpm_requires_path
        mock_host_rpm_builder.rpm_provides_path = 'rpm-provides-path'
        mock_host_rpm_builder.config_viewer_host_dir = 'config_viewer_host_dir'
        mock_host_rpm_builder.config_rpm_prefix = "any-config-prefix"

        mock_host_rpm_builder._overlay_segment = self._create_mock_overlay_segment_method()

        self.mock_host_rpm_builder = mock_host_rpm_builder

    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_check_if_config_directory_already_exists_and_raise_exception_when_directory_already_exists(self, mock_exists):

        mock_exists.return_value = True

        self.assertRaises(ConfigDirAlreadyExistsException, HostRpmBuilder.build, self.mock_host_rpm_builder)

        mock_exists.assert_called_with('/foo/bar')

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_raise_exception_when_creation_of_configuration_directory_fails(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        mock_mkdir.side_effect = Exception('Oh noooo ...')

        self.assertRaises(CouldNotCreateConfigDirException, HostRpmBuilder.build, self.mock_host_rpm_builder)

        mock_mkdir.assert_called_with('/foo/bar')

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_get_overlay_segments_for_each_segment_in_overlay_order(self, mock_exists, mock_mkdir, mock_overlay_order):
        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._overlay_segment.assert_any_call('segment1')
        self.mock_host_rpm_builder._overlay_segment.assert_any_call('segment2')
        self.mock_host_rpm_builder._overlay_segment.assert_any_call('segment3')

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_create_variables_directory_if_it_does_not_exist(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        mock_mkdir.assert_any_call('/path/to/variables-directory')

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_rpm_rquires_file(self, mock_exists, mock_mkdir, mock_overlay_order):
        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False
        self.mock_host_rpm_builder._write_dependency_file = Mock()

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_dependency_file.assert_any_called(['segment1-requires', 'segment2-requires', 'segment3-requires'], 'rpm-requires-path', collapse_duplicates=True)

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_rpm_provides_file(self, mock_exists, mock_mkdir, mock_overlay_order):
        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False
        self.mock_host_rpm_builder._write_dependency_file = Mock()

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_dependency_file.assert_any_called(['segment1-provides', 'segment2-provides', 'segment3-provides'], 'rpm-provides-path', False)

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_rpm_requires_repos_file_if_repo_packages_regex_configured(self, mock_exists, mock_mkdir, mock_overlay_order):
        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False
        self.mock_host_rpm_builder._write_dependency_file = Mock()

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_dependency_file.assert_any_called(['segment1-requires', 'segment2-requires', 'segment3-requires'], 'variables-directory/RPM_REQUIRES_REPOS', filter_regex='^yadt-.*-repos?$')

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_rpm_requires_non_repos_file_if_repo_packages_regex_configured(self, mock_exists, mock_mkdir, mock_overlay_order):
        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False
        self.mock_host_rpm_builder._write_dependency_file = Mock()

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_dependency_file.assert_any_called(['segment1-requires', 'segment2-requires', 'segment3-requires'], 'variables-directory/RPM_REQUIRES_NON_REPOS', positive_filter=False, filter_regex='^yadt-.*-repos?$')

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_export_spec_file(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._export_spec_file.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_save_log_entries_to_variable(self, mock_exists, mock_mkdir, mock_overlay_order):

        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._save_log_entries_to_variable.assert_called_with(['segment1-svn-paths', 'segment2-svn-paths', 'segment3-svn-paths'])

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_save_overlaying_to_variable(self, mock_exists, mock_mkdir, mock_overlay_order):

        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._save_overlaying_to_variable.assert_called_with({'segment1': ['segment1-exported-paths'],
                                                                                    'segment3': ['segment3-exported-paths'],
                                                                                    'segment2': ['segment2-exported-paths']})

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_move_variables_out_of_rpm_dir(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._move_variables_out_of_rpm_dir.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_save_file_list(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._save_file_list.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_save_segment_variables(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._save_segment_variables.assert_called_with(
            do_not_write_host_segment_variable=False)

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    @patch('config_rpm_maker.hostrpmbuilder.TokenReplacer')
    def test_should_save_segment_variables_without_host_when_building_group_rpm(self, token_replacer, mock_exists, mock_mkdir):
        def only_rpm_name_variable_file_exists(path):
            if path.endswith("RPM_NAME"):
                return True
            return False

        mock_exists.side_effect = only_rpm_name_variable_file_exists
        self.mock_host_rpm_builder._get_content.return_value = "any-group-rpm-name"

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._save_segment_variables.assert_called_with(
            do_not_write_host_segment_variable=True)

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    @patch('config_rpm_maker.hostrpmbuilder.open', create=True)
    def test_should_write_rpm_name_and_protection_variable_for_host_rpm(self, _, mock_exists, mock_mkdir):
        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_file.assert_any_call('/path/to/variables-directory/RPM_NAME',
                                                               'devweb01')
        self.mock_host_rpm_builder._write_file.assert_any_call('/path/to/variables-directory/INSTALL_PROTECTION_DEPENDENCY',
                                                               'hostname-@@@HOST@@@')

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    @patch('config_rpm_maker.hostrpmbuilder.TokenReplacer')
    def test_should_write_empty_protection_variable_for_group_rpm(self, token_replacer, mock_exists, mock_mkdir):
        def only_rpm_name_variable_file_exists(path):
            if path.endswith("RPM_NAME"):
                return True
            return False
        mock_exists.side_effect = only_rpm_name_variable_file_exists
        self.mock_host_rpm_builder._get_content.return_value = "any-group-rpm-name"

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_file.assert_any_call('/path/to/variables-directory/INSTALL_PROTECTION_DEPENDENCY',
                                                               '')
        for write_call in self.mock_host_rpm_builder._write_file.call_args_list:
            write_args, _write_kwargs = write_call
            if "/path/to/variables-directory/RPM_NAME" in write_args:
                self.fail("Found unwanted call %s, for a group rpm we should not overwrite the RPM_NAME variable!" % str(write_call))
        self.assertEqual(self.mock_host_rpm_builder.rpm_name, "any-group-rpm-name")

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_save_network_variables(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._save_network_variables.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_copy_files_for_config_viewer(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._copy_files_for_config_viewer.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_patch_info_into_variables_and_configviewer(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False
        self.mock_host_rpm_builder._generate_patch_info.return_value = "patchinfo1\npatchinfo2\npatchinfo3\n"

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_file.assert_any_call('/path/to/variables-directory/VARIABLES', 'patchinfo1\npatchinfo2\npatchinfo3\n')
        self.mock_host_rpm_builder._write_file.assert_any_call('config_viewer_host_dir/devweb01.variables', 'patchinfo1\npatchinfo2\npatchinfo3\n')

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_filter_tokens_in_rpm_sources(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._filter_tokens_in_rpm_sources.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_build_rpm_using_rpmbuild(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._build_rpm_using_rpmbuild.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.is_config_viewer_only_enabled')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_not_build_rpm_using_rpmbuild(self, mock_exists, mock_mkdir, mock_get):

        mock_get.return_value = True
        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        mock_get.assert_any_call()
        self.assertEqual(0, len(self.mock_host_rpm_builder._build_rpm_using_rpmbuild.call_args_list))

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_filter_tokens_in_config_viewer(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._filter_tokens_in_config_viewer.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_revision_file_for_config_viewer(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_revision_file_for_config_viewer.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_overlaying_for_config_viewer(self, mock_exists, mock_mkdir, mock_overlay_order):

        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']
        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_overlaying_for_config_viewer.assert_called_with({'segment1': ['segment1-exported-paths'],
                                                                                           'segment3': ['segment3-exported-paths'],
                                                                                           'segment2': ['segment2-exported-paths']})

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_remove_logger_handlers(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._remove_logger_handlers.assert_called_with()

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_return_rpms(self, mock_exists, mock_mkdir):
        found_rpms = ['rpm1', 'rpm2', 'rpm3']

        self.mock_host_rpm_builder._find_rpms.return_value = found_rpms
        mock_exists.return_value = False

        actual_built_rpms = HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.assertEqual(found_rpms, actual_built_rpms)

    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_clean_up_after_successful_build(self, mock_exists, mock_mkdir):

        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._clean_up.assert_called_with()


@patch('config_rpm_maker.hostrpmbuilder.is_no_clean_up_enabled')
@patch('config_rpm_maker.hostrpmbuilder.rmtree')
@patch('config_rpm_maker.hostrpmbuilder.remove')
class CleanUpTests(UnitTests):

    def setUp(self):
        mock_host_rpm_builder = Mock(HostRpmBuilder)
        mock_host_rpm_builder.host_config_dir = 'host configuration directory'
        mock_host_rpm_builder.variables_dir = 'variables directory'
        mock_host_rpm_builder.hostname = 'devweb01'
        mock_host_rpm_builder.output_file_path = '/path/to/output/file'
        mock_host_rpm_builder.error_file_path = '/path/to/error/file'

        self.mock_host_rpm_builder = mock_host_rpm_builder

    def test_should_remove_anything_if_configuration_asks_for_no_clean_up(self, mock_remove, mock_rmtree, mock_config):

        mock_config.return_value = True

        HostRpmBuilder._clean_up(self.mock_host_rpm_builder)

        self.assert_mock_never_called(mock_rmtree)
        mock_config.assert_called_with()

    def test_should_remove_variables_directory(self, moc_remove, mock_rmtree, mock_config):

        mock_config.return_value = False

        HostRpmBuilder._clean_up(self.mock_host_rpm_builder)

        mock_rmtree.assert_any_call('variables directory')

    def test_should_remove_host_configuration_directory(self, mock_remove, mock_rmtree, mock_config):

        mock_config.return_value = False

        HostRpmBuilder._clean_up(self.mock_host_rpm_builder)

        mock_rmtree.assert_any_call('host configuration directory')

    def test_should_remove_host_output_file(self, mock_remove, mock_rmtree, mock_config):

        mock_config.return_value = False

        HostRpmBuilder._clean_up(self.mock_host_rpm_builder)

        mock_remove.assert_any_call('/path/to/output/file')

    def test_should_remove_host_error_file(self, mock_remove, mock_rmtree, mock_config):

        mock_config.return_value = False

        HostRpmBuilder._clean_up(self.mock_host_rpm_builder)

        mock_remove.assert_any_call('/path/to/error/file')


class WriteRevisionFileForConfigViewerTests(TestCase):

    def setUp(self):
        mock_host_rpm_builder = Mock(HostRpmBuilder)
        mock_host_rpm_builder.config_viewer_host_dir = 'config-viewer-host-dir'
        mock_host_rpm_builder.hostname = 'hostname'
        mock_host_rpm_builder.revision = '1234'
        self.mock_host_rpm_builder = mock_host_rpm_builder

    def test_should_write_revision_file_using_host_name(self):

        HostRpmBuilder._write_revision_file_for_config_viewer(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._write_file.assert_called_with('config-viewer-host-dir/hostname.rev', '1234')


@patch('config_rpm_maker.hostrpmbuilder.is_no_clean_up_enabled')
@patch('config_rpm_maker.hostrpmbuilder.Popen')
@patch('config_rpm_maker.hostrpmbuilder.abspath')
@patch('config_rpm_maker.hostrpmbuilder.environ')
class BuildRpmUsingRpmbuildTests(UnitTests):

    def setUp(self):
        mock_host_rpm_builder = Mock(HostRpmBuilder)
        mock_host_rpm_builder.hostname = 'berweb01'
        mock_host_rpm_builder.thread_name = 'thread-0'
        mock_host_rpm_builder.logger = Mock()
        mock_host_rpm_builder.work_dir = '/path/to/working/directory'
        mock_host_rpm_builder.rpm_build_dir = '/path/to/rpm/build/directory'
        mock_host_rpm_builder._tar_sources.return_value = '/path/to/tarred_sources.tar.gz'

        mock_process = Mock()
        mock_process.communicate.return_value = ('stdout', 'stderr')
        mock_process.returncode = 0

        self.mock_host_rpm_builder = mock_host_rpm_builder
        self.mock_process = mock_process

    def test_should_tar_sources_before_building_rpm(self, mock_environ, mock_abspath, mock_popen, mock_config):

        mock_popen.return_value = self.mock_process

        HostRpmBuilder._build_rpm_using_rpmbuild(self.mock_host_rpm_builder)

        self.mock_host_rpm_builder._tar_sources.assert_called_with()

    def test_should_call_rpmbuild(self, mock_environ, mock_abspath, mock_popen, mock_config):

        mock_popen.return_value = self.mock_process

        mock_environment_copy = {}
        mock_environ.copy.return_value = mock_environment_copy

        def fake_abspath(directory):
            return '/absolute' + directory

        mock_abspath.side_effect = fake_abspath

        HostRpmBuilder._build_rpm_using_rpmbuild(self.mock_host_rpm_builder)

        mock_popen.assert_called_withPopen("rpmbuild --define --clean '_topdir /absolute/path/to/rpm/build/directory' -ta /path/to/tarred_sources.tar.gz", shell=True, env=mock_environment_copy, stderr=PIPE, stdout=PIPE)

    def test_should_not_append_clean_option_when_configration_says_no_clean_up(self, mock_environ, mock_abspath, mock_popen, mock_config):

        mock_config.return_value = True
        mock_popen.return_value = self.mock_process

        mock_environment_copy = {}
        mock_environ.copy.return_value = mock_environment_copy

        def fake_abspath(directory):
            return '/absolute' + directory

        mock_abspath.side_effect = fake_abspath

        HostRpmBuilder._build_rpm_using_rpmbuild(self.mock_host_rpm_builder)

        mock_popen.assert_called_with("rpmbuild  --define '_topdir /absolute/path/to/rpm/build/directory' -ta /path/to/tarred_sources.tar.gz", shell=True, env=mock_environment_copy, stderr=PIPE, stdout=PIPE)

    def test_should_write_stdout_to_logger(self, mock_environ, mock_abspath, mock_popen, mock_config):

        mock_logger = Mock()
        self.mock_host_rpm_builder.logger = mock_logger

        mock_popen.return_value = self.mock_process

        mock_environment_copy = {}
        mock_environ.copy.return_value = mock_environment_copy

        def fake_abspath(directory):
            return '/absolute' + directory

        mock_abspath.side_effect = fake_abspath

        HostRpmBuilder._build_rpm_using_rpmbuild(self.mock_host_rpm_builder)

        mock_logger.info.assert_called_with('stdout')

    def test_should_write_stderr_to_logger(self, mock_environ, mock_abspath, mock_popen, mock_config):

        mock_logger = Mock()
        self.mock_host_rpm_builder.logger = mock_logger

        mock_popen.return_value = self.mock_process

        mock_environment_copy = {}
        mock_environ.copy.return_value = mock_environment_copy

        def fake_abspath(directory):
            return '/absolute' + directory

        mock_abspath.side_effect = fake_abspath

        HostRpmBuilder._build_rpm_using_rpmbuild(self.mock_host_rpm_builder)

        mock_logger.error.assert_called_with('stderr')

    def test_should_not_write_stderr_to_logger_when_not_given(self, mock_environ, mock_abspath, mock_popen, mock_config):

        mock_logger = Mock()
        self.mock_host_rpm_builder.logger = mock_logger
        self.mock_process.communicate.return_value = ('stdout', "")
        mock_popen.return_value = self.mock_process

        HostRpmBuilder._build_rpm_using_rpmbuild(self.mock_host_rpm_builder)

        self.assert_mock_never_called(mock_logger.error)

    def test_should_raise_exception_when_process_returns_with_error_code(self, mock_environ, mock_abspath, mock_popen, mock_config):

        self.mock_process.returncode = 123
        mock_popen.return_value = self.mock_process

        self.assertRaises(CouldNotBuildRpmException, HostRpmBuilder._build_rpm_using_rpmbuild, self.mock_host_rpm_builder)
