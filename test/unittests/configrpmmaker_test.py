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

        self.assert_mock_not_called(mock_move)
        self.assert_mock_not_called(mock_rmtree)

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

        self.assert_mock_not_called(mock_rmtree)

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
