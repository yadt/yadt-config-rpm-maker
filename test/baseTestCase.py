import os
import shutil
import subprocess
import unittest
from config_rpm_maker import config

class SvnTestCase(unittest.TestCase):

    def create_svn_repo(self):
        self.repo_dir = os.path.abspath(os.path.join(config.get('temp_dir'), 'svn_repo'))
        if os.path.exists(self.repo_dir):
            shutil.rmtree(self.repo_dir)
        os.makedirs(self.repo_dir)
        if subprocess.call('svnadmin create %s' % self.repo_dir, shell=True):
            raise Exception('Could not create svn repo.')
        self.repo_url = 'file://%s' % self.repo_dir
        if subprocess.call('svn import -q -m import testdata/svn_repo %s' % self.repo_url, shell=True):
            raise Exception('Could not import test data.')
        if subprocess.call('svn import -q -m import testdata/index.html %s/config/typ/web/data/index.html' % self.repo_url, shell=True):
            raise Exception('Could not import test data.')