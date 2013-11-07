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
