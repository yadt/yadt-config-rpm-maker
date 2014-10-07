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
import subprocess
import rpm

from integration_test_support import IntegrationTest, IntegrationTestException

from config_rpm_maker.configrpmmaker import (CouldNotBuildSomeRpmsException,
                                             CouldNotUploadRpmsException,
                                             ConfigRpmMaker,
                                             configuration)
from config_rpm_maker.configuration.properties import (is_no_clean_up_enabled,
                                                       get_svn_path_to_config,
                                                       get_config_rpm_prefix,
                                                       get_temporary_directory,
                                                       get_rpm_upload_command)
from config_rpm_maker.configuration import build_config_viewer_host_directory
from config_rpm_maker.segment import All, Typ
from config_rpm_maker.svnservice import SvnService

EXECUTION_ERROR_MESSAGE = """Execution of "{command_with_arguments}" failed. Error code was {error_code}
stdout was: "{stdout}"
stderr was: "{stderr}"
"""


class ConfigRpmMakerIntegrationTest(IntegrationTest):

    def test_should_find_matching_hosts(self):
        config_rpm_maker = ConfigRpmMaker(None, None)
        self.assertEqual(['berweb01', 'devweb01'], config_rpm_maker._find_matching_hosts(All(), 'all/foo/bar', ['berweb01', 'devweb01']))
        self.assertEqual([], config_rpm_maker._find_matching_hosts(All(), 'foo/bar', ['berweb01', 'devweb01']))
        self.assertEqual(['berweb01', 'devweb01'], config_rpm_maker._find_matching_hosts(Typ(), 'typ/web', ['berweb01', 'devweb01']))

    def test_should_identify_affected_hosts(self):
        config_rpm_maker = ConfigRpmMaker(None, None)
        self.assertEqual(set(['berweb01', 'devweb01', 'tuvweb02']), config_rpm_maker._get_affected_hosts(['typ/web', 'foo/bar'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['berweb01', 'devweb01', 'tuvweb02']), config_rpm_maker._get_affected_hosts(['foo/bar', 'all'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['berweb01', 'tuvweb02']), config_rpm_maker._get_affected_hosts(['loc/pro', 'loc/tuv'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['devweb01']), config_rpm_maker._get_affected_hosts(['foo/bar', 'loctyp/devweb'], ['berweb01', 'devweb01', 'tuvweb02']))
        self.assertEqual(set(['devweb01']), config_rpm_maker._get_affected_hosts(['foo/bar', 'host/devweb01'], ['berweb01', 'devweb01', 'tuvweb02']))

    def test_should_build_hosts_and_cleanup_work_dir(self):
        config_rpm_maker = self._given_config_rpm_maker()

        try:
            config_rpm_maker.build()
        except Exception:
            # the cleanup should be independent of the result of the build operation
            pass

        self.assert_path_does_not_exist(config_rpm_maker.work_dir)
        self.assert_path_does_not_exist(config_rpm_maker.error_log_file)

    def test_should_not_clean_up_working_directory(self):

        configuration.set_property(is_no_clean_up_enabled, True)
        config_rpm_maker = self._given_config_rpm_maker()

        try:
            config_rpm_maker.build()
        except Exception:
            # the cleanup should be independent of the result of the build operation
            pass

        self.assert_path_exists(config_rpm_maker.work_dir)
        self.assert_path_exists(config_rpm_maker.error_log_file)

    def test_should_build_rpms_for_hosts(self):

        configuration.set_property(is_no_clean_up_enabled, True)
        config_rpm_maker = self._given_config_rpm_maker()
        rpms = config_rpm_maker.build()

        self.assertEqual(12, len(rpms))

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
                          'vars/var_in_var': 'berwebberweb'},
                'symlinks': {'symlinks/link1': '/foo/bar'},
            },
        }

        for host in hosts_to_check:
            host_to_check = hosts_to_check[host]
            requires = host_to_check.get('requires', None)
            provides = host_to_check.get('provides', None)
            files = host_to_check.get('files', None)
            symlinks = host_to_check.get('symlinks', None)
            self.assertRpm(host, rpms, requires=requires, provides=provides, files=files, symlinks=symlinks)

        self.assertRpm("group-dev-web",
                       rpms,
                       requires=['all-req', 'all-req2', 'ty-web-requirement', 'yadt-config-group-dev-web-repos', 'yadt-minion'],
                       provides=['all-prov', 'all-prov2', 'all-prov3', 'typ-web-provides', 'yadt-config-all', 'yadt-config-group-dev-web'],
                       exhaustive=True)

    def test_should_perform_chunked_uploads(self):
        old_config = get_rpm_upload_command()
        target_file = os.path.abspath(os.path.join(get_temporary_directory(), 'upload.txt'))
        if os.path.exists(target_file):
            os.remove(target_file)
        cmd_file = os.path.abspath(os.path.join(get_temporary_directory(), 'upload.sh'))
        with open(cmd_file, 'w') as f:
            f.write('#!/bin/bash\ndest=$1 ; shift ; echo "${#@} $@" >> "$dest"')

        os.chmod(cmd_file, 0755)
        cmd = '%s %s' % (cmd_file, target_file)
        configuration.set_property(get_rpm_upload_command, cmd)
        try:
            ConfigRpmMaker(None, None)._upload_rpms(['a' for x in range(25)])
        finally:
            configuration.set_property(get_rpm_upload_command, old_config)

        self.assertTrue(os.path.exists(target_file))
        with open(target_file) as f:
            self.assertEqual(f.read(), '10 a a a a a a a a a a\n10 a a a a a a a a a a\n5 a a a a a\n')

    def test_should_raise_CouldNotBuildSomeRpmsException(self):
        self.assertRaises(CouldNotBuildSomeRpmsException, ConfigRpmMaker(None, None)._build_hosts, ['devabc123'])

    def test_should_raise_CouldNotUploadRpmsException(self):
        rpm_upload_command_before_test = get_rpm_upload_command()
        configuration.set_property(get_rpm_upload_command, "foobar")

        self.assertRaises(CouldNotUploadRpmsException, ConfigRpmMaker(None, None)._upload_rpms, [''])

        configuration.set_property(get_rpm_upload_command, rpm_upload_command_before_test)

    def test_should_move_config_viewer_data_to_destination(self):

        config_rpm_maker = self._given_config_rpm_maker()

        config_rpm_maker.build()

        self.assert_revision_file_contains_revision('devweb01', '2')
        self.assert_revision_file_contains_revision('tuvweb01', '2')
        self.assert_revision_file_contains_revision('berweb01', '2')

    def test_should_only_move_config_viewer_data_to_destination_when_revision_is_higher(self):

        config_rpm_maker = self._given_config_rpm_maker()

        self.write_revision_file_for_hostname('tuvweb01', revision='3')
        self.write_revision_file_for_hostname('berweb01', revision='4')

        config_rpm_maker.build()

        self.assert_revision_file_contains_revision('devweb01', revision='2')
        self.assert_revision_file_contains_revision('tuvweb01', revision='3')
        self.assert_revision_file_contains_revision('berweb01', revision='4')

    def test_should_move_or_remove_temporary_directories(self):

        config_rpm_maker = self._given_config_rpm_maker()

        self.write_revision_file_for_hostname('tuvweb01', revision='3')
        self.write_revision_file_for_hostname('berweb01', revision='4')

        config_rpm_maker.build()

        self.assert_path_does_not_exist(build_config_viewer_host_directory('devweb01', revision='2'))
        self.assert_path_does_not_exist(build_config_viewer_host_directory('tuvweb01', revision='2'))
        self.assert_path_does_not_exist(build_config_viewer_host_directory('berweb01', revision='2'))

    def _given_config_rpm_maker(self):
        svn_service = SvnService(base_url=self.repo_url, path_to_config=get_svn_path_to_config())

        return ConfigRpmMaker('2', svn_service)

    def assertRpm(self, hostname, rpms, requires=None, provides=None, files=None, symlinks=None, exhaustive=False):
        path = None
        for rpm_name in rpms:
            name = os.path.basename(rpm_name)
            if name.startswith(get_config_rpm_prefix() + hostname) and 'noarch' in name and not 'repos' in name:
                path = rpm_name
                break

        if not path:
            raise Exception("Did not find host '%s' in %s." % (hostname, str(rpms)))
        self.assertTrue(os.path.exists(path), "Could not find file %s." % path)
        ts = rpm.TransactionSet()
        ts.setVSFlags((rpm._RPMVSF_NOSIGNATURES | rpm._RPMVSF_NODIGESTS))
        f = os.open(path, os.O_RDONLY)
        try:
            hdr = ts.hdrFromFdno(f)
            del ts
            self.assertRequires(hdr, hostname, requires, exhaustive)
            self.assertProvides(hdr, hostname, provides, exhaustive)
        finally:
            os.close(f)

        extract_path = self.extractRpmFiles(path, hostname)
        self.assertFiles(files, extract_path)
        self.assertSymlinks(symlinks, extract_path)

    def assertSymlinks(self, symlinks, extract_path):
        if symlinks:
            for symlink_file in symlinks:
                complete_path = os.path.join(extract_path, symlink_file)
                if os.path.exists(complete_path):
                    self.fail("Symlink %s was not created." % complete_path)
                expected_target = symlinks[symlink_file]
                real_target = os.readlink(complete_path)
                self.assertEquals(real_target, expected_target, "Symlink target for %s differs\nExpected: %s\nGot: %s" % (complete_path, expected_target, real_target))

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

    def _without_rpmlib_packages(self, requires):
        filtered_requires = [package_name for package_name in requires if not package_name.startswith('rpmlib')]
        return sorted(filtered_requires)

    def assertRequires(self, hdr, hostname, requires, exhaustive):
        if requires:
            if exhaustive:
                real_requires = requires
            else:
                real_requires = requires + ['hostname-' + hostname,
                                            'yadt-config-' + hostname + '-repos',
                                            'rpmlib(CompressedFileNames)',
                                            'rpmlib(PayloadFilesHavePrefix)',
                                            'yadt-minion']

            expected_requires = self._without_rpmlib_packages(real_requires)
            actual_requires = self._without_rpmlib_packages(hdr['requires'])
            self.assertListsEqual(expected_requires, actual_requires)

    def assertProvides(self, hdr, hostname, provides, exhaustive):
        if provides:
            if exhaustive:
                real_provides = provides
            else:
                real_provides = provides + ['yadt-config-all', 'yadt-config-' + hostname, ]

            self.assertListsEqual(sorted(real_provides), sorted(hdr['provides']))

    def assertListsEqual(self, expected, actual):
        difference = list(set(expected) - set(actual)) + list(set(actual) - set(expected))
        self.assertEqual(expected, actual, "Lists are different.\nExpected: %s\n     Got: %s\ndifference is: %s" % (str(expected), str(actual), str(difference)))

    def extractRpmFiles(self, path, hostname):
        extract_path = os.path.join(get_temporary_directory(), hostname + '.extract')
        os.mkdir(extract_path)

        command_with_arguments = 'rpm2cpio ' + os.path.abspath(path) + ' | cpio  -idmv'
        process = subprocess.Popen(command_with_arguments,
                                   shell=True,
                                   cwd=extract_path,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            message = EXECUTION_ERROR_MESSAGE.format(command_with_arguments=command_with_arguments,
                                                     error_code=process.returncode,
                                                     stdout=stdout or "",
                                                     stderr=stderr or "")

            raise IntegrationTestException(message)

        return extract_path
