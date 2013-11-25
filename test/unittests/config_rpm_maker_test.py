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

from config_rpm_maker import build_configuration_rpms_from
from config_rpm_maker.exceptions import BaseConfigRpmMakerException


class BuildConfigurationRpmsTests(TestCase):

    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_return_with_success_message_and_return_code_zero_when_everything_works_as_expected(self, mock_config_rpm_maker_class, mock_svn_service_class, mock_exit_program, mock_config):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service_class.return_value = Mock()
        mock_config_rpm_maker_class.return_value = Mock()

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1)

        mock_exit_program.assert_called_with("Success.", return_code=0)

    @patch('config_rpm_maker.LOGGER')
    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_return_with_error_message_and_error_code_when_exception_occurrs(self, mock_config_rpm_maker_class, mock_svn_service_class, mock_exit_program, mock_config, mock_logger):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service_class.side_effect = BaseConfigRpmMakerException("We knew this could happen!")

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1)

        mock_exit_program.assert_called_with('An exception occurred!', return_code=4)

    @patch('config_rpm_maker.traceback')
    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_print_traceback_when_completly_unexpected_exception_occurrs(self, mock_config_rpm_maker_class, mock_svn_service_class, mock_exit_program, mock_config, mock_traceback):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service_class.side_effect = Exception("WTF!")

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1)

        mock_traceback.print_exc.assert_called_with(5)

    @patch('config_rpm_maker.traceback')
    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_return_with_error_message_and_error_code_when_completly_unexpected_exception_occurrs(self, mock_config_rpm_maker_class, mock_svn_service_class, mock_exit_program, mock_config, mock_traceback):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service_class.side_effect = Exception("WTF!")

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1)

        mock_exit_program.assert_called_with('An unknown exception occurred!', return_code=5)

    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_initialize_svn_service_with_given_repository_url(self, mock_config_rpm_maker_class, mock_svn_service_constructor, mock_exit_program, mock_config):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service_constructor.return_value = Mock()
        mock_config_rpm_maker_class.return_value = Mock()

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1)

        mock_svn_service_constructor.assert_called_with(path_to_config='/path-to-configuration',
                                                        base_url='file:///path_to/testdata/repository')

    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_initialize_svn_service_with_path_to_config_from_configuration(self, mock_config_rpm_maker_class, mock_svn_service_constructor, mock_exit_program, mock_config):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service_constructor.return_value = Mock()
        mock_config_rpm_maker_class.return_value = Mock()

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1)

        mock_svn_service_constructor.assert_called_with(path_to_config='/path-to-configuration',
                                                        base_url='file:///path_to/testdata/repository')

    @patch('config_rpm_maker.config')
    @patch('config_rpm_maker.exit_program')
    @patch('config_rpm_maker.SvnService')
    @patch('config_rpm_maker.ConfigRpmMaker')
    def test_should_initialize_config_rpm_maker_with_given_revision_and_svn_service(self, mock_config_rpm_maker_class, mock_svn_service_constructor, mock_exit_program, mock_config):

        mock_config.get.return_value = '/path-to-configuration'
        mock_svn_service = Mock()
        mock_svn_service_constructor.return_value = mock_svn_service
        mock_config_rpm_maker_class.return_value = Mock()

        build_configuration_rpms_from('file:///path_to/testdata/repository', 1980)

        mock_config_rpm_maker_class.assert_called_with(svn_service=mock_svn_service, revision=1980)
