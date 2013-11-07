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
from logging import INFO

from config_rpm_maker.__main__ import initialize_logging


class CliTests(TestCase):

    @patch('config_rpm_maker.__main__.basicConfig')
    def test_should_initialize_logging_using_configuration(self, mock_basicConfig):
        initialize_logging()

        self.assertEqual(call(format='[%(levelname)s] %(message)s', level=INFO), mock_basicConfig.call_args)
