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

from config_rpm_maker import config
from config_rpm_maker.dependency import Dependency
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker.hostResolver import HostResolver
from config_rpm_maker.segment import OVERLAY_ORDER, ALL_SEGEMENTS
from config_rpm_maker.token.tokenreplacer import TokenReplacer


LOGGER = getLogger(__name__)


class CouldNotCreateConfigDirException(BaseConfigRpmMakerException):
    error_info = "Could not create host configuration directory :"


class CouldNotBuildRpmException(BaseConfigRpmMakerException):
    error_info = "Could not create rpm for host :"


class HostRpmBuilder(object):
    @classmethod
    def get_config_viewer_host_dir(cls, hostname, temp=False):
        path = os.path.join(config.get('config_viewer_dir'), 'hosts', hostname)

        if temp:
            path += '.new'

        return path

    def __init__(self, hostname, revision, work_dir, svn_service_queue, error_logging_handler=None):
        self.hostname = hostname
        self.revision = revision
        self.work_dir = work_dir
        self.error_logging_handler = error_logging_handler
        self.logger = self._create_logger()
        self.svn_service_queue = svn_service_queue
        self.config_rpm_prefix = config.get('config_rpm_prefix')
        self.host_config_dir = os.path.join(self.work_dir, self.config_rpm_prefix + self.hostname)
        self.variables_dir = os.path.join(self.host_config_dir, 'VARIABLES')
        self.rpm_requires_path = os.path.join(self.variables_dir, 'RPM_REQUIRES')
        self.rpm_provides_path = os.path.join(self.variables_dir, 'RPM_PROVIDES')
        self.spec_file_path = os.path.join(self.host_config_dir, self.config_rpm_prefix + self.hostname + '.spec')
        self.config_viewer_host_dir = HostRpmBuilder.get_config_viewer_host_dir(hostname, True)
        self.rpm_build_dir = os.path.join(self.work_dir, 'rpmbuild')

    def build(self):
        LOGGER.info('Building configuration rpm(s) for host "%s"', self.hostname)
        self.logger.info("Building config rpm for host %s revision %s", self.hostname, self.revision)

        if os.path.exists(self.host_config_dir):
            raise Exception('ERROR: "%s" exists already whereas I should be creating it now.' % self.host_config_dir)

        try:
            os.mkdir(self.host_config_dir)
        except Exception as e:
            raise CouldNotCreateConfigDirException("Could not create host config directory '%s' : %s" % self.host_config_dir, e)

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

        self.logger.debug("Overall_exported: %s", str(overall_exported))
        self.logger.info("Overall_requires: %s", str(overall_requires))
        self.logger.info("Overall_provides: %s", str(overall_provides))
        self.logger.debug("Overall_svn_paths: %s", str(overall_svn_paths))

        if not os.path.exists(self.variables_dir):
            os.mkdir(self.variables_dir)

        self._write_dependency_file(overall_requires, self.rpm_requires_path, collapse_duplicates=True)
        self._write_dependency_file(overall_provides, self.rpm_provides_path, False)
        self._write_file(os.path.join(self.variables_dir, 'REVISION'), self.revision)

        repo_packages_regex = config.get('repo_packages_regex')
        if repo_packages_regex:
            self._write_dependency_file(overall_requires, os.path.join(self.variables_dir, 'RPM_REQUIRES_REPOS'), filter_regex=repo_packages_regex)
            self._write_dependency_file(overall_requires, os.path.join(self.variables_dir, 'RPM_REQUIRES_NON_REPOS'), filter_regex=repo_packages_regex, positive_filter=False)

        self._export_spec_file()
        self._save_log_entries_to_variable(overall_svn_paths)
        self._save_overlaying_to_variable(overall_exported)

        self._move_variables_out_of_rpm_dir()
        self._save_file_list()

        self._save_segment_variables()
        self._save_network_variables()

        patch_info = self._generate_patch_info()

        self._copy_files_for_config_viewer()

        # write patch info into variable and config viewer
        self._write_file(os.path.join(self.variables_dir, 'VARIABLES'), patch_info)
        self._write_file(os.path.join(self.config_viewer_host_dir, self.hostname + '.variables'), patch_info)

        self._filter_tokens_in_rpm_sources()
        self._build_rpm()

        LOGGER.debug('Writing configviewer data for host "%s"', self.hostname)
        self._filter_tokens_in_config_viewer()
        self._write_revision_file_for_config_viewer()
        self._write_overlaying_for_config_viewer(overall_exported)

        self._remove_logger_handlers()

        return self._find_rpms()

    def _filter_tokens_in_config_viewer(self):

        def configviewer_token_replacer(token, replacement):
            filtered_replacement = replacement.rstrip()
            return '<strong title="%s">%s</strong>' % (token, filtered_replacement)

        token_replacer = TokenReplacer.filter_directory(self.config_viewer_host_dir, self.variables_dir, html_escape=True, replacer_function=configviewer_token_replacer)
        tokens_unused = set(token_replacer.token_values.keys()) - token_replacer.token_used
        path_to_unused_variables = os.path.join(self.config_viewer_host_dir, 'unused_variables.txt')
        self._write_file(path_to_unused_variables, '\n'.join(sorted(tokens_unused)))
        token_replacer.filter_file(path_to_unused_variables, html_escape=True)

    def _write_revision_file_for_config_viewer(self):
        self._write_file(os.path.join(self.config_viewer_host_dir, self.hostname + '.rev'), self.revision)

    def _find_rpms(self):
        result = []
        for root, dirs, files in os.walk(os.path.join(self.rpm_build_dir, 'RPMS')):
            for filename in files:
                if filename.startswith(self.config_rpm_prefix + self.hostname) and filename.endswith('.rpm'):
                    result.append(os.path.join(root, filename))
        for root, dirs, files in os.walk(os.path.join(self.rpm_build_dir, 'SRPMS')):
            for filename in files:
                if filename.startswith(self.config_rpm_prefix + self.hostname) and filename.endswith('.rpm'):
                    result.append(os.path.join(root, filename))
        return result

    def _build_rpm(self):
        tar_path = self._tar_sources()

        working_environment = os.environ.copy()
        working_environment['HOME'] = os.path.abspath(self.work_dir)
        rpmbuild_cmd = "rpmbuild --define '_topdir %s' -ta %s" % (os.path.abspath(self.rpm_build_dir), tar_path)

        LOGGER.debug('Building rpms by executing "%s"', rpmbuild_cmd)
        self.logger.info("Executing '%s' ...", rpmbuild_cmd)

        p = subprocess.Popen(rpmbuild_cmd,
                             shell=True,
                             env=working_environment,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        stdout, stderr = p.communicate()

        self.logger.info(stdout)
        if stderr:
            self.logger.error(stderr)

        if p.returncode:
            raise CouldNotBuildRpmException('Could not build RPM for host "%s": stdout="%s", stderr="%s"' % (self.hostname, stdout.strip(), stderr.strip()))

    def _tar_sources(self):
        output_file = self.host_config_dir + '.tar.gz'
        tar_cmd = 'tar -cvzf "%s" -C %s %s' % (output_file, self.work_dir, self.config_rpm_prefix + self.hostname)
        self.logger.debug("Executing %s ...", tar_cmd)
        p = subprocess.Popen(tar_cmd,
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode:
            raise Exception('Creating tar of config dir failed:\n  stdout="%s",\n  stderr="%s"' % (stdout, stderr))
        return output_file

    def _filter_tokens_in_rpm_sources(self):
        TokenReplacer.filter_directory(self.host_config_dir, self.variables_dir)

    def _copy_files_for_config_viewer(self):
        if os.path.exists(self.config_viewer_host_dir):
            shutil.rmtree(self.config_viewer_host_dir)

        shutil.copytree(self.host_config_dir, self.config_viewer_host_dir, symlinks=True)
        shutil.copytree(self.variables_dir, os.path.join(self.config_viewer_host_dir, 'VARIABLES'))

    def _generate_patch_info(self):
        variables = filter(lambda name: name != 'SVNLOG' and name != 'OVERLAYING', os.listdir(self.variables_dir))
        variables = sorted(variables)
        variables = [var_name.rjust(40) + ' : ' + self._get_content(os.path.join(self.variables_dir, var_name)) for var_name in variables]
        return "\n".join(variables) + "\n"

    def _save_network_variables(self):
        ip, fqdn, aliases = HostResolver().resolve(self.hostname)
        self._write_file(os.path.join(self.variables_dir, 'IP'), ip)
        self._write_file(os.path.join(self.variables_dir, 'FQDN'), fqdn)
        self._write_file(os.path.join(self.variables_dir, 'ALIASES'), aliases)

    def _save_segment_variables(self):
        for segment in ALL_SEGEMENTS:
            self._write_file(os.path.join(self.variables_dir, segment.get_variable_name()), segment.get(self.hostname)[-1])

    def _save_file_list(self):
        f = open(os.path.join(self.work_dir, 'filelist.' + self.hostname), 'w')
        try:
            for root, dirs, files in os.walk(self.host_config_dir):
                for file in files:
                    f.write(os.path.join(root, file))
                    f.write("\n")
        finally:
            f.close()

    def _move_variables_out_of_rpm_dir(self):
        new_var_dir = os.path.join(self.work_dir, 'VARIABLES.' + self.hostname)
        shutil.move(self.variables_dir, new_var_dir)
        self.variables_dir = new_var_dir

    def _save_log_entries_to_variable(self, svn_paths):
        svn_service = self.svn_service_queue.get()
        logs = []
        try:
            for svn_path in svn_paths:
                for log_entry in svn_service.log(svn_path, self.revision, 5):
                    logs.append(log_entry)
        except ClientError:
            pass
        finally:
            self.svn_service_queue.put(svn_service)
            self.svn_service_queue.task_done()

        logs = sorted(logs, key=lambda log: log['revision'].number, reverse=True)
        logs = logs[:5]
        logs_text = [self._render_log(log) for log in logs]
        svn_log = "\n".join(logs_text)
        self._write_file(os.path.join(self.variables_dir, 'SVNLOG'), svn_log)

    def _save_overlaying_to_variable(self, exported_dict):
        overlaying = {}
        for segment in OVERLAY_ORDER:
            for path_tuple in exported_dict[segment]:
                overlaying[path_tuple[1]] = path_tuple[0]

        content = "\n".join([overlaying[path].rjust(25) + ' : /' + path for path in sorted(overlaying.keys())])
        self._write_file(os.path.join(self.variables_dir, 'OVERLAYING'), content)

    def _write_overlaying_for_config_viewer(self, exported_dict):
        overlaying = {}
        for segment in OVERLAY_ORDER:
            for path_tuple in exported_dict[segment]:
                overlaying[path_tuple[1]] = path_tuple[0]

        content = "\n".join([overlaying[path] + ':/' + path for path in sorted(overlaying.keys())])
        self._write_file(os.path.join(self.config_viewer_host_dir, self.hostname + '.overlaying'), content + "\n")

    def _render_log(self, log):
        if 'author' in log:
            author = log['author']
        else:
            author = 'unknown_author'
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
        svn_service = self.svn_service_queue.get()
        try:
            svn_service.export(config.get('path_to_spec_file'), self.spec_file_path, self.revision)
        finally:
            self.svn_service_queue.put(svn_service)
            self.svn_service_queue.task_done()

    def _overlay_segment(self, segment):
        requires = []
        provides = []
        svn_base_paths = []
        exported_paths = []
        for svn_path in segment.get_svn_paths(self.hostname):
            svn_service = self.svn_service_queue.get()
            try:
                new_exported_paths = svn_service.export(svn_path, self.host_config_dir, self.revision)
                exported_paths += new_exported_paths

            except ClientError:
                pass
            finally:
                self.svn_service_queue.put(svn_service)
                self.svn_service_queue.task_done()
            svn_base_paths.append(svn_path)
            requires += self._parse_dependency_file(self.rpm_requires_path)
            provides += self._parse_dependency_file(self.rpm_provides_path)

        return svn_base_paths, exported_paths, requires, provides

    def _parse_dependency_file(self, path):
        if os.path.exists(path):
            f = open(path)
            try:
                content = f.read()
                return [item for line in content.split('\n') for item in line.split(',')]
            finally:
                f.close()

        return []

    def _write_dependency_file(self, dependencies, file_path, collapse_duplicates=False, filter_regex='.*', positive_filter=True):
        dep = Dependency(collapseDependencies=collapse_duplicates, filterRegex=filter_regex, positiveFilter=positive_filter)
        dep.add(dependencies)
        self._write_file(file_path, dep.__repr__())

    def _write_file(self, file_path, content):
        f = open(file_path, 'w')
        try:
            f.write(content)
        finally:
            f.close()

    def _get_content(self, path):
        f = open(path, 'r')
        try:
            return f.read()
        finally:
            f.close()

    def _remove_logger_handlers(self):
        self.logger.removeHandler(self.error_handler)
        self.logger.removeHandler(self.handler)
        self.error_handler.close()
        self.handler.close()

    def _create_logger(self):
        log_level = config.get_log_level()
        formatter = Formatter(config.LOG_FILE_FORMAT, config.LOG_FILE_DATE_FORMAT)

        self.handler = FileHandler(os.path.join(self.work_dir, self.hostname + '.output'))
        self.handler.setFormatter(formatter)
        self.handler.setLevel(log_level)

        self.error_handler = FileHandler(os.path.join(self.work_dir, self.hostname + '.error'))
        self.error_handler.setFormatter(formatter)
        self.error_handler.setLevel(ERROR)

        logger = getLogger(self.hostname)
        logger.addHandler(self.handler)
        logger.addHandler(self.error_handler)
        logger.setLevel(log_level)

        if self.error_logging_handler:
            logger.addHandler(self.error_logging_handler)

        return logger
