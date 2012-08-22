import os
import shutil
import subprocess
import tempfile
import logging
from config_rpm_maker import config
from config_rpm_maker.hostRpmBuilder import HostRpmBuilder
from config_rpm_maker.segment import OVERLAY_ORDER

logging.basicConfig(format="%(asctime)s %(levelname)5s [%(name)s] - %(message)s")
logging.getLogger().setLevel(config.get('log_level', 'INFO'))

class ConfigRpmMaker(object):

    def __init__(self, revision, svn_service):
        self.revision = revision
        self.svn_service = svn_service

    def build(self):
        logging.info("Starting with revision %s", self.revision)
        change_set = self.svn_service.get_change_set(self.revision)
        available_hosts = self.svn_service.get_hosts(self.revision)

        affected_hosts = self._get_affected_hosts(change_set, available_hosts)
        if not affected_hosts:
            logging.info("We have nothing to do. No host affected from change set: %s", str(change_set))
            return

        rpms = self._build_hosts(affected_hosts)
        self._upload_rpms(rpms)
        self._move_configviewer_dirs_to_final_destination(affected_hosts)

        return rpms

    def _move_configviewer_dir_to_final_destination(self, hosts):
        for host in hosts:
            temp_path = HostRpmBuilder.get_config_viewer_host_dir(host, True)
            dest_path = HostRpmBuilder.get_config_viewer_host_dir(host)
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.move(temp_path, dest_path)

    def _build_hosts(self, affected_hosts):
        rpms = []
        for host in affected_hosts:
            rpms += self._build_host(host)
        return rpms

    def _build_host(self, host):
        temp_dir = config.get('temp_dir')
        if temp_dir and not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        work_dir = tempfile.mkdtemp(prefix='yadt-config-rpm-maker.', suffix='.' + host, dir=temp_dir)
        return HostRpmBuilder(hostname=host, revision=self.revision, work_dir=work_dir, svn_service=self.svn_service).build()

    def _upload_rpms(self, rpms):
        rpm_upload_cmd = config.get('rpm_upload_cmd')
        if rpm_upload_cmd:
            for rpm in rpms:
                cmd = rpm_upload_cmd + ' ' + rpm
                p = subprocess.Popen(cmd, shell=True)
                p.communicate()
                if p.returncode:
                    raise Exception('Could not upload rpm %s . Returned: %d', (rpm, p.returncode))

    def _get_affected_hosts(self, change_set, available_host):
        result = set()
        for segment in OVERLAY_ORDER:
            for change_path in change_set:
                result |= set(self._find_matching_hosts(segment, change_path, available_host))

        return result

    def _find_matching_hosts(self, segment, svn_path, available_hosts):
        result = []
        for host in available_hosts:
            for path in segment.get_svn_paths(host):
                if svn_path.startswith(path):
                    result.append(host)
                    break

        return result




