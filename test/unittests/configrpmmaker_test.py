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

from mock import Mock, call, patch

from unittest_support import UnitTests
from config_rpm_maker.configrpmmaker import ConfigRpmMaker


class MoveConfigviewerDirsToFinalDestinationTest(UnitTests):

    def setUp(self):
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker.revision = '54'
        self.mock_config_rpm_maker = mock_config_rpm_maker

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    def test_should_not_do_anything_if_no_hosts_are_given(self, mock_move, mock_rmtree):

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, [])

        self.assert_mock_never_called(mock_move)
        self.assert_mock_never_called(mock_rmtree)

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_move_directory_to_destination(self, mock_exists, mock_move, mock_rmtree):

        mock_exists.return_value = False

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01'])

        mock_move.assert_called_with('target/tmp/configviewer/hosts/devweb01.new-revision-54', 'target/tmp/configviewer/hosts/devweb01')

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_not_remove_directory_if_it_does_not_already_exist(self, mock_exists, mock_move, mock_rmtree):

        mock_exists.return_value = False

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01'])

        self.assert_mock_never_called(mock_rmtree)

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    @patch('config_rpm_maker.configrpmmaker.build_config_viewer_host_directory')
    def test_should_remove_directory_if_it_does_already_exist(self, mock_build_config_viewer_host_directory, mock_exists, mock_move, mock_rmtree):

        mock_build_config_viewer_host_directory.return_value = 'target/tmp/configviewer/hosts/devweb01'
        self.mock_config_rpm_maker._read_integer_from_file.return_value = 53

        mock_exists.return_value = True

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01'])

        mock_rmtree.assert_called_with('target/tmp/configviewer/hosts/devweb01')

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_not_remove_directory_if_the_revision_of_the_file_in_the_directory_is_higher(self, mock_exists, mock_move, mock_rmtree):

        self.mock_config_rpm_maker._read_integer_from_file.return_value = 99

        mock_exists.return_value = True

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01'])

        self.assertTrue(call('target/tmp/configviewer/hosts/devweb01') not in mock_rmtree.call_args_list)

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_remove_temporary_directory_if_the_revision_of_the_file_in_the_directory_is_higher(self, mock_exists, mock_move, mock_rmtree):

        self.mock_config_rpm_maker._read_integer_from_file.return_value = 99

        mock_exists.return_value = True

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01'])

        mock_rmtree.assert_called_with('target/tmp/configviewer/hosts/devweb01.new-revision-54')

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_move_directories_of_hosts_to_destination(self, mock_exists, mock_move, mock_rmtree):

        mock_exists.return_value = False

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01', 'tuvweb01'])

        mock_move.assert_any_call('target/tmp/configviewer/hosts/devweb01.new-revision-54', 'target/tmp/configviewer/hosts/devweb01')
        mock_move.assert_any_call('target/tmp/configviewer/hosts/tuvweb01.new-revision-54', 'target/tmp/configviewer/hosts/tuvweb01')

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_remove_directories_of_hosts_if_they_already_exist(self, mock_exists, mock_move, mock_rmtree):

        mock_exists.return_value = True
        self.mock_config_rpm_maker._read_integer_from_file.return_value = 42

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01', 'tuvweb01'])

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/devweb01')
        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/tuvweb01')

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_remove_directories_of_hosts_if_they_already_exist_and_should_override_those_with_a_lower_revision(self, mock_exists, mock_move, mock_rmtree):

        def read_integer_from_file_side_effect(path):
            if path.endswith('devweb01.rev'):
                return 42
            elif path.endswith('tuvweb01.rev'):
                raise Exception('This should not happen since the exists side effect returns False')
            elif path.endswith('berweb01.rev'):
                return 42
            else:
                raise Exception('Unknown path "%s"' % path)

        self.mock_config_rpm_maker._read_integer_from_file.side_effect = read_integer_from_file_side_effect

        def exists_side_effect(path):
            if path.endswith('devweb01'):
                return True
            elif path.endswith('tuvweb01'):
                return False
            elif path.endswith('berweb01'):
                return True
            else:
                raise Exception("Unknown path %s" % path)

        mock_exists.side_effect = exists_side_effect

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01', 'tuvweb01', 'berweb01'])

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/devweb01')
        mock_move.assert_any_call('target/tmp/configviewer/hosts/devweb01.new-revision-54', 'target/tmp/configviewer/hosts/devweb01')

        self.assertTrue(call('target/tmp/configviewer/hosts/tuvweb01') not in mock_rmtree.call_args_list)
        mock_move.assert_any_call('target/tmp/configviewer/hosts/tuvweb01.new-revision-54', 'target/tmp/configviewer/hosts/tuvweb01')

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/berweb01')
        mock_move.assert_any_call('target/tmp/configviewer/hosts/berweb01.new-revision-54', 'target/tmp/configviewer/hosts/berweb01')

    @patch('config_rpm_maker.configrpmmaker.rmtree')
    @patch('config_rpm_maker.configrpmmaker.move')
    @patch('config_rpm_maker.configrpmmaker.exists')
    def test_should_remove_directories_of_hosts_if_they_already_exist_and_should_leave_them_if_they_have_a_higher_revision(self, mock_exists, mock_move, mock_rmtree):

        def read_integer_from_file_side_effect(path):
            if path.endswith('devweb01.rev'):
                return 99
            elif path.endswith('tuvweb01.rev'):
                raise Exception('This should not happen since the exists side effect returns False')
            elif path.endswith('berweb01.rev'):
                return 42
            else:
                raise Exception("Unknown path %s" % path)

        self.mock_config_rpm_maker._read_integer_from_file.side_effect = read_integer_from_file_side_effect

        def exists_side_effect(path):
            if path.endswith('devweb01'):
                return True
            elif path.endswith('tuvweb01'):
                return False
            elif path.endswith('berweb01'):
                return True
            else:
                raise Exception("Unknown path %s" % path)

        mock_exists.side_effect = exists_side_effect

        ConfigRpmMaker._move_configviewer_dirs_to_final_destination(self.mock_config_rpm_maker, ['devweb01', 'tuvweb01', 'berweb01'])

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/devweb01.new-revision-54')
        self.assertTrue(call('target/tmp/configviewer/hosts/devweb01.new-revision-54', 'target/tmp/configviewer/hosts/devweb01') not in mock_move.call_args_list)

        self.assertTrue(call('target/tmp/configviewer/hosts/tuvweb01') not in mock_rmtree.call_args_list)
        mock_move.assert_any_call('target/tmp/configviewer/hosts/tuvweb01.new-revision-54', 'target/tmp/configviewer/hosts/tuvweb01')

        mock_rmtree.assert_any_call('target/tmp/configviewer/hosts/berweb01')
        mock_move.assert_any_call('target/tmp/configviewer/hosts/berweb01.new-revision-54', 'target/tmp/configviewer/hosts/berweb01')


