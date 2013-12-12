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

        self.assert_config_viewer_file('berweb01', 'berweb01.overlaying', """host/berweb01:/VARIABLES
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

        self.assert_config_viewer_file('berweb01', 'berweb01.variables', """<!DOCTYPE html><html><head><title>berweb01.variables</title></head><body><pre>                                 ALIASES :
                                     ALL : all
                                    FQDN : localhost.localdomain
                                    HOST : berweb01
                                  HOSTNR : 01
                                      IP : 127.0.0.1
                                     LOC : ber
                                  LOCTYP : berweb
                                OVERRIDE : berweb
                                REVISION : 2
                            RPM_PROVIDES : pro-prov2, all-prov2, all-prov, pro-prov, typ-web-provides, all-prov3
                            RPM_REQUIRES : ber-req2, pro-req, all-req, ber-req, ty-web-requirement, all-req2, host-spec-requirement
                  RPM_REQUIRES_NON_REPOS : ber-req2, pro-req, all-req, ber-req, ty-web-requirement, all-req2, host-spec-requirement
                      RPM_REQUIRES_REPOS :
                            SHORT_HOSTNR : 1
                                     TYP : web
                              VAR_IN_VAR : <strong title="LOC">ber</strong><strong title="TYP">web</strong><strong title="OVERRIDE">berweb</strong>
</pre></body></html>""")

        host_name = 'berweb01'

        self.assert_config_viewer_path_exists(host_name, 'data', 'file-with-special-character')

        self.assert_config_viewer_file(host_name, join('data', 'index.html'), "<!DOCTYPE html><html><head><title>index.html</title></head><body><pre>&lt;html&gt;&lt;head&gt;&lt;/head&gt;&lt;/html&gt;")
        self.assert_config_viewer_file(host_name, join('data', 'other.html'), "<!DOCTYPE html><html><head><title>other.html</title></head><body><pre>&lt;!DOCTYPE HTML PUBLIC &quot;-//W3C//DTD HTML 4.01 Transitional//EN&quot;")

        self.assert_config_viewer_path_exists(host_name, 'files', 'binary.zip')
        self.assert_config_viewer_file(host_name, join('files', 'file_from_all'), "")
        self.assert_config_viewer_file(host_name, join('files', 'file_from_ber'), "")
        self.assert_config_viewer_file(host_name, join('files', 'file_from_pro'), "")
        self.assert_config_viewer_file(host_name, join('files', 'override'), "<!DOCTYPE html><html><head><title>override</title></head><body><pre>berweb</pre></body></html>")

        self.assert_config_viewer_file(host_name, 'unused_variables.txt', "<!DOCTYPE html><html><head><title>unused_variables.txt</title></head><body><pre>ALIASES")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'ALIASES'), "")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'ALL'), "<!DOCTYPE html><html><head><title>ALL</title></head><body><pre>all</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'FQDN'), "<!DOCTYPE html><html><head><title>FQDN</title></head><body><pre>localhost.localdomain</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'HOST'), "<!DOCTYPE html><html><head><title>HOST</title></head><body><pre>%s</pre></body></html>" % host_name)
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'HOSTNR'), "<!DOCTYPE html><html><head><title>HOSTNR</title></head><body><pre>01</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'IP'), "<!DOCTYPE html><html><head><title>IP</title></head><body><pre>127.0.0.1</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'LOC'), "<!DOCTYPE html><html><head><title>LOC</title></head><body><pre>ber</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'LOCTYP'), "<!DOCTYPE html><html><head><title>LOCTYP</title></head><body><pre>berweb</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'OVERLAYING'), "<!DOCTYPE html><html><head><title>OVERLAYING</title></head><body><pre>            host/berweb01 : /VARIABLES")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'OVERRIDE'), "<!DOCTYPE html><html><head><title>OVERRIDE</title></head><body><pre>berweb</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'REVISION'), "2")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'RPM_PROVIDES'), "<!DOCTYPE html><html><head><title>RPM_PROVIDES</title></head><body><pre>pro-prov2, all-prov2, all-prov, pro-prov, typ-web-provides, all-prov3</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'RPM_REQUIRES'), "<!DOCTYPE html><html><head><title>RPM_REQUIRES</title></head><body><pre>ber-req2, pro-req, all-req, ber-req, ty-web-requirement, all-req2, host-spec-requirement</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'RPM_REQUIRES_NON_REPOS'), "<!DOCTYPE html><html><head><title>RPM_REQUIRES_NON_REPOS</title></head><body><pre>ber-req2, pro-req, all-req, ber-req, ty-web-requirement, all-req2, host-spec-requirement</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'RPM_REQUIRES_REPOS'), "")
        self.assert_config_viewer_file_exactly(host_name, join('VARIABLES', 'SHORT_HOSTNR'), "1")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'SVNLOG'), "<!DOCTYPE html><html><head><title>SVNLOG</title></head><body><pre>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'TYP'), "<!DOCTYPE html><html><head><title>TYP</title></head><body><pre>web</pre></body></html>")
        self.assert_config_viewer_file(host_name, join('VARIABLES', 'VAR_IN_VAR'), '''<!DOCTYPE html><html><head><title>VAR_IN_VAR</title></head><body><pre><strong title="LOC">ber</strong><strong title="TYP">web</strong><strong title="OVERRIDE">berweb</strong></pre></body></html>''')

        self.assert_config_viewer_file(host_name, join('vars', 'override'), '''<!DOCTYPE html><html><head><title>override</title></head><body><pre><strong title="OVERRIDE">berweb</strong></pre></body></html>''')
        self.assert_config_viewer_file(host_name, join('vars', 'var_in_var'), '''<!DOCTYPE html><html><head><title>var_in_var</title></head><body><pre><strong title="VAR_IN_VAR">berwebberweb</strong></pre></body></html>''')
        self.assert_config_viewer_path_exists(host_name, 'yadt-config-%s.spec' % host_name)

    def assert_config_viewer_file_exactly(self, host_name, file_path, content):
        host_directory = config.build_config_viewer_host_directory(host_name)
        overlaying_path = join(host_directory, file_path)
        self.assert_file_content(overlaying_path, content)

    def assert_config_viewer_file(self, host_name, file_path, content):
        host_directory = config.build_config_viewer_host_directory(host_name)
        overlaying_path = join(host_directory, file_path)
        self.assert_file_content_line_by_line(overlaying_path, content)

    def assert_config_viewer_path_exists(self, host_name, *path):
        path_to_check = join(config.build_config_viewer_host_directory(host_name), *path)
        self.assert_path_exists(path_to_check)
