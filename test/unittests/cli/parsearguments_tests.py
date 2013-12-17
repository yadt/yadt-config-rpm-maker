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

from logging import DEBUG, INFO
from mock import patch, Mock
from unittest import TestCase

from config_rpm_maker.configuration import is_config_viewer_only_enabled, get_rpm_upload_command, is_verbose_enabled, is_no_clean_up_enabled
from config_rpm_maker.cli.parsearguments import USAGE_INFORMATION, OPTION_CONFIG_VIEWER_ONLY, OPTION_RPM_UPLOAD_CMD, OPTION_VERBOSE, OPTION_NO_CLEAN_UP
from config_rpm_maker.cli.parsearguments import apply_arguments_to_config, parse_arguments, determine_console_log_level


class ParseArgumentsTests(TestCase):

    @patch('config_rpm_maker.cli.parsearguments.OptionParser')
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

    @patch('config_rpm_maker.cli.parsearguments.exit')
    @patch('config_rpm_maker.cli.parsearguments.OptionParser')
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

    @patch('config_rpm_maker.cli.parsearguments.exit')
    @patch('config_rpm_maker.cli.parsearguments.stdout')
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

    def test_should_return_verbose_option_as_false_when_no_option_given(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertFalse(actual_arguments["--verbose"])

    def test_should_return_verbose_option_as_true_when_debug_option_given(self):

        actual_arguments = parse_arguments(["foo", "123", "--verbose"], version="")

        self.assertTrue(actual_arguments["--verbose"])

    def test_should_return_no_clean_up_option_as_true_when_no_clean_up_option_given(self):

        actual_arguments = parse_arguments(["foo", "123", "--no-clean-up"], version="")

        self.assertTrue(actual_arguments["--no-clean-up"])

    def test_should_return_no_syslog_option_as_true_when_no_syslog_option_given(self):

        actual_arguments = parse_arguments(["foo", "123", "--no-syslog"], version="")

        self.assertTrue(actual_arguments["--no-syslog"])

    def test_should_return_option_config_viewer_only_as_false_when_no_option_given(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertFalse(actual_arguments["--config-viewer-only"])

    def test_should_return_option_config_viewer_only_as_true_when_option_is_given(self):

        actual_arguments = parse_arguments(["foo", "123", "--config-viewer-only"], version="")

        self.assertTrue(actual_arguments["--config-viewer-only"])

    def test_should_return_first_argument_as_repository(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertEqual(actual_arguments["<repository-url>"], "foo")

    def test_should_return_second_argument_as_revision(self):

        actual_arguments = parse_arguments(["foo", "123"], version="")

        self.assertEqual(actual_arguments["<revision>"], "123")


@patch('config_rpm_maker.cli.parsearguments.set_property')
class ApplyArgumentsToConfiguration(TestCase):

    def setUp(self):
        self.arguments = {OPTION_RPM_UPLOAD_CMD: False,
                          OPTION_CONFIG_VIEWER_ONLY: False,
                          OPTION_NO_CLEAN_UP: False,
                          OPTION_VERBOSE: False}

    def test_should_not_apply_anything_if_no_options_given(self, mock_set_property):

        apply_arguments_to_config(self.arguments)

        self.assertEqual(0, len(mock_set_property.call_args_list))

    def test_should_set_rpm_upload_command_when_option_is_given(self, mock_set_property):

        self.arguments[OPTION_RPM_UPLOAD_CMD] = '/bin/true'

        apply_arguments_to_config(self.arguments)

        mock_set_property.assert_any_call(get_rpm_upload_command, '/bin/true')

    def test_should_set_config_viewer_only_when_option_is_given(self, mock_set_property):

        self.arguments[OPTION_CONFIG_VIEWER_ONLY] = True

        apply_arguments_to_config(self.arguments)

        mock_set_property.assert_any_call(is_config_viewer_only_enabled, True)

    def test_should_set_verbose_when_option_is_given(self, mock_set_property):

        self.arguments[OPTION_VERBOSE] = True

        apply_arguments_to_config(self.arguments)

        mock_set_property.assert_any_call(is_verbose_enabled, True)

    def test_should_set_no_clean_up_when_option_is_given(self, mock_set_property):

        self.arguments[OPTION_NO_CLEAN_UP] = True

        apply_arguments_to_config(self.arguments)

        mock_set_property.assert_any_call(is_no_clean_up_enabled, True)


class DetermineConsoleLogLevelTests(TestCase):

    def test_should_return_debug_when_debug_option_is_given(self):

        fake_arguments = {'--debug': True}

        actual = determine_console_log_level(fake_arguments)

        self.assertEqual(DEBUG, actual)

    def test_should_return_info_when_no_debug_option_is_given(self):

        fake_arguments = {'--debug': False}

        actual = determine_console_log_level(fake_arguments)

        self.assertEqual(INFO, actual)
