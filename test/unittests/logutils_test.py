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

from logging import ERROR, Logger
from mock import Mock, call, patch
from unittest import TestCase

from config_rpm_maker.config import DEFAULT_LOG_LEVEL, DEFAULT_SYS_LOG_LEVEL
from config_rpm_maker.logutils import (MutedLogger,
                                       create_console_handler,
                                       create_sys_log_handler,
                                       log_configuration,
                                       log_elements_of_list,
                                       log_process_id,
                                       verbose)


@patch('config_rpm_maker.logutils.StreamHandler')
@patch('config_rpm_maker.logutils.Formatter')
class CreateConsoleHandlerTests(TestCase):

    def test_should_initialze_formatter_and_use_it(self, mock_formatter_class, mock_stream_handler_class):

        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_handler = Mock()
        mock_stream_handler_class.return_value = mock_handler

        create_console_handler()

        mock_formatter_class.assert_called_with('[%(levelname)5s] %(message)s')
        mock_handler.setFormatter.assert_called_with(mock_formatter)

    def test_should_set_default_log_level_if_no_log_level_given(self, mock_formatter_class, mock_stream_handler_class):

        mock_handler = Mock()
        mock_stream_handler_class.return_value = mock_handler

        create_console_handler()

        mock_handler.setLevel.assert_called_with(DEFAULT_LOG_LEVEL)

    def test_should_set_given_log_level(self, mock_formatter_class, mock_stream_handler_class):

        mock_handler = Mock()
        mock_stream_handler_class.return_value = mock_handler

        create_console_handler(log_level=ERROR)

        mock_handler.setLevel.assert_called_with(ERROR)

    def test_should_return_created_console_handler(self, mock_formatter_class, mock_stream_handler_class):

        mock_handler = Mock()
        mock_stream_handler_class.return_value = mock_handler

        actual_handler = create_console_handler()

        self.assertEqual(mock_handler, actual_handler)


@patch('config_rpm_maker.logutils.SysLogHandler')
@patch('config_rpm_maker.logutils.Formatter')
class CreateSysLogHandlerTests(TestCase):

    def test_should_initialze_formatter_using_the_revision_number_in_the_format(self, mock_formatter_class, mock_sys_log_handler_class):

        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        mock_handler = Mock()
        mock_sys_log_handler_class.return_value = mock_handler

        create_sys_log_handler(123)

        mock_formatter_class.assert_called_with('config_rpm_maker[123]: [%(levelname)5s] %(message)s')
        mock_handler.setFormatter.assert_called_with(mock_formatter)

    def test_should_set_default_log_level_if_no_log_level_given(self, mock_formatter_class, mock_sys_log_handler_class):

        mock_handler = Mock()
        mock_sys_log_handler_class.return_value = mock_handler

        create_sys_log_handler(123)

        mock_handler.setLevel.assert_called_with(DEFAULT_SYS_LOG_LEVEL)

    def test_should_return_created_console_handler(self, mock_formatter_class, mock_sys_log_handler_class):

        mock_handler = Mock()
        mock_sys_log_handler_class.return_value = mock_handler

        actual_handler = create_sys_log_handler(123)

        self.assertEqual(mock_handler, actual_handler)


class LogConfigurationTests(TestCase):

    def setUp(self):
        self.mock_log = Mock()

    def test_should_log_given_path(self):

        log_configuration(self.mock_log, {}, 'configuration_file.yaml')

        self.mock_log.assert_any_call('Loaded configuration file "%s"', 'configuration_file.yaml')

    def test_should_log_when_configuration_file_was_empty(self):

        log_configuration(self.mock_log, {}, 'configuration_file.yaml')

        self.mock_log.assert_any_call('Configuration file was empty!')

    def test_should_log_given_string_configuration_property(self):

        log_configuration(self.mock_log, {'property': '123'}, 'configuration_file.yaml')

        self.mock_log.assert_any_call('Configuraton property %s = "%s" (%s)', '"property"', '123', 'str')

    def test_should_log_given_boolean_configuration_property(self):

        log_configuration(self.mock_log, {'property': True}, 'configuration_file.yaml')

        self.mock_log.assert_any_call('Configuraton property %s = "%s" (%s)', '"property"', True, 'bool')

    def test_should_log_given_integer_configuration_property(self):

        log_configuration(self.mock_log, {'property': 123}, 'configuration_file.yaml')

        self.mock_log.assert_any_call('Configuraton property %s = "%s" (%s)', '"property"', 123, 'int')

    def test_should_log_given_configuration_properties_in_alphabetical_order(self):

        configuration = {'a_property': 123,
                         'b_property': False,
                         'c_property': 'hello world'}

        log_configuration(self.mock_log, configuration, 'configuration_file.yaml')

        self.assertEqual([call('Loaded configuration file "%s"', 'configuration_file.yaml'),
                          call('Configuraton property %s = "%s" (%s)', '"a_property"', 123, 'int'),
                          call('Configuraton property %s = "%s" (%s)', '"b_property"', False, 'bool'),
                          call('Configuraton property %s = "%s" (%s)', '"c_property"', 'hello world', 'str')],
                         self.mock_log.call_args_list)


