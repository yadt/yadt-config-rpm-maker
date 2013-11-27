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

from StringIO import StringIO
from unittest import TestCase


class UnitTests(TestCase):

    def create_fake_file(self, content=""):
        """
            Creates a fake file-like object. Use this is if you have to mock away
                @patch('__builtin__.open')

        """
        class FakeFile(StringIO):
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        return FakeFile(content)
