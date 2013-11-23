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
from mock import Mock

from config_rpm_maker.svnservice import SvnService


class SvnServiceTests(TestCase):

    def test_should_ensure_that_all_returned_host_names_are_ordinary_strings(self):

        mock_svn_service = Mock(SvnService)
        mock_svn_service.config_url = '/path to repository/config'
        mock_svn_service.client = Mock()
        item0 = Mock()
        item0.repos_path = "get_hosts removes the first element - so this will never show up"
        item1 = Mock()
        item1.repos_path = "bar"
        item2 = Mock()
        item2.repos_path = u"spam"
        mock_svn_service.client.list.return_value = [(item0,), (item1,), (item2,)]

        actual_host_names = SvnService.get_hosts(mock_svn_service, 123)

        self.assert_is_ordinary_string(actual_host_names[0])
        self.assert_is_ordinary_string(actual_host_names[1])

    def assert_is_ordinary_string(self, text):
        self.assertTrue(isinstance(text, str), '"%s" is NOT a ordniary string!' % text)
