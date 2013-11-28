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
import tempfile

import traceback
import config

from logging import ERROR, FileHandler, Formatter, getLogger
from os.path import exists, join
from Queue import Queue
from shutil import rmtree, move
from threading import Thread

from config_rpm_maker.config import (DEFAULT_ERROR_LOG_URL,
                                     DEFAULT_THREAD_COUNT,
                                     DEFAULT_UPLOAD_CHUNK_SIZE,
                                     ENVIRONMENT_VARIABLE_KEY_KEEP_WORKING_DIRECTORY,
                                     KEY_THREAD_COUNT,
                                     KEY_RPM_UPLOAD_COMMAND,
                                     KEY_TEMPORARY_DIRECTORY,
                                     get_config_viewer_host_dir)

from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.hostrpmbuilder import HostRpmBuilder
from config_rpm_maker.logutils import log_elements_of_list
from config_rpm_maker.profiler import measure_execution_time
from config_rpm_maker.segment import OVERLAY_ORDER

LOGGER = getLogger(__name__)


class BuildHostThread(Thread):

    def __init__(self, revision, host_queue, svn_service_queue, rpm_queue, failed_host_queue, work_dir, name=None, error_logging_handler=None):
        super(BuildHostThread, self).__init__(name=name)
        self.revision = revision
        self.host_queue = host_queue
        self.svn_service_queue = svn_service_queue
        self.rpm_queue = rpm_queue
        self.work_dir = work_dir
        self.failed_host_queue = failed_host_queue
        self.error_logging_handler = error_logging_handler

    def run(self):
        rpms = []
        while not self.host_queue.empty():
            host = self.host_queue.get()
            self.host_queue.task_done()
            try:
                rpms = HostRpmBuilder(thread_name=self.name,
                                      hostname=host,
                                      revision=self.revision,
                                      work_dir=self.work_dir,
                                      svn_service_queue=self.svn_service_queue,
                                      error_logging_handler=self.error_logging_handler).build()
                for rpm in rpms:
                    self.rpm_queue.put(rpm)

            except BaseConfigRpmMakerException as e:
                self.failed_host_queue.put((host, str(e)))

            except Exception:
                self.failed_host_queue.put((host, traceback.format_exc()))

        count_of_rpms = len(rpms)
        if count_of_rpms > 0:
            LOGGER.debug('%s: finished and built %s rpm(s).', self.name, count_of_rpms)
        else:
            LOGGER.debug('%s: finished without building any rpm!', self.name)


class CouldNotBuildSomeRpmsException(BaseConfigRpmMakerException):
    error_info = "Could not build all rpms\n"


class CouldNotUploadRpmsException(BaseConfigRpmMakerException):
    error_info = "Could not upload rpms!\n"


class ConfigurationException(BaseConfigRpmMakerException):
    error_info = "Configuration error, please fix it\n"


