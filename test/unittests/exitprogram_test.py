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
from mock import patch

from config_rpm_maker.exitprogram import exit_program, get_timestamp_from_start


class ExitProgramTests(TestCase):

    @patch('config_rpm_maker.exitprogram.LOGGER')
    @patch('config_rpm_maker.exitprogram.exit')
    def test_should_exit_with_given_return_code(self, mock_exit, mock_logger):

        exit_program('Some message.', 123)

        mock_exit.assert_called_once_with(123)

    @patch('config_rpm_maker.exitprogram.exit')
    @patch('config_rpm_maker.exitprogram.LOGGER')
    def test_should_log_message_as_info_if_return_code_is_zero(self, mock_logger, mock_exit):

        exit_program('Success.', 0)

        mock_logger.info.assert_called_with('Success.')
        self.assertEqual(0, mock_logger.error.call_count)

    @patch('config_rpm_maker.exitprogram.exit')
    @patch('config_rpm_maker.exitprogram.LOGGER')
    def test_should_log_message_as_error_if_return_code_is_not_zero(self, mock_logger, mock_exit):

        exit_program('Failed.', 1)

        mock_logger.error.assert_called_with('Failed.')

    @patch('config_rpm_maker.exitprogram.time')
    @patch('config_rpm_maker.exitprogram.exit')
    @patch('config_rpm_maker.exitprogram.LOGGER')
    def test_should_not_log_elapsed_time_when_we_did_not_start_to_measure_the_time(self, mock_logger, mock_exit, mock_time):

        mock_time.return_value = 1

        exit_program('Success.', 0)

        self.assertEqual(1, len(mock_logger.info.call_args_list))

    @patch('config_rpm_maker.exitprogram.get_timestamp_from_start')
    @patch('config_rpm_maker.exitprogram.time')
    @patch('config_rpm_maker.exitprogram.exit')
    @patch('config_rpm_maker.exitprogram.LOGGER')
    def test_should_log_elapsed_time(self, mock_logger, mock_exit, mock_time, mock_get_timestamp_from_start):

        mock_get_timestamp_from_start.return_value = 0
        mock_time.return_value = 1

        exit_program('Success.', 0)

        mock_logger.info.assert_any_call('Elapsed time: 1.0s')

    @patch('config_rpm_maker.exitprogram.get_timestamp_from_start')
    @patch('config_rpm_maker.exitprogram.time')
    @patch('config_rpm_maker.exitprogram.exit')
    @patch('config_rpm_maker.exitprogram.LOGGER')
    def test_should_round_elapsed_time_down_to_two_decimals_after_dot(self, mock_logger, mock_exit, mock_time, mock_get_timestamp_from_start):

        mock_get_timestamp_from_start.return_value = 0
        mock_time.return_value = 0.555555555555

        exit_program('Success.', 0)

        mock_logger.info.assert_any_call('Elapsed time: 0.56s')


class GetTimeStampFromStart(TestCase):

    @patch('config_rpm_maker.exitprogram._timestamp_at_start')
    def test_should_return_time_stamp_from_start(self, mock_timestamp):

        actual_time_stamp = get_timestamp_from_start()

        self.assertEqual(mock_timestamp, actual_time_stamp)
