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


import config_rpm_maker

from config_rpm_maker.config import DEFAULT_CONFIG_VIEWER_ONLY, KEY_CONFIG_VIEWER_ONLY
from config_rpm_maker.hostrpmbuilder import ConfigDirAlreadyExistsException, CouldNotCreateConfigDirException, HostRpmBuilder


class BuildTests(TestCase):

    def _create_mock_overlay_segment_method(self):
        def fake_overlay_segment(segment):
            return ['%s-svn-paths' % segment], ['%s-exported-paths' % segment], ['%s-requires' % segment], [
                '%s-provides' % segment]

        mock_overlay_segment = Mock()
        mock_overlay_segment.side_effect = fake_overlay_segment
        return mock_overlay_segment

    def setUp(self):
        self.VARIABLES_DIRECTORY = 'variables-directory'
        self.RPM_REQUIRES_PATH = 'rpm-requires-path'

        mock_host_rpm_builder = Mock(HostRpmBuilder)
        mock_host_rpm_builder.thread_name = 'Mock-Thread'
        mock_host_rpm_builder.hostname = 'devweb01'
        mock_host_rpm_builder.logger = Mock()
        mock_host_rpm_builder.revision = '123'
        mock_host_rpm_builder.host_config_dir = '/foo/bar'
        mock_host_rpm_builder.variables_dir = self.VARIABLES_DIRECTORY
        mock_host_rpm_builder.rpm_requires_path = self.RPM_REQUIRES_PATH
        mock_host_rpm_builder.rpm_provides_path = 'rpm-provides-path'
        mock_host_rpm_builder.config_viewer_host_dir = 'config_viewer_host_dir'

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

        mock_mkdir.assert_any_call('variables-directory')

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

    @patch('config_rpm_maker.hostrpmbuilder.config.get')
    @patch('config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_write_not_write_rpm_requires_with_repo_stuff_if_no_repo_packages_regex_configured(self, mock_exists, mock_mkdir, mock_overlay_order, mock_get):

        config_rpm_maker.hostrpmbuilder.OVERLAY_ORDER = ['segment1', 'segment2', 'segment3']

        mock_get.return_value = False
        mock_exists.return_value = False
        self.mock_host_rpm_builder._write_dependency_file = Mock()

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        self.assertEqual(2, self.mock_host_rpm_builder._write_dependency_file.call_count)
        self.mock_host_rpm_builder._write_dependency_file.assert_any_called(['segment1-requires', 'segment2-requires', 'segment3-requires'], 'rpm-requires-path', collapse_duplicates=True)
        self.mock_host_rpm_builder._write_dependency_file.assert_any_called(['segment1-requires', 'segment2-requires', 'segment3-requires'], 'variables-directory/RPM_REQUIRES_REPOS', filter_regex='^yadt-.*-repos?$')

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

        self.mock_host_rpm_builder._save_segment_variables.assert_called_with()

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

        self.mock_host_rpm_builder._write_file.assert_any_call('variables-directory/VARIABLES', 'patchinfo1\npatchinfo2\npatchinfo3\n')
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

    @patch('config_rpm_maker.hostrpmbuilder.config.get')
    @patch('config_rpm_maker.hostrpmbuilder.mkdir')
    @patch('config_rpm_maker.hostrpmbuilder.exists')
    def test_should_not_build_rpm_using_rpmbuild(self, mock_exists, mock_mkdir, mock_get):

        mock_get.return_value = True
        mock_exists.return_value = False

        HostRpmBuilder.build(self.mock_host_rpm_builder)

        mock_get.assert_any_call(KEY_CONFIG_VIEWER_ONLY, DEFAULT_CONFIG_VIEWER_ONLY)
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