class ConfigRpmMaker(object):

    ERROR_MSG = """
------------------------------------------------------------------------
Your commit has been accepted by the SVN server, but due to the errors
that it contains no RPMs have been created.

See %s/%s.txt for details.

Please fix the issues and trigger the RPM creation with a dummy commit.
------------------------------------------------------------------------
"""

    def __init__(self, revision, svn_service):
        self.revision = revision
        self.svn_service = svn_service
        self.temp_dir = config.get(KEY_TEMPORARY_DIRECTORY)
        self._assure_temp_dir_if_set()
        self._create_logger()
        self.work_dir = None

    @measure_execution_time
    def __build_error_msg_and_move_to_public_access(self, revision):
        err_url = config.get('error_log_url', DEFAULT_ERROR_LOG_URL)
        error_msg = self.ERROR_MSG % (err_url, revision)
        for line in error_msg.split('\n'):
            LOGGER.error(line)
        self._move_error_log_for_public_access()
        self._clean_up_work_dir()
        return error_msg

    def build(self):
        LOGGER.info('Working on revision %s', self.revision)
        self.logger.info("Starting with revision %s", self.revision)
        try:
            change_set = self.svn_service.get_change_set(self.revision)
            available_hosts = self.svn_service.get_hosts(self.revision)

            affected_hosts = list(self._get_affected_hosts(change_set, available_hosts))
            if not affected_hosts:
                LOGGER.info("No rpm(s) built. No host affected by change set: %s", str(change_set))
                return

            log_elements_of_list(LOGGER.debug, 'Detected %s affected host(s).', affected_hosts)

            self._prepare_work_dir()
            rpms = self._build_hosts(affected_hosts)
            self._upload_rpms(rpms)
            self._move_configviewer_dirs_to_final_destination(affected_hosts)

        except BaseConfigRpmMakerException, e:
            self.logger.error('Last error during build:\n%s' % str(e))
            self.__build_error_msg_and_move_to_public_access(self.revision)
            raise e

        except Exception, e:
            self.logger.exception('Last error during build:')
            error_msg = self.__build_error_msg_and_move_to_public_access(self.revision)
            raise Exception('Unexpected error occurred, stacktrace will follow.\n%s\n\n%s' % (traceback.format_exc(), error_msg))

        self._clean_up_work_dir()
        return rpms

    def _clean_up_work_dir(self):
        LOGGER.debug('Cleaning up working directory "%s"', self.work_dir)
        if self.work_dir and os.path.exists(self.work_dir) and not self._keep_work_dir():
            shutil.rmtree(self.work_dir)

        if os.path.exists(self.error_log_file):
            LOGGER.debug('Removing error log "%s"', self.error_log_file)
            os.remove(self.error_log_file)

    def _keep_work_dir(self):
        return ENVIRONMENT_VARIABLE_KEY_KEEP_WORKING_DIRECTORY in os.environ and os.environ[ENVIRONMENT_VARIABLE_KEY_KEEP_WORKING_DIRECTORY]

    def _move_error_log_for_public_access(self):
        error_log_dir = os.path.join(config.get('error_log_dir'))
        if error_log_dir:
            if not os.path.exists(error_log_dir):
                os.makedirs(error_log_dir)
            shutil.move(self.error_log_file, os.path.join(error_log_dir, self.revision + '.txt'))

    def _move_configviewer_dirs_to_final_destination(self, hosts):
        LOGGER.info("Updating configviewer data.")

        for host in hosts:
            temp_path = get_config_viewer_host_dir(host, True)
            dest_path = get_config_viewer_host_dir(host)

            if exists(dest_path):
                path_to_revision_file = join(dest_path, "%s.rev" % host)
                with open(path_to_revision_file) as revision_file_content:
                    revision_from_file = int(revision_file_content.read())
                    if revision_from_file > int(self.revision):
                        continue
                rmtree(dest_path)

            move(temp_path, dest_path)

    @measure_execution_time
    def _build_hosts(self, hosts):
        if not hosts:
            LOGGER.warn('Trying to build rpms for hosts, but no hosts given!')
            return

        host_queue = Queue()
        for host in hosts:
            host_queue.put(host)

        failed_host_queue = Queue()
        rpm_queue = Queue()
        svn_service_queue = Queue()
        svn_service_queue.put(self.svn_service)

        thread_count = self._get_thread_count(hosts)
        thread_pool = [BuildHostThread(name='Thread-%d' % i,
                                       revision=self.revision,
                                       svn_service_queue=svn_service_queue,
                                       rpm_queue=rpm_queue,
                                       failed_host_queue=failed_host_queue,
                                       host_queue=host_queue,
                                       work_dir=self.work_dir,
                                       error_logging_handler=self.error_handler) for i in range(thread_count)]

        for thread in thread_pool:
            LOGGER.debug('%s: starting ...', thread.name)
            thread.start()

        for thread in thread_pool:
            thread.join()

        failed_hosts = dict(self._consume_queue(failed_host_queue))
        if failed_hosts:
            failed_hosts_str = ['\n%s:\n\n%s\n\n' % (key, value) for (key, value) in failed_hosts.iteritems()]
            raise CouldNotBuildSomeRpmsException("Could not build config rpm for some host(s): %s" % '\n'.join(failed_hosts_str))

        LOGGER.info("Finished building configuration rpm(s).")
        built_rpms = self._consume_queue(rpm_queue)
        log_elements_of_list(LOGGER.debug, 'Built %s rpm(s).', built_rpms)

        return built_rpms

    @measure_execution_time
    def _upload_rpms(self, rpms):
        rpm_upload_cmd = config.get(KEY_RPM_UPLOAD_COMMAND)
        chunk_size = self._get_chunk_size(rpms)

        if rpm_upload_cmd:
            LOGGER.info("Uploading %s rpm(s).", len(rpms))
            LOGGER.debug('Uploading rpm(s) using command "%s" and chunk_size "%s"', rpm_upload_cmd, chunk_size)

            pos = 0
            while pos < len(rpms):
                rpm_chunk = rpms[pos:pos + chunk_size]
                cmd = '%s %s' % (rpm_upload_cmd, ' '.join(rpm_chunk))
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                if process.returncode:
                    error_message = """Rpm upload failed. Executed command "%s"
stdout: "%s"
stderr: "%s"
return code: %d""" % (cmd, stdout.strip(), stderr.strip(), process.returncode)
                    raise CouldNotUploadRpmsException(error_message)
                pos += chunk_size
        else:
            LOGGER.info("Rpms will not be uploaded since no upload command has been configured.")

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
        thread_count = int(config.get(KEY_THREAD_COUNT, DEFAULT_THREAD_COUNT))
        if thread_count < 0:
            raise ConfigurationException('%s is %s, values <0 are not allowed)' % (KEY_THREAD_COUNT, thread_count))

        if not thread_count or thread_count > len(affected_hosts):
            if not thread_count:
                reason = 'Configuration property "%s" is %s' % (KEY_THREAD_COUNT, thread_count)
            elif thread_count > len(affected_hosts):
                reason = "More threads available than affected hosts"
            thread_count = len(affected_hosts)
            LOGGER.info("%s: using one thread for each affected host." % (reason))
        return thread_count

    def _consume_queue(self, queue):
        items = []

        while not queue.empty():
            item = queue.get()
            queue.task_done()
            items.append(item)

        return items

    def _create_logger(self):
        self.error_log_file = tempfile.mktemp(dir=config.get(KEY_TEMPORARY_DIRECTORY),
                                              prefix='yadt-config-rpm-maker',
                                              suffix='.error.log')
        self.error_handler = FileHandler(self.error_log_file)
        formatter = Formatter(config.LOG_FILE_FORMAT, config.LOG_FILE_DATE_FORMAT)
        self.error_handler.setFormatter(formatter)
        self.error_handler.setLevel(ERROR)

        self.logger = getLogger('fileLogger')
        self.logger.addHandler(self.error_handler)
        self.logger.propagate = False

    def _assure_temp_dir_if_set(self):
        if self.temp_dir and not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def _prepare_work_dir(self):
        LOGGER.debug('Preparing working directory "%s"', self.temp_dir)
        self.work_dir = tempfile.mkdtemp(prefix='yadt-config-rpm-maker.',
                                         suffix='.' + self.revision,
                                         dir=self.temp_dir)

        self.rpm_build_dir = os.path.join(self.work_dir, 'rpmbuild')
        LOGGER.debug('Creating directory structure for rpmbuild in "%s"', self.rpm_build_dir)
        for name in ['tmp', 'RPMS', 'RPMS/x86_64,RPMS/noarch', 'BUILD', 'SRPMS', 'SPECS', 'SOURCES']:
            path = os.path.join(self.rpm_build_dir, name)
            if not os.path.exists(path):
                os.makedirs(path)

    def _get_chunk_size(self, rpms):
        chunk_size_raw = config.get('rpm_upload_chunk_size', DEFAULT_UPLOAD_CHUNK_SIZE)
        try:
            chunk_size = int(chunk_size_raw)
        except ValueError:
            raise ConfigurationException('rpm_upload_chunk_size (%s) is not a legal value (should be int)' % chunk_size_raw)
        if chunk_size < 0:
            raise ConfigurationException("Config param 'rpm_upload_cmd_chunk_size' needs to be greater or equal 0")

        if not chunk_size:
            chunk_size = len(rpms)

        return chunk_size
