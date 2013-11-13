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
from mock import call, patch

from config_rpm_maker import exit_program


class ConfigRpmMakerTest(TestCase):

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
