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

from pysvn import ClientError
from datetime import datetime
from logging import ERROR, Formatter, FileHandler, getLogger
from os import mkdir, remove, environ
from os.path import exists, abspath
from shutil import rmtree
from subprocess import PIPE, Popen

from config_rpm_maker import configuration
from config_rpm_maker.configuration.properties import (is_no_clean_up_enabled,
                                                       get_log_level,
                                                       get_repo_packages_regex,
                                                       get_config_rpm_prefix,
                                                       is_config_viewer_only_enabled,
                                                       get_path_to_spec_file)
from config_rpm_maker.configuration import build_config_viewer_host_directory
from config_rpm_maker.dependency import Dependency
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.hostresolver import HostResolver
from config_rpm_maker.utilities.logutils import verbose
from config_rpm_maker.segment import OVERLAY_ORDER, ALL_SEGEMENTS
from config_rpm_maker.token.tokenreplacer import TokenReplacer
from config_rpm_maker.utilities.profiler import measure_execution_time


LOGGER = getLogger(__name__)


class CouldNotCreateConfigDirException(BaseConfigRpmMakerException):
    error_info = "Could not create host configuration directory :"


class CouldNotBuildRpmException(BaseConfigRpmMakerException):
    error_info = "Could not create rpm for host :"


class ConfigDirAlreadyExistsException(BaseConfigRpmMakerException):
    error_info = "Config dir already exists: "


class CouldNotTarConfigurationDirectoryException(BaseConfigRpmMakerException):
    error_info = "Could not tar configuration directory: "


