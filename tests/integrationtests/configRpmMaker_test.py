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
import rpm

from baseTestCase import SvnTestCase

from config_rpm_maker import ConfigRpmMaker, config
from config_rpm_maker.segment import All, Typ
from config_rpm_maker.svn import SvnService
from config_rpm_maker import config as config_dev  # TODO: WTF? config has been imported twice ...


class ConfigRpmMakerTest(SvnTestCase):

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

    def test_build_hosts_and_cleanup_work_dir(self):
        config_rpm_maker = self._given_config_rpm_maker()
        try:
            config_rpm_maker.build()
        except Exception:
            # the cleanup should be independent of the result of the build operation
            pass
        self.assertFalse(os.path.exists(config_rpm_maker.work_dir))
        self.assertFalse(os.path.exists(config_rpm_maker.error_log_file))

    def test_build_hosts(self):
        config_rpm_maker = self._given_config_rpm_maker(keep_work_dir=True)
        rpms = config_rpm_maker.build()
        self.assertEqual(9, len(rpms))

        hosts_to_check = {
            'devweb01': {},
            'tuvweb01': {},
            'berweb01': {
                'requires': ['all-req', 'all-req2', 'ber-req', 'ber-req2', 'host-spec-requirement', 'pro-req', 'ty-web-requirement'],
                'provides': ['all-prov', 'all-prov2', 'all-prov3', 'pro-prov', 'pro-prov2', 'typ-web-provides'],
                'files': {'files/file_from_all': '',
                          'files/file_from_ber': '',
                          'files/file_from_pro': '',
                          'files/override': 'berweb',
                          'vars/override': 'berweb',
                          'vars/var_in_var': 'berwebberweb'}
            }
        }
        for host in hosts_to_check:
            host_to_check = hosts_to_check[host]
            requires = host_to_check.get('requires', None)
            provides = host_to_check.get('provides', None)
            files = host_to_check.get('files', None)
            self.assertRpm(host, rpms, requires=requires, provides=provides, files=files)

    def test_chunked_uploads(self):
        old_config = config.get('rpm_upload_cmd')
        target_file = os.path.abspath(os.path.join(config.get('temp_dir'), 'upload.txt'))
        if os.path.exists(target_file):
            os.remove(target_file)
        cmd_file = os.path.abspath(os.path.join(config.get('temp_dir'), 'upload.sh'))
        with open(cmd_file, 'w') as f:
            f.write('#!/bin/bash\ndest=$1 ; shift ; echo "${#@} $@" >> "$dest"')

        os.chmod(cmd_file, 0755)
        cmd = '%s %s' % (cmd_file, target_file)
        config.setvalue('rpm_upload_cmd', cmd)
        try:
            ConfigRpmMaker(None, None)._upload_rpms(['a' for x in range(25)])
        finally:
            config.setvalue('rpm_upload_cmd', old_config)

        self.assertTrue(os.path.exists(target_file))
        with open(target_file) as f:
            self.assertEqual(f.read(), '10 a a a a a a a a a a\n10 a a a a a a a a a a\n5 a a a a a\n')

    def _given_config_rpm_maker(self, keep_work_dir=False):
        self._cleanup_temp_dir()
        self.create_svn_repo()
        svn_service = SvnService(base_url=self.repo_url, username=None, password=None, path_to_config=config.get('svn_path_to_config'))

        if keep_work_dir:
            os.environ['KEEPWORKDIR'] = '1'
        elif 'KEEPWORKDIR' in os.environ:
            del os.environ['KEEPWORKDIR']

        return ConfigRpmMaker('2', svn_service)

    def _cleanup_temp_dir(self):
        temp_dir = config_dev.get('temp_dir')
        if temp_dir:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

    def assertRpm(self, hostname, rpms, requires=None, provides=None, files=None):
        path = None
        for rpm_name in rpms:
            name = os.path.basename(rpm_name)
            if name.startswith(config_dev.get('config_rpm_prefix') + hostname) and 'noarch' in name and not 'repos' in name:
                path = rpm_name
                break

        if not path:
            raise Exception("Did not find host '%s' in %s." % (hostname, str(rpms)))

        self.assertTrue(os.path.exists(path), "Could not find file %s ." % path)
        ts = rpm.TransactionSet()
        ts.setVSFlags((rpm._RPMVSF_NOSIGNATURES | rpm._RPMVSF_NODIGESTS))
        f = os.open(path, os.O_RDONLY)
        try:
            hdr = ts.hdrFromFdno(f)
            del ts
            self.assertRequires(hdr, hostname, requires)
            self.assertProvides(hdr, hostname, provides)
        finally:
            os.close(f)

        extract_path = self.extractRpmFiles(path, hostname)
        self.assertFiles(files, extract_path)

    def assertFiles(self, files, extract_path):
        if files:
            for file_path in files:
                complete_path = os.path.join(extract_path, file_path)
                f = open(complete_path, 'r')
                try:
                    content = f.read()
                    self.assertEqual(content, files[file_path], "Content of '%s' differs:\nExpected: %s\nGot: %s" % (file_path, content, files[file_path]))
                finally:
                    f.close()

    def assertRequires(self, hdr, hostname, requires):
        if requires:
            real_requires = requires + ['hostname-' + hostname, 'yadt-config-' + hostname + '-repos', 'rpmlib(CompressedFileNames)', 'rpmlib(PayloadFilesHavePrefix)', 'yadt-client']
            self.assertListsEqual(sorted(real_requires), sorted(hdr['requires']))

    def assertProvides(self, hdr, hostname, provides):
        if provides:
            real_provides = provides + ['yadt-config-all', 'yadt-config-' + hostname, ]
            self.assertListsEqual(sorted(real_provides), sorted(hdr['provides']))

    def assertListsEqual(self, expected, actual):
        difference = list(set(expected) - set(actual)) + list(set(actual) - set(expected))
        self.assertEqual(expected, actual, "Lists are different.\nExpected: %s\n     Got: %s\ndifference is: %s" % (str(expected), str(actual), str(difference)))

    def extractRpmFiles(self, path, hostname):
        extract_path = os.path.join(config_dev.get('temp_dir'), hostname + '.extract')
        os.mkdir(extract_path)

        p = subprocess.Popen('rpm2cpio ' + os.path.abspath(path) + ' | cpio  -idmv', shell=True, cwd=extract_path)
        p.communicate()

        return extract_path