class LogElementsOfListTests(TestCase):

    def setUp(self):
        self.mock_log = Mock()

    def test_should_only_log_summary_when_list_has_no_elements(self):

        log_elements_of_list(self.mock_log, 'Created %s elements.', [])

        self.mock_log.assert_called_with('Created %s elements.', 0)

    def test_should_log_one_element_if_a_list_with_one_element_is_given(self):

        log_elements_of_list(self.mock_log, 'Created %s elements.', ['element'])

        self.mock_log.assert_any_call('Created %s elements. Listing in sorted order:', 1)
        self.mock_log.assert_any_call('    #%s: %s', 0, 'element')

    def test_should_log_two_elements_if_a_list_with_two_elements_is_given(self):

        log_elements_of_list(self.mock_log, 'Created %s elements.', ['element0', 'element1'])

        self.mock_log.assert_any_call('Created %s elements. Listing in sorted order:', 2)
        self.mock_log.assert_any_call('    #%s: %s', 0, 'element0')
        self.mock_log.assert_any_call('    #%s: %s', 1, 'element1')

    def test_should_log_elements_in_sorted_order(self):

        log_elements_of_list(self.mock_log, 'Created %s elements.', ['element0', 'element1', 'element2'])

        self.assertEqual([call('Created %s elements. Listing in sorted order:', 3),
                          call('    #%s: %s', 0, 'element0'),
                          call('    #%s: %s', 1, 'element1'),
                          call('    #%s: %s', 2, 'element2')],
                         self.mock_log.call_args_list)


@patch('config_rpm_maker.logutils.getpid')
class LogProcessId(TestCase):

    def test_should_log_process_id(self, mock_getpid):

        mock_logging_function = Mock()
        mock_getpid.return_value = 1234

        log_process_id(mock_logging_function)

        mock_logging_function.assert_called_with('Process ID is %s', 1234)


class MutedLoggerTests(TestCase):

    def test_should_pass_when_calling_info_with_a_simple_string(self):

        muted_logger = MutedLogger()

        muted_logger.info("Hello world.")

    def test_should_pass_when_calling_info_with_a_pattern_and_some_arguments(self):

        muted_logger = MutedLogger()

        muted_logger.info("Hello world.", 12, "abc")

    def test_should_pass_when_calling_error_with_a_simple_string(self):

        muted_logger = MutedLogger()

        muted_logger.error("Why did you do this?")

    def test_should_pass_when_calling_error_with_a_pattern_and_some_arguments(self):

        muted_logger = MutedLogger()

        muted_logger.error("You did it %d times and I think %s.", 12, "abc")

    def test_should_pass_when_calling_warn_with_a_simple_string(self):

        muted_logger = MutedLogger()

        muted_logger.warn("Hello I am warning you.")

    def test_should_pass_when_calling_warn_with_a_pattern_and_some_arguments(self):

        muted_logger = MutedLogger()

        muted_logger.warn("Warning you about %s and %d", "abc", 12)

    def test_should_pass_when_calling_debug_with_a_simple_string(self):

        muted_logger = MutedLogger()

        muted_logger.debug("Hello I am debugging you.")

    def test_should_pass_when_calling_debug_with_a_pattern_and_some_arguments(self):

        muted_logger = MutedLogger()

        muted_logger.debug("Debugging %d and %s.", 12, "abc")


class VerboseTests(TestCase):

    @patch('config_rpm_maker.logutils.get')
    def test_should_return_given_logger_when_configuration_value_for_verbose_is_true(self, mock_get):

        mock_logger = Mock(Logger)
        mock_get.return_value = True

        verbose(mock_logger).info("Hello")

        mock_logger.info.assert_called_with("Hello")
        mock_get.assert_called_with('verbose')

    @patch('config_rpm_maker.logutils._muted_logger')
    @patch('config_rpm_maker.logutils.get')
    def test_should_not_return_muted_logger_when_configuration_value_for_verbose_is_false(self, mock_get, mock_muted_logger):

        mock_logger = Mock(Logger)
        mock_get.return_value = False

        verbose(mock_logger).info("Hello")

        mock_muted_logger.info.assert_called_with("Hello")
        mock_get.assert_called_with('verbose')
