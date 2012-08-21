import os
import shutil
import unittest

from config_rpm_maker import ConfigRpmMaker
from config_rpm_maker.segment import All, Typ
from config_rpm_maker.svn import SvnService
from config_rpm_maker import config as config_dev
import test_config

class ConfigRpmMakerTest(unittest.TestCase):

    def test_find_matching_hosts(self):
        config_rpm_maker = ConfigRpmMaker(None, None)
        self.assertEqual(['berweb01', 'devweb01'], config_rpm_maker._find_matching_hosts(All(), 'all/foo/bar', ['berweb01', 'devweb01']))
        self.assertEqual([], config_rpm_maker._find_matching_hosts(All(), 'foo/bar', ['berweb01', 'devweb01']))
        self.assertEqual(['berweb01', 'devweb01'], config_rpm_maker._find_matching_hosts(Typ(), 'typ/web', ['berweb01', 'devweb01']))

    def test_affected_hosts(self):
        config_rpm_maker = ConfigRpmMaker(None, None)
        self.assertEqual(set(['berweb01', 'devweb01', 'tuvweb02']), config_rpm_maker._get_affected_hosts(['typ/web', 'foo/bar'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['berweb01', 'devweb01', 'tuvweb02']), config_rpm_maker._get_affected_hosts(['foo/bar', 'all'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['berweb01', 'tuvweb02']), config_rpm_maker._get_affected_hosts(['loc/pro', 'loc/tuv'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['devweb01']), config_rpm_maker._get_affected_hosts(['foo/bar', 'loctyp/devweb'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['devweb01']), config_rpm_maker._get_affected_hosts(['foo/bar', 'host/devweb01'], ['berweb01', 'devweb01', 'tuvweb02']))

    def test_build_hosts(self):
        self._cleanup_temp_dir()
        svn_service = SvnService(base_url=test_config.get('svn_base_url'), username=test_config.get('svn_username'), password=test_config.get('svn_password'), path_to_config=test_config.get('svn_path_to_config'))
        config_rpm_maker = ConfigRpmMaker(test_config.get('svn_build_revision'), svn_service)

        config_rpm_maker.build()

    def _cleanup_temp_dir(self):
        temp_dir = config_dev.get('temp_dir')
        if temp_dir:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)