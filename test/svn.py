import unittest

from config_rpm_maker.svn import SvnService
import test_config

class SvnServiceTest(unittest.TestCase):

    def test_get_change_set(self):
        service = SvnService(test_config.get('svn_base_url'), test_config.get('svn_username'), test_config.get('svn_password'), path_to_config = test_config.get('svn_path_to_config'))
        self.assertEqual(test_config.get('svn_expected_paths'), service.get_change_set(test_config.get('svn_revision')))

    def test_get_hosts(self):
        service = SvnService(test_config.get('svn_base_url'), test_config.get('svn_username'), test_config.get('svn_password'), path_to_config = test_config.get('svn_path_to_config'))
        self.assertEqual(['berweb01', 'devweb01', 'tuvweb01'], service.get_hosts(test_config.get('svn_revision')))

    def test_export(self):
        service = SvnService(test_config.get('svn_base_url'), test_config.get('svn_username'), test_config.get('svn_password'), path_to_config = test_config.get('svn_path_to_config'))
        self.assertEqual([('host/berweb01', 'VARIABLES')], service.export('host/berweb01', 'target/tmp/test', test_config.get('svn_revision')))

    def test_log(self):
        service = SvnService(test_config.get('svn_base_url'), test_config.get('svn_username'), test_config.get('svn_password'), path_to_config = test_config.get('svn_path_to_config'))
        logs = service.log('', test_config.get('svn_revision'), 5)
        self.assertEqual(5, len(logs))