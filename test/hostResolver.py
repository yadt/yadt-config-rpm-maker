import unittest
from config_rpm_maker.hostResolver import HostResolver

class HostResolverTest(unittest.TestCase):

   def test_resolve_localhost(self):
       ip, fqdn, aliases = HostResolver().resolve('localhost')
       self.assertTrue(ip == '127.0.0.1' or ip == '::1')
       self.assertEqual(fqdn, 'localhost')
