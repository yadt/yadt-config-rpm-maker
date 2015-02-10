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

import unittest

from config_rpm_maker.segment import LocTyp, All, Host, Short_HostNr


class SegmentTest(unittest.TestCase):

    def test_should_return_all_when_hosts_are_given(self):
        self.assertEqual(['all', ], All().get('devweb01'))
        self.assertEqual(['all', ], All().get_svn_paths('berweb17'))

    def test_should_return_corresponding_loctyp(self):
        self.assertEqual(['devweb', ], LocTyp().get('devweb01'))

        self.assertEqual(['proweb', 'berweb'], LocTyp().get('berweb01'))
        self.assertEqual(['proweb', 'hamweb'], LocTyp().get('hamweb01'))

        self.assertEqual(['loctyp/proweb', 'loctyp/berweb'],
                         LocTyp().get_svn_paths('berweb17'))
        self.assertEqual(['loctyp/proweb', 'loctyp/hamweb'],
                         LocTyp().get_svn_paths('hamweb17'))

    def test_should_return_path_to_host_when_host_is_given(self):
        self.assertEqual(['devweb01', ], Host().get('devweb01'))
        self.assertEqual(['host/berweb17', ], Host().get_svn_paths('berweb17'))

    def test_should_return_short_hostnr(self):
        self.assertEqual(['1', ], Short_HostNr().get('devweb01'))
        self.assertEqual(['21', ], Short_HostNr().get('devweb21'))
        self.assertEqual('SHORT_HOSTNR', Short_HostNr().get_variable_name())
