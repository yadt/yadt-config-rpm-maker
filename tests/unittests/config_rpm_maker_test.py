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

from mock import Mock, call, patch
from unittest import TestCase, main

from config_rpm_maker import (USAGE_INFORMATION,
                              build_configuration_rpms_from,
                              exit_program,
                              parse_arguments,
                              validate_revision_argument)
from config_rpm_maker.exceptions import BaseConfigRpmMakerException


class ParseArgumentsTests(TestCase):

    @patch('config_rpm_maker.OptionParser')
    def test_should_use_usage_information(self, mock_option_parser_class):

        mock_option_parser = Mock()
        mock_values = Mock()
        mock_values.version = False
        mock_values.debug = False
        mock_arguments = ["foo", "bar"]
        mock_option_parser.parse_args.return_value = (mock_values, mock_arguments)
        mock_option_parser_class.return_value = mock_option_parser

        parse_arguments([], version="")

        mock_option_parser_class.assert_called_with(usage=USAGE_INFORMATION)

    @patch('config_rpm_maker.exit')
    @patch('config_rpm_maker.OptionParser')
    def test_should_print_help_screen_and_exit_when_less_than_two_positional_arguments_are_given(self, mock_option_parser_class, mock_exit):

        mock_option_parser = Mock()
        mock_values = Mock()
        mock_values.version = False
        mock_values.debug = False
        mock_arguments = [""]
        mock_option_parser.parse_args.return_value = (mock_values, mock_arguments)
        mock_option_parser_class.return_value = mock_option_parser

        parse_arguments([], version="")

        mock_option_parser.print_help.assert_called_with()
        mock_exit.assert_called_with(1)

    @patch('config_rpm_maker.exit')
    @patch('config_rpm_maker.stdout')
    def test_should_print_version_and_exit_with_return_code_zero_when_version_option_given(self, mock_stdout, mock_exit):

        parse_arguments(["--version"], version="yadt-config-rpm-maker 2.0")

        mock_stdout.write.assert_called_with("yadt-config-rpm-maker 2.0\n")
        mock_exit.assert_called_with(0)

    def test_should_return_debug_option_as_false_when_no_option_given(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertFalse(actual_arguments["--debug"])

    def test_should_return_debug_option_as_true_when_debug_option_given(self):

        actual_arguments = parse_arguments(["foo", "123", "--debug"], version="")

        self.assertTrue(actual_arguments["--debug"])

    def test_should_return_first_argument_as_repository(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertEqual(actual_arguments["<repository>"], "foo")

    def test_should_return_second_argument_as_revision(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertEqual(actual_arguments["<revision>"], "123")


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


class ArgumentValidationTests(TestCase):

    @patch('config_rpm_maker.exit_program')
    def test_should_exit_if_a_non_integer_string_is_given(self, mock_exit_program):

        validate_revision_argument('abc')

        mock_exit_program.assert_called_with('Given revision "abc" is not an integer.', return_code=2)

    @patch('config_rpm_maker.exit_program')
    def test_should_not_exit_if_a_integer_string_is_given(self, mock_exit_program):

        validate_revision_argument('123')

        self.assertEqual(None, mock_exit_program.call_args)


class ExitProgramTests(TestCase):

    @patch('config_rpm_maker.LOGGER')
    @patch('config_rpm_maker.exit')
    def test_should_exit_with_given_return_code(self, mock_exit, mock_logger):

        exit_program('Some message.', 123)

        mock_exit.assert_called_once_with(123)

    @patch('config_rpm_maker.exit')
    @patch('config_rpm_maker.LOGGER')
    def test_should_log_message_as_info_if_return_code_is_zero(self, mock_logger, mock_exit):

        exit_program('Success.', 0)

        mock_logger.info.assert_called_with('Success.')
        self.assertEqual(0, mock_logger.error.call_count)

    @patch('config_rpm_maker.exit')
    @patch('config_rpm_maker.LOGGER')
    def test_should_log_message_as_error_if_return_code_is_not_zero(self, mock_logger, mock_exit):

        exit_program('Failed.', 1)

        mock_logger.error.assert_called_with('Failed.')

    @patch('config_rpm_maker.time')
    @patch('config_rpm_maker.exit')
    @patch('config_rpm_maker.LOGGER')
    def test_should_log_elapsed_time(self, mock_logger, mock_exit, mock_time):

        mock_time.return_value = 1

        exit_program('Success.', 0)

        self.assertEqual(call('Elapsed time: 1.0s'), mock_logger.info.call_args_list[0])

    @patch('config_rpm_maker.time')
    @patch('config_rpm_maker.exit')
    @patch('config_rpm_maker.LOGGER')
    def test_should_round_elapsed_time_down_to_two_decimals_after_dot(self, mock_logger, mock_exit, mock_time):

        mock_time.return_value = 0.555555555555

        exit_program('Success.', 0)

        self.assertEqual(call('Elapsed time: 0.56s'), mock_logger.info.call_args_list[0])

if __name__ == "__main__":
    main()
