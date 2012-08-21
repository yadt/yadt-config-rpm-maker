import unittest

from config_rpm_maker.segment import LocTyp, All, Host, Short_HostNr

class SegmentTest(unittest.TestCase):

    def test_all(self):
        self.assertEqual(['all', ], All().get('devweb01'))
        self.assertEqual(['all', ], All().get_svn_paths('berweb17'))

    def test_loctyp(self):
        self.assertEqual(['devweb', ], LocTyp().get('devweb01'))
        self.assertEqual(['proweb', 'hamweb'], LocTyp().get('hamweb01'))
        self.assertEqual(['loctyp/proweb', 'loctyp/berweb'], LocTyp().get_svn_paths('berweb17'))

    def test_host(self):
        self.assertEqual(['devweb01', ], Host().get('devweb01'))
        self.assertEqual(['host/berweb17', ], Host().get_svn_paths('berweb17'))

    def test_short_hostnr(self):
        self.assertEqual(['1', ], Short_HostNr().get('devweb01'))
        self.assertEqual(['21', ], Short_HostNr().get('devweb21'))
        self.assertEqual('SHORT_HOSTNR', Short_HostNr().get_variable_name())
