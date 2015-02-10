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
from logging import ERROR, FileHandler, Formatter, getLogger
from os import makedirs, remove
from os.path import exists, join
from Queue import Queue
from shutil import rmtree, move
from threading import Thread
from tempfile import mkdtemp

import configuration
from config_rpm_maker.configuration.properties import (get_error_log_url,
                                                       get_error_log_directory,
                                                       get_max_failed_hosts,
                                                       is_no_clean_up_enabled,
                                                       get_rpm_upload_command,
                                                       get_rpm_upload_chunk_size,
                                                       get_thread_count,
                                                       get_temporary_directory,
                                                       is_verbose_enabled)
from config_rpm_maker.configuration import build_config_viewer_host_directory
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.hostrpmbuilder import HostRpmBuilder
from config_rpm_maker.utilities.logutils import log_elements_of_list
from config_rpm_maker.utilities.profiler import measure_execution_time, log_directories_summary
from config_rpm_maker.segment import OVERLAY_ORDER

LOGGER = getLogger(__name__)


class BuildHostThread(Thread):

    def __init__(self, revision, host_queue, svn_service_queue, rpm_queue, failed_host_queue, work_dir, name=None, error_logging_handler=None):
        super(BuildHostThread, self).__init__(name=name)
        self.revision = revision
        self.host_queue = host_queue
        self.svn_service_queue = svn_service_queue
        self.rpm_queue = rpm_queue
        self.failed_host_queue = failed_host_queue
        self.work_dir = work_dir
        self.error_logging_handler = error_logging_handler

    def _notify_that_host_failed(self, host_name, stack_trace):
        failure_information = (host_name, stack_trace)
        self.failed_host_queue.put(failure_information)
        approximately_count = self.failed_host_queue.qsize()
        LOGGER.error('Build for host "{host_name}" failed. Approximately {count} builds failed.'.format(host_name=host_name,
                                                                                                        count=approximately_count))

        maximum_allowed_failed_hosts = get_max_failed_hosts()
        if approximately_count >= maximum_allowed_failed_hosts:
            LOGGER.error('Stopping to build more hosts since the maximum of %d failed hosts has been reached' % maximum_allowed_failed_hosts)
            self.host_queue.queue.clear()

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
                self._notify_that_host_failed(host, str(e))

            except Exception:
                self._notify_that_host_failed(host, traceback.format_exc())

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
        self.temp_dir = get_temporary_directory()
        self._assure_temp_dir_if_set()
        self.logger = None
        self._create_logger()
        self.work_dir = None

    def __build_error_msg_and_move_to_public_access(self, revision):
        err_url = get_error_log_url()
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
            changed_paths = self.svn_service.get_changed_paths(self.revision)
            if not changed_paths:
                LOGGER.info("No rpm(s) built. No change in configuration directory.")
                return
            available_hosts = self.svn_service.get_hosts(self.revision)

            affected_hosts = list(self._get_affected_hosts(changed_paths, available_hosts))
            if not affected_hosts:
                LOGGER.info("No rpm(s) built. No host affected by change set: %s", str(changed_paths))
                return

            log_elements_of_list(LOGGER.debug, 'Detected %s affected host(s).', affected_hosts)

            self._prepare_work_dir()
            rpms = self._build_hosts(affected_hosts)
            self._upload_rpms(rpms)
            self._move_configviewer_dirs_to_final_destination(affected_hosts)

        except BaseConfigRpmMakerException as exception:
            self.logger.error('Last error during build:\n%s' % str(exception))
            self.__build_error_msg_and_move_to_public_access(self.revision)
            raise exception

        except Exception as exception:
            self.logger.exception('Last error during build:')
            error_msg = self.__build_error_msg_and_move_to_public_access(self.revision)
            raise Exception('Unexpected error occurred, stacktrace will follow.\n%s\n\n%s' % (traceback.format_exc(), error_msg))

        self._clean_up_work_dir()
        return rpms

    def _clean_up_work_dir(self):
        if self._keep_work_dir():
            LOGGER.info('All working data can be found in "{working_directory}"'.format(working_directory=self.work_dir))
        else:
            if self.work_dir and exists(self.work_dir):

                if is_verbose_enabled():
                    log_directories_summary(LOGGER.debug, self.work_dir)

                LOGGER.debug('Cleaning up working directory "%s"', self.work_dir)
                rmtree(self.work_dir)

            if exists(self.error_log_file):
                LOGGER.debug('Removing error log "%s"', self.error_log_file)
                remove(self.error_log_file)

    def _keep_work_dir(self):
        return is_no_clean_up_enabled()

    def _move_error_log_for_public_access(self):
        error_log_dir = os.path.join(get_error_log_directory())
        if error_log_dir:
            if not os.path.exists(error_log_dir):
                os.makedirs(error_log_dir)
            shutil.move(self.error_log_file, os.path.join(error_log_dir, self.revision + '.txt'))

    def _read_integer_from_file(self, path):

        with open(path) as file_which_contains_integer:
            integer_from_file = int(file_which_contains_integer.read())

        return integer_from_file

    def _move_configviewer_dirs_to_final_destination(self, hosts):
        LOGGER.info("Updating configviewer data.")

        for host in hosts:
            temp_path = build_config_viewer_host_directory(host, revision=self.revision)
            dest_path = build_config_viewer_host_directory(host)

            if exists(dest_path):
                path_to_revision_file = join(dest_path, "%s.rev" % host)
                revision_from_file = self._read_integer_from_file(path_to_revision_file)

                if revision_from_file > int(self.revision):
                    LOGGER.debug('Will not update configviewer data for host "%s" since the current revision file contains revision %d which is higher than %s', host, revision_from_file, self.revision)
                    rmtree(temp_path)
                    continue

                rmtree(dest_path)

            LOGGER.debug('Updating configviewer data for host "%s"', host)
            move(temp_path, dest_path)


    def _build_hosts(self, hosts):
        if not hosts:
            LOGGER.warn('Trying to build rpms for hosts, but no hosts given!')
            return

        host_queue = Queue()
        for host in hosts:
            host_queue.put(host)

        rpm_queue = Queue()
        svn_service_queue = Queue()
        failed_host_queue = Queue()
        svn_service_queue.put(self.svn_service)

        thread_count = self._get_thread_count(hosts)
        thread_pool = [BuildHostThread(name='Thread-%d' % i,
                                       revision=self.revision,
                                       svn_service_queue=svn_service_queue,
                                       rpm_queue=rpm_queue,
                                       host_queue=host_queue,
                                       failed_host_queue=failed_host_queue,
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
        rpm_upload_cmd = get_rpm_upload_command()
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
                    error_message = 'Rpm upload failed with exit code %s. Executed command "%s"\n' % (process.returncode, cmd)
                    if stdout:
                        error_message += 'stdout: "%s"\n' % stdout.strip()
                    if stderr:
                        error_message += 'stderr: "%s"\n' % stderr.strip()
                    raise CouldNotUploadRpmsException(error_message)
                pos += chunk_size
        else:
            LOGGER.info("Rpms will not be uploaded since no upload command has been configured.")

    def _get_affected_hosts(self, changed_paths, available_host):
        result = set()
        for segment in OVERLAY_ORDER:
            for changed_path in changed_paths:
                result |= set(self._find_matching_hosts(segment, changed_path, available_host))

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
        thread_count = int(get_thread_count())
        if thread_count < 0:
            raise ConfigurationException('%s is %s, values <0 are not allowed)' % (get_thread_count, thread_count))

        if not thread_count or thread_count > len(affected_hosts):
            if not thread_count:
                reason = 'Configuration property "%s" is %s' % (get_thread_count, thread_count)
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
        self.error_log_file = tempfile.mktemp(dir=get_temporary_directory(),
                                              prefix='yadt-config-rpm-maker.',
                                              suffix='.revision-%s.error.log' % self.revision)
        self.error_handler = FileHandler(self.error_log_file)
        formatter = Formatter(configuration.LOG_FILE_FORMAT, configuration.LOG_FILE_DATE_FORMAT)
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
        self.work_dir = mkdtemp(prefix='yadt-config-rpm-maker.',
                                suffix='.' + self.revision,
                                dir=self.temp_dir)

        self.rpm_build_dir = join(self.work_dir, 'rpmbuild')
        LOGGER.debug('Creating directory structure for rpmbuild in "%s"', self.rpm_build_dir)
        for name in ['tmp', 'RPMS', 'RPMS/x86_64', 'RPMS/noarch', 'BUILD', 'BUILDROOT', 'SRPMS', 'SPECS', 'SOURCES']:
            path = join(self.rpm_build_dir, name)
            if not exists(path):
                makedirs(path)

    def _get_chunk_size(self, rpms):
        chunk_size_raw = get_rpm_upload_chunk_size()
        try:
            chunk_size = int(chunk_size_raw)
        except ValueError:
            raise ConfigurationException('rpm_upload_chunk_size (%s) is not a legal value (should be int)' % chunk_size_raw)
        if chunk_size < 0:
            raise ConfigurationException("Config param 'rpm_upload_cmd_chunk_size' needs to be greater or equal 0")

        if not chunk_size:
            chunk_size = len(rpms)

        return chunk_size
