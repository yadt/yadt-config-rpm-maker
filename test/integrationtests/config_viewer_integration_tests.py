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


from os.path import join

from integration_test_support import IntegrationTest

from config_rpm_maker.config import KEY_NO_CLEAN_UP, KEY_SVN_PATH_TO_CONFIG
from config_rpm_maker.configrpmmaker import ConfigRpmMaker, config
from config_rpm_maker.svnservice import SvnService


class ConfigViewerIntegrationTests(IntegrationTest):

    def test_should_create_files_for_hosts(self):

        config.set_property(KEY_NO_CLEAN_UP, True)
        svn_service = SvnService(base_url=self.repo_url, path_to_config=config.get(KEY_SVN_PATH_TO_CONFIG))

        ConfigRpmMaker('2', svn_service).build()

        host_name = 'berweb01'
        host_directory = config.build_config_viewer_host_directory(host_name)
        overlaying_path = join(host_directory, host_name + '.overlaying')
        self.assert_file_content(overlaying_path, """host/berweb01:/VARIABLES
loctyp/berweb:/VARIABLES/OVERRIDE
loc/pro:/VARIABLES/RPM_PROVIDES
host/berweb01:/VARIABLES/RPM_REQUIRES
loctyp/berweb:/VARIABLES/VAR_IN_VAR
typ/web:/data
typ/web:/data/file-with-special-character
typ/web:/data/index.html
typ/web:/data/other.html
loctyp/berweb:/files
all:/files/binary.zip
all:/files/file_from_all
loc/ber:/files/file_from_ber
loc/pro:/files/file_from_pro
loctyp/berweb:/files/override
loctyp/berweb:/vars
all:/vars/override
loctyp/berweb:/vars/var_in_var
""")
