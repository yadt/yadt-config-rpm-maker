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

from config_rpm_maker.argumentvalidation import ensure_valid_revision, ensure_valid_repository_url


@patch('config_rpm_maker.argumentvalidation.exit_program')
class EnsureValidRevisionTests(TestCase):

    def test_should_exit_if_a_non_integer_string_is_given(self, mock_exit_program):

        ensure_valid_revision('abc')

        mock_exit_program.assert_called_with('Given revision "abc" is not an integer.', return_code=2)

    def test_should_not_exit_if_a_integer_string_is_given(self, mock_exit_program):

        ensure_valid_revision('123')

        self.assertEqual(None, mock_exit_program.call_args)

    def test_should_return_revision_if_a_integer_string_is_given(self, mock_exit_program):

        actual_revision = ensure_valid_revision('123')

        self.assertEqual('123', actual_revision)


@patch('config_rpm_maker.argumentvalidation.exit_program')
class EnsureValidRepositoryUrlTests(TestCase):

    def test_should_exit_program_when_strange_url_is_given(self, mock_exit_program):

        ensure_valid_repository_url('foo://bar')

        mock_exit_program.assert_called_with('Given repository url "foo://bar" is invalid.', return_code=6)

    def test_should_return_url_when_a_valid_svn_url(self, mock_exit_program):

        actual_url = ensure_valid_repository_url('svn://host/repository')

        self.assertEqual('svn://host/repository', actual_url)

    def test_should_return_url_when_a_valid_http_url(self, mock_exit_program):

        actual_url = ensure_valid_repository_url('http://host/repository')

        self.assertEqual('http://host/repository', actual_url)

    def test_should_return_url_when_a_valid_https_url(self, mock_exit_program):

        actual_url = ensure_valid_repository_url('https://host/repository')

        self.assertEqual('https://host/repository', actual_url)

    def test_should_return_url_when_a_valid_ssh_url(self, mock_exit_program):

        actual_url = ensure_valid_repository_url('ssh://host/repository')

        self.assertEqual('ssh://host/repository', actual_url)

    def test_should_return_url_when_a_valid_file_url(self, mock_exit_program):

        actual_url = ensure_valid_repository_url('file://directory/repository')

        self.assertEqual('file://directory/repository', actual_url)

    def test_should_prepend_file_scheme_if_url_has_no_scheme(self, mock_exit_program):

        actual_url = ensure_valid_repository_url('/directory/repository')

        self.assertEqual('file:///directory/repository', actual_url)