class HostRpmBuilder(object):
    def __init__(self, thread_name, hostname, revision, work_dir, svn_service_queue, error_logging_handler=None):
        self.thread_name = thread_name
        self.hostname = hostname
        self.revision = revision
        self.work_dir = work_dir
        self.error_logging_handler = error_logging_handler
        self.output_file_path = os.path.join(self.work_dir, self.hostname + '.output')
        self.error_file_path = os.path.join(self.work_dir, self.hostname + '.error')
        self.logger = self._create_logger()
        self.svn_service_queue = svn_service_queue
        self.config_rpm_prefix = get_config_rpm_prefix()
        self.host_config_dir = os.path.join(self.work_dir, self.config_rpm_prefix + self.hostname)
        self.variables_dir = os.path.join(self.host_config_dir, 'VARIABLES')
        self.rpm_requires_path = os.path.join(self.variables_dir, 'RPM_REQUIRES')
        self.rpm_provides_path = os.path.join(self.variables_dir, 'RPM_PROVIDES')
        self.spec_file_path = os.path.join(self.host_config_dir, self.config_rpm_prefix + self.hostname + '.spec')
        self.config_viewer_host_dir = build_config_viewer_host_directory(hostname, revision=self.revision)
        self.rpm_build_dir = os.path.join(self.work_dir, 'rpmbuild')

    def build(self):
        LOGGER.info('%s: building configuration rpm(s) for host "%s"', self.thread_name, self.hostname)
        self.logger.info("Building config rpm for host %s revision %s", self.hostname, self.revision)

        if exists(self.host_config_dir):
            raise ConfigDirAlreadyExistsException(
                'ERROR: "%s" exists already although I should be creating it now.' % self.host_config_dir)

        try:
            mkdir(self.host_config_dir)
        except Exception as exception:
            raise CouldNotCreateConfigDirException(
                'Could not create host config directory "%s".' % self.host_config_dir, exception)

        overall_requires = []
        overall_provides = []
        overall_svn_paths = []
        overall_exported = {}

        for segment in OVERLAY_ORDER:
            svn_paths, exported_paths, requires, provides = self._overlay_segment(segment)
            overall_exported[segment] = exported_paths
            overall_svn_paths += svn_paths
            overall_requires += requires
            overall_provides += provides

        self.logger.debug("Overall_exported: %s", overall_exported)
        self.logger.info("Overall_requires: %s", overall_requires)
        self.logger.info("Overall_provides: %s", overall_provides)
        self.logger.debug("Overall_svn_paths: %s", overall_svn_paths)

        if not exists(self.variables_dir):
            mkdir(self.variables_dir)

        self._write_dependency_file(overall_requires, self.rpm_requires_path, accumulate_duplicates=False)
        self._write_dependency_file(overall_provides, self.rpm_provides_path, accumulate_duplicates=True)
        self._write_file(os.path.join(self.variables_dir, 'REVISION'), self.revision)

        rpm_name_variable_file = os.path.join(self.variables_dir, 'RPM_NAME')
        self.is_a_group_rpm = exists(rpm_name_variable_file)

        self._save_segment_variables(
            do_not_write_host_segment_variable=self.is_a_group_rpm)

        if self.is_a_group_rpm:
            # Do some preliminary token filtering so that the RPM_NAME is expanded
            try:
                TokenReplacer.filter_directory(os.path.dirname(self.variables_dir),
                                               self.variables_dir,
                                               thread_name=self.thread_name,
                                               skip=False)
            except Exception as e:
                LOGGER.warning("Problem during preliminary filtering of "
                        "variables for group {0}: {1}".format(self.hostname, e))

            self.rpm_name = self._get_content(rpm_name_variable_file).rstrip()
            LOGGER.info('Host {0} will trigger group rpm build with name {1}'.format(self.hostname, self.rpm_name))
            self.spec_file_path = os.path.join(self.host_config_dir, self.config_rpm_prefix + self.rpm_name + '.spec')
            self._write_file(os.path.join(self.variables_dir, 'INSTALL_PROTECTION_DEPENDENCY'), '')
        else:
            self._write_file(rpm_name_variable_file, self.hostname)
            self.rpm_name = self.hostname
            self._write_file(os.path.join(self.variables_dir, 'INSTALL_PROTECTION_DEPENDENCY'), 'hostname-@@@HOST@@@')

        repo_packages_regex = get_repo_packages_regex()
        self._write_dependency_file(overall_requires,
            os.path.join(self.variables_dir, 'RPM_REQUIRES_REPOS'),
            filter_regex=repo_packages_regex)
        self._write_dependency_file(overall_requires,
            os.path.join(self.variables_dir, 'RPM_REQUIRES_NON_REPOS'),
            filter_regex=repo_packages_regex,
            positive_filter=False)

        self._export_spec_file()
        self._save_log_entries_to_variable(overall_svn_paths)
        self._save_overlaying_to_variable(overall_exported)

        self._move_variables_out_of_rpm_dir()
        self._save_file_list()

        self._save_network_variables()

        patch_info = self._generate_patch_info()

        self._copy_files_for_config_viewer()

        # write patch info into variable and config viewer
        self._write_file(os.path.join(self.variables_dir, 'VARIABLES'), patch_info)
        self._write_file(os.path.join(self.config_viewer_host_dir, self.hostname + '.variables'), patch_info)

        self._filter_tokens_in_rpm_sources()

        if not is_config_viewer_only_enabled():
            self._build_rpm_using_rpmbuild()

        LOGGER.debug('%s: writing configviewer data for host "%s"', self.thread_name, self.hostname)
        self._filter_tokens_in_config_viewer()
        self._write_revision_file_for_config_viewer()
        self._write_overlaying_for_config_viewer(overall_exported)

        self._remove_logger_handlers()
        self._clean_up()

        return self._find_rpms()

    def _clean_up(self):
        if is_no_clean_up_enabled():
            verbose(LOGGER).debug('Not cleaning up anything for host "%s"', self.hostname)
            return

        LOGGER.debug('Cleaning up temporary files for host "%s"', self.hostname)

        rmtree(self.variables_dir)
        rmtree(self.host_config_dir)
        remove(self.output_file_path)
        remove(self.error_file_path)

    def _filter_tokens_in_config_viewer(self):

        def configviewer_token_replacer(token, replacement):
            filtered_replacement = replacement.rstrip()
            return '<strong title="%s">%s</strong>' % (token, filtered_replacement)

        token_replacer = TokenReplacer.filter_directory(self.config_viewer_host_dir,
                                                        self.variables_dir,
                                                        html_escape=True,
                                                        replacer_function=configviewer_token_replacer,
                                                        thread_name=self.thread_name)
        tokens_unused = set(token_replacer.token_values.keys()) - token_replacer.token_used
        path_to_unused_variables = os.path.join(self.config_viewer_host_dir, 'unused_variables.txt')
        self._write_file(path_to_unused_variables, '\n'.join(sorted(tokens_unused)))
        token_replacer.filter_file(path_to_unused_variables, html_escape=True)

    def _write_revision_file_for_config_viewer(self):
        revision_file_path = os.path.join(self.config_viewer_host_dir, self.hostname + '.rev')
        self._write_file(revision_file_path, self.revision)

    def _find_rpms(self):
        result = []
        for root, dirs, files in os.walk(os.path.join(self.rpm_build_dir, 'RPMS')):
            for filename in files:
                if filename.startswith(self.config_rpm_prefix + self.rpm_name) and filename.endswith('.rpm'):
                    result.append(os.path.join(root, filename))
        for root, dirs, files in os.walk(os.path.join(self.rpm_build_dir, 'SRPMS')):
            for filename in files:
                if filename.startswith(self.config_rpm_prefix + self.rpm_name) and filename.endswith('.rpm'):
                    result.append(os.path.join(root, filename))
        return result

    @measure_execution_time
    def _build_rpm_using_rpmbuild(self):
        tar_path = self._tar_sources()

        working_environment = environ.copy()
        working_environment['HOME'] = abspath(self.work_dir)
        absolute_rpm_build_path = abspath(self.rpm_build_dir)

        clean_option = "--clean"
        if is_no_clean_up_enabled():
            clean_option = ""

        rpmbuild_cmd = "rpmbuild %s --define '_topdir %s' -ta %s" % (
            clean_option, absolute_rpm_build_path, tar_path)

        LOGGER.debug('%s: building rpms by executing "%s"', self.thread_name, rpmbuild_cmd)
        self.logger.info("Executing '%s' ...", rpmbuild_cmd)

        process = Popen(rpmbuild_cmd,
                        shell=True,
                        env=working_environment,
                        stdout=PIPE,
                        stderr=PIPE)

        stdout, stderr = process.communicate()

        self.logger.info(stdout)
        if stderr:
            self.logger.error(stderr)

        if process.returncode:
            raise CouldNotBuildRpmException(
                'Could not build RPM for host "%s": stdout="%s", stderr="%s"' % (
                    self.hostname, stdout.strip(), stderr.strip()))

    @measure_execution_time
    def _tar_sources(self):
        if self.is_a_group_rpm:
            group_config_dir = os.path.join(self.work_dir, self.config_rpm_prefix + self.rpm_name)
            shutil.move(self.host_config_dir, group_config_dir)
            self.host_config_dir = group_config_dir
            output_file = group_config_dir + '.tar.gz'
            tar_cmd = 'tar -cvzf "%s" -C %s %s' % (
                output_file, self.work_dir, self.config_rpm_prefix + self.rpm_name)
        else:
            output_file = self.host_config_dir + '.tar.gz'
            tar_cmd = 'tar -cvzf "%s" -C %s %s' % (
                output_file, self.work_dir, self.config_rpm_prefix + self.hostname)

        self.logger.debug("Executing %s ...", tar_cmd)
        process = subprocess.Popen(tar_cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode:
            stdout = stdout.strip()
            stderr = stderr.strip()
            raise CouldNotTarConfigurationDirectoryException(
                'Creating tar of config dir failed:\n  stdout="%s",\n  stderr="%s"' % (stdout, stderr))
        return output_file

    @measure_execution_time
    def _filter_tokens_in_rpm_sources(self):
        TokenReplacer.filter_directory(self.host_config_dir, self.variables_dir, thread_name=self.thread_name)

    @measure_execution_time
    def _copy_files_for_config_viewer(self):
        if os.path.exists(self.config_viewer_host_dir):
            shutil.rmtree(self.config_viewer_host_dir)

        shutil.copytree(self.host_config_dir, self.config_viewer_host_dir, symlinks=True)
        shutil.copytree(self.variables_dir, os.path.join(self.config_viewer_host_dir, 'VARIABLES'))

    def _generate_patch_info(self):
        variables = filter(lambda name: name not in ('SVNLOG', 'OVERLAYING'), os.listdir(self.variables_dir))

        info_lines = []
        for variable_name in sorted(variables):
            variable_value = self._get_content(os.path.join(self.variables_dir, variable_name))
            info_lines.append(variable_name.rjust(40) + ' : ' + variable_value)
        return "\n".join(info_lines) + "\n"

    @measure_execution_time
    def _save_network_variables(self):
        ip, fqdn, aliases = HostResolver().resolve(self.hostname)
        self._write_file(os.path.join(self.variables_dir, 'IP'), ip)
        self._write_file(os.path.join(self.variables_dir, 'FQDN'), fqdn)
        self._write_file(os.path.join(self.variables_dir, 'ALIASES'), aliases)

    def _save_segment_variables(self, do_not_write_host_segment_variable):
        if do_not_write_host_segment_variable:
            all_segments = OVERLAY_ORDER[:-1]
        else:
            all_segments = ALL_SEGEMENTS
        for segment in all_segments:
            self._write_file(
                os.path.join(self.variables_dir, segment.get_variable_name()),
                segment.get(self.hostname)[-1])

    def _save_file_list(self):
        with open(os.path.join(self.work_dir, 'filelist.' + self.hostname), 'w') as file_list:
            for root, _, file_names in os.walk(self.host_config_dir):
                for file_name in file_names:
                    file_list.write(os.path.join(root, file_name) + "\n")

    def _move_variables_out_of_rpm_dir(self):
        new_var_dir = os.path.join(self.work_dir, 'VARIABLES.' + self.hostname)
        shutil.move(self.variables_dir, new_var_dir)
        self.variables_dir = new_var_dir

    def _save_log_entries_to_variable(self, svn_paths):
        svn_service = self._get_next_svn_service_from_queue()
        try:
            logs = svn_service.get_logs_for_revision(self.revision)
        except SvnServiceException, exc:
            svn_log = "Could not retrieve log for revision: {0}".format(exc)
        else:
            svn_log = self._render_log(logs[0])
        finally:
            self.svn_service_queue.put(svn_service)

        self._write_file(os.path.join(self.variables_dir, 'SVNLOG'), svn_log)

    def _save_overlaying_to_variable(self, exported_dict):
        overlaying = {}
        for segment in OVERLAY_ORDER:
            for segment_name, path in exported_dict[segment]:
                overlaying[path] = segment_name

        lines = [segment_name.rjust(25) + ' : /' + path
                for path, segment_name in sorted(overlaying.items())]
        content = "\n".join(lines)
        self._write_file(os.path.join(self.variables_dir, 'OVERLAYING'), content)

    def _write_overlaying_for_config_viewer(self, exported_dict):
        overlaying = {}
        for segment in OVERLAY_ORDER:
            for segment_name, path in exported_dict[segment]:
                overlaying[path] = segment_name

        lines = [segment_name + ':/' + path
                for path, segment_name in sorted(overlaying.items())]
        content = "\n".join(lines) + "\n"

        file_name = os.path.join(self.config_viewer_host_dir,
                self.hostname + '.overlaying')
        self._write_file(file_name, content)

    def _render_log(self, log):
        author = log.get("author", "unknown_author")
        return """
------------------------------------------------------------------------
r%s | %s | %s
Change set:
   %s

%s""" % (log['revision'].number,
         author,
         datetime.fromtimestamp(log['date']).strftime("%Y-%m-%d %H:%M:%S"),
         "\n   ".join([path['action'] + ' ' + path['path'] for path in log['changed_paths']]),
         log['message'])

    def _export_spec_file(self):
        svn_service = self._get_next_svn_service_from_queue()
        try:
            svn_service.export(get_path_to_spec_file(), self.spec_file_path, self.revision)
        finally:
            self.svn_service_queue.put(svn_service)

    @measure_execution_time
    def _get_next_svn_service_from_queue(self):
        return self.svn_service_queue.get()

    def _overlay_segment(self, segment):
        requires = []
        provides = []
        svn_base_paths = []
        exported_paths = []
        for svn_path in segment.get_svn_paths(self.hostname):
            svn_service = self._get_next_svn_service_from_queue()
            try:
                new_exported_paths = svn_service.export(svn_path, self.host_config_dir, self.revision)
                exported_paths += new_exported_paths

            except ClientError:
                pass

            finally:
                self.svn_service_queue.put(svn_service)

            svn_base_paths.append(svn_path)
            requires += self._parse_dependency_file(self.rpm_requires_path)
            provides += self._parse_dependency_file(self.rpm_provides_path)

        return svn_base_paths, exported_paths, requires, provides

    def _parse_dependency_file(self, path):
        if os.path.exists(path):
            content = self._get_content(path)
            return [item for line in content.split('\n') for item in line.split(',')]

        return []

    def _write_dependency_file(self, dependencies, file_path, accumulate_duplicates=True, filter_regex='.*', positive_filter=True):
        dep = Dependency(accumulate_dependencies=accumulate_duplicates, filter_regex=filter_regex, positive_filter=positive_filter)
        dep.add(dependencies)
        self._write_file(file_path, str(dep))

    def _write_file(self, file_path, content):
        with open(file_path, 'w') as file_to_write:
            file_to_write.write(content)

    def _get_content(self, path):
        with open(path, 'r') as file_to_read:
            return file_to_read.read()

    def _remove_logger_handlers(self):
        self.logger.removeHandler(self.error_handler)
        self.logger.removeHandler(self.handler)
        self.error_handler.close()
        self.handler.close()

    def _create_logger(self):
        log_level = get_log_level()
        formatter = Formatter(configuration.LOG_FILE_FORMAT, configuration.LOG_FILE_DATE_FORMAT)

        self.handler = FileHandler(self.output_file_path)
        self.handler.setFormatter(formatter)
        self.handler.setLevel(log_level)

        self.error_handler = FileHandler(self.error_file_path)
        self.error_handler.setFormatter(formatter)
        self.error_handler.setLevel(ERROR)

        logger = getLogger(self.hostname)
        logger.addHandler(self.handler)
        logger.addHandler(self.error_handler)
        logger.setLevel(log_level)

        if self.error_logging_handler:
            logger.addHandler(self.error_logging_handler)

        return logger
