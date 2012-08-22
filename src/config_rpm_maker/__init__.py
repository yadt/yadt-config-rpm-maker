from Queue import Queue
import os
import shutil
import subprocess
import tempfile
import logging
import copy
from config_rpm_maker import config
from config_rpm_maker.hostRpmBuilder import HostRpmBuilder
from config_rpm_maker.segment import OVERLAY_ORDER
from threading import Thread

logging.basicConfig(format="%(asctime)s %(levelname)5s [%(name)s] - %(message)s")
logging.getLogger().setLevel(config.get('log_level', 'INFO'))

class BuildHostThread(Thread):

    def __init__(self, revision, host_queue, svn_service_queue, rpm_queue, failed_host_queue, name=None):
        super( BuildHostThread, self).__init__(name=name)
        self.revision = revision
        self.host_queue = host_queue
        self.svn_service_queue = svn_service_queue
        self.rpm_queue = rpm_queue
        self.failed_host_queue = failed_host_queue

    def run(self):
        while not self.host_queue.empty():
            host = self.host_queue.get()
            self.host_queue.task_done()
            try:
                temp_dir = config.get('temp_dir')
                if temp_dir and not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)

                work_dir = tempfile.mkdtemp(prefix='yadt-config-rpm-maker.', suffix='.' + host, dir=temp_dir)
                rpms = HostRpmBuilder(hostname=host, revision=self.revision, work_dir=work_dir, svn_service_queue=self.svn_service_queue).build()
                for rpm in rpms:
                    self.rpm_queue.put(rpm)
            except Exception as e:
                self.failed_host_queue.put((host, e))


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

    def _move_configviewer_dirs_to_final_destination(self, hosts):
        for host in hosts:
            temp_path = HostRpmBuilder.get_config_viewer_host_dir(host, True)
            dest_path = HostRpmBuilder.get_config_viewer_host_dir(host)
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.move(temp_path, dest_path)

    def _build_hosts(self, hosts):
        if not hosts:
            return

        host_queue = Queue()
        for host in hosts:
            host_queue.put(host)

        failed_host_queue = Queue()
        rpm_queue = Queue()
        svn_service_queue = Queue()
        svn_service_queue.put(self.svn_service)

        thread_count = self._get_thread_count(hosts)
        thread_pool = [BuildHostThread(name='host_rpm_thread_%d' % i, revision=self.revision, svn_service_queue=svn_service_queue, rpm_queue=rpm_queue, failed_host_queue=failed_host_queue, host_queue=host_queue) for i in range(thread_count)]




        for thread in thread_pool:
            thread.start()

        for thread in thread_pool:
            thread.join()

        failed_hosts = dict(self._consume_queue(failed_host_queue))
        if failed_hosts:
            raise Exception("For some the host we could not build the config rpm: %s" % str(failed_hosts))

        return self._consume_queue(rpm_queue)

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

    def _get_thread_count(self, affected_hosts):
        thread_count = int(config.get('thread_count', 1))
        if thread_count < 0:
            raise Exception('Thread count is %s, but smaller than zero is not allowed.')

        # thread_count is zero means one thread for affected host
        if not thread_count or thread_count > len(affected_hosts):
            thread_count = len(affected_hosts)
        return thread_count

    def _consume_queue(self, queue):
        items = []
        while not queue.empty():
            item = queue.get()
            queue.task_done()
            items.append(item)

        return items