@patch('config_rpm_maker.configrpmmaker.exists')
@patch('config_rpm_maker.configrpmmaker.mkdtemp')
@patch('config_rpm_maker.configrpmmaker.makedirs')
class PrepareWorkDirTests(UnitTests):

    def test_should_create_working_directory_in_configured_temporary_directory(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_mkdtemp.assert_called_with(prefix='yadt-config-rpm-maker.', suffix='.4852', dir='temporary directory')

    def test_should_not_create_any_directory_when_all_directories_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = True

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        self.assert_mock_never_called(mock_makedirs)

    def test_should_create_tmp_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/tmp')

    def test_should_create_RPMS_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/RPMS')

    def test_should_create_RPMS_x86_64_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/RPMS/x86_64')

    def test_should_create_RPMS_noarch_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/RPMS/noarch')

    def test_should_create_BUILD_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/BUILD')

    def test_should_create_BUILDROOT_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/BUILDROOT')

    def test_should_create_SRPMS_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/SRPMS')

    def test_should_create_SPECS_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/SPECS')

    def test_should_create_SOURCES_directory_when_it_does_not_exist(self, mock_makedirs, mock_mkdtemp, mock_exists):

        mock_config_rpm_maker = self.create_mock_config_rpm_maker()
        mock_exists.return_value = False
        mock_mkdtemp.return_value = 'working-directory'

        ConfigRpmMaker._prepare_work_dir(mock_config_rpm_maker)

        mock_makedirs.assert_any_call('working-directory/rpmbuild/SOURCES')

    def create_mock_config_rpm_maker(self):
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker.temp_dir = 'temporary directory'
        mock_config_rpm_maker.revision = '4852'
        return mock_config_rpm_maker


@patch('config_rpm_maker.configrpmmaker.remove')
@patch('config_rpm_maker.configrpmmaker.rmtree')
@patch('config_rpm_maker.configrpmmaker.exists')
class CleanUpWorkingDirectoryTests(UnitTests):

    def test_should_not_remove_anything_when_configuration_says_we_should_not_clean_up(self, mock_exists, mock_rmtree, mock_remove):

        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker._keep_work_dir.return_value = True
        mock_config_rpm_maker.work_dir = '/path/to/working/directory'

        ConfigRpmMaker._clean_up_work_dir(mock_config_rpm_maker)

        self.assert_mock_never_called(mock_exists)
        self.assert_mock_never_called(mock_rmtree)
        self.assert_mock_never_called(mock_remove)

    def test_should_not_try_to_remove_working_directory_if_it_is_not_set(self, mock_exists, mock_rmtree, mock_remove):

        mock_exists.return_value = False
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker._keep_work_dir.return_value = False
        mock_config_rpm_maker.work_dir = None
        mock_config_rpm_maker.error_log_file = None

        ConfigRpmMaker._clean_up_work_dir(mock_config_rpm_maker)

        self.assert_mock_never_called(mock_rmtree)
        self.assert_mock_never_called(mock_remove)

    def test_should_not_remove_working_directory_if_it_does_not_exist(self, mock_exists, mock_rmtree, mock_remove):

        mock_exists.return_value = False
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker._keep_work_dir.return_value = False
        mock_config_rpm_maker.work_dir = '/path/to/working/directory'
        mock_config_rpm_maker.error_log_file = None

        ConfigRpmMaker._clean_up_work_dir(mock_config_rpm_maker)

        self.assert_mock_never_called(mock_rmtree)
        self.assert_mock_never_called(mock_remove)
        mock_exists.assert_any_call('/path/to/working/directory')

    def test_should_remove_working_directory_if_it_exists(self, mock_exists, mock_rmtree, mock_remove):

        mock_exists.return_value = True
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker._keep_work_dir.return_value = False
        mock_config_rpm_maker.work_dir = '/path/to/working/directory'
        mock_config_rpm_maker.error_log_file = None

        ConfigRpmMaker._clean_up_work_dir(mock_config_rpm_maker)

        mock_exists.assert_any_call('/path/to/working/directory')
        mock_rmtree.assert_called_with('/path/to/working/directory')

    def test_should_not_remove_error_log_if_it_does_not_exist(self, mock_exists, mock_rmtree, mock_remove):

        mock_exists.return_value = False
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker._keep_work_dir.return_value = False
        mock_config_rpm_maker.work_dir = '/path/to/working/directory'
        mock_config_rpm_maker.error_log_file = '/path/to/error.log'

        ConfigRpmMaker._clean_up_work_dir(mock_config_rpm_maker)

        self.assert_mock_never_called(mock_remove)

    def test_should_remove_error_log_if_it_exists(self, mock_exists, mock_rmtree, mock_remove):

        mock_exists.return_value = True
        mock_config_rpm_maker = Mock(ConfigRpmMaker)
        mock_config_rpm_maker._keep_work_dir.return_value = False
        mock_config_rpm_maker.work_dir = '/path/to/working/directory'
        mock_config_rpm_maker.error_log_file = '/path/to/error.log'

        ConfigRpmMaker._clean_up_work_dir(mock_config_rpm_maker)

        mock_exists.assert_any_call('/path/to/error.log')
        mock_remove.assert_called_with('/path/to/error.log')
