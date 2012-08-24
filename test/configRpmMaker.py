import os
import shutil
import subprocess
import rpm
from baseTestCase import SvnTestCase

from config_rpm_maker import ConfigRpmMaker, config
from config_rpm_maker.segment import All, Typ
from config_rpm_maker.svn import SvnService
from config_rpm_maker import config as config_dev
import test_config

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

    def test_build_hosts(self):
        self._cleanup_temp_dir()
        self.create_svn_repo()
        svn_service = SvnService(base_url=self.repo_url, username=None, password=None, path_to_config=config.get('svn_path_to_config'))
        config_rpm_maker = ConfigRpmMaker('2', svn_service)

        rpms = config_rpm_maker.build()
        self.assertEqual(9, len(rpms))

        hosts_to_check = {
            'devweb01': {},
            'tuvweb01': {},
            'berweb01': {
                'requires' : ['all-req', 'all-req2', 'ber-req', 'ber-req2', 'host-spec-requirement', 'pro-req', 'ty-web-requirement'],
                'provides' : ['all-prov', 'all-prov2', 'all-prov3', 'pro-prov', 'pro-prov2', 'typ-web-provides'],
                'files' : {
                    'files/file_from_all' : '',
                    'files/file_from_ber' : '',
                    'files/file_from_pro' : '',
                    'files/override' : 'berweb',
                    'vars/override' : 'berweb',
                    'vars/var_in_var' : 'berwebberweb',
                    }
            }
        }
        for host in hosts_to_check:
            self.assertRpm(host, rpms, requires=hosts_to_check[host].get('requires', None), provides=hosts_to_check[host].get('provides', None), files=hosts_to_check[host].get('files', None))

    def _cleanup_temp_dir(self):
        temp_dir = config_dev.get('temp_dir')
        if temp_dir:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

    def assertRpm(self, hostname, rpms, requires = None, provides = None, files=None):
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
        ts.setVSFlags((rpm._RPMVSF_NOSIGNATURES|rpm._RPMVSF_NODIGESTS))
        f = open(path, 'r')
        try:
            hdr = ts.hdrFromFdno(f)
            del ts
            self.assertRequires(hdr, hostname, requires)
            self.assertProvides(hdr, hostname, provides)
        finally:
            f.close()

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
            real_requires = requires + ['hostname-' + hostname,'is24-config-' + hostname + '-repos', 'rpmlib(CompressedFileNames)', 'rpmlib(PayloadFilesHavePrefix)', 'yadt-client']
            self.assertArrayEqual(sorted(real_requires), sorted(hdr['requires']))

    def assertProvides(self, hdr, hostname, provides):
        if provides:
            real_provides = provides + ['is24-config-all', 'is24-config-' + hostname, ]
            self.assertArrayEqual(sorted(real_provides), sorted(hdr['provides']))

    def assertArrayEqual(self, expected, value):
        self.assertEqual(len(expected), len(value), "Lists have different element count. Expected %s , Got %s" % (str(expected), str(value)))
        for i in range(len(expected)):
            self.assertEqual(expected[i], value[i], "Element %d is different. Expected %s , Got %s" % (i, str(expected), str(value)))

    def extractRpmFiles(self, path, hostname):
        extract_path = os.path.join(config_dev.get('temp_dir'), hostname + '.extract')
        os.mkdir(extract_path)

        p = subprocess.Popen('rpm2cpio ' + os.path.abspath(path) + ' | cpio  -idmv', shell=True, cwd=extract_path)
        p.communicate()

        return extract_path
