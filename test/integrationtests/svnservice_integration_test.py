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

from integration_test_support import IntegrationTest

from config_rpm_maker import config
from config_rpm_maker.config import KEY_SVN_PATH_TO_CONFIG
from config_rpm_maker.svnservice import SvnServiceException, SvnService


class SvnServiceTest(IntegrationTest):

    def test_get_change_set(self):
        service = SvnService(self.repo_url, None, None, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        self.assertEqual(['typ/web/data/index.html'], service.get_change_set(2))

    def test_get_hosts(self):
        service = SvnService(self.repo_url, None, None, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        self.assertEqual(['berweb01', 'devweb01', 'tuvweb01'], service.get_hosts(2))

    def test_export(self):
        service = SvnService(self.repo_url, None, None, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        self.assertEqual([('host/berweb01', 'VARIABLES'), ('host/berweb01', 'VARIABLES/RPM_REQUIRES')], service.export('host/berweb01', 'target/tmp/test', 2))

    def test_log(self):
        service = SvnService(self.repo_url, None, None, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        logs = service.log('', 2, 5)
        self.assertEqual(1, len(logs))

    def test_should_raise_SvnServiceException(self):
        service = SvnService(self.repo_url, None, None, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))
        self.assertRaises(SvnServiceException, service.get_change_set, 13)
