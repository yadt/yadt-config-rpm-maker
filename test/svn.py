from baseTestCase import SvnTestCase
from config_rpm_maker import config
from config_rpm_maker.svn import SvnService

class SvnServiceTest(SvnTestCase):

    def setUp(self):
        self.create_svn_repo()

    def test_get_change_set(self):
        service = SvnService(self.repo_url, None, None, path_to_config = config.get('svn_path_to_config'))
        self.assertEqual(['typ/web/data/index.html'], service.get_change_set(2))

    def test_get_hosts(self):
        service = SvnService(self.repo_url, None, None, path_to_config = config.get('svn_path_to_config'))
        self.assertEqual(['berweb01', 'devweb01', 'tuvweb01'], service.get_hosts(2))

    def test_export(self):
        service = SvnService(self.repo_url, None, None, path_to_config = config.get('svn_path_to_config'))
        self.assertEqual([('host/berweb01', 'VARIABLES'), ('host/berweb01', 'VARIABLES/RPM_REQUIRES')], service.export('host/berweb01', 'target/tmp/test', 2))

    def test_log(self):
        service = SvnService(self.repo_url, None, None, path_to_config = config.get('svn_path_to_config'))
        logs = service.log('', 2, 5)
        self.assertEqual(1, len(logs))
