import os
import shutil
import subprocess
from config_rpm_maker import segment, config
from config_rpm_maker.dependency import Dependency
from config_rpm_maker.hostResolver import HostResolver
from config_rpm_maker.segment import OVERLAY_ORDER, ALL_SEGEMENTS
from pysvn import ClientError
from datetime import datetime
from config_rpm_maker.token import cli
from config_rpm_maker.token.tokenreplacer import TokenReplacer


class HostRpmBuilder(object):

    def __init__(self, hostname, revision, work_dir, svn_service):
        self.hostname = hostname
        self.revision = revision
        self.work_dir = work_dir
        self.svn_service = svn_service
        self.config_rpm_prefix = config.get('config_rpm_prefix')
        self.host_config_dir = os.path.join(self.work_dir, self.config_rpm_prefix + '-' + self.hostname)
        self.variables_dir = os.path.join(self.host_config_dir, 'VARIABLES')
        self.rpm_requires_path = os.path.join(self.variables_dir, 'RPM_REQUIRES')
        self.rpm_provides_path = os.path.join(self.variables_dir, 'RPM_PROVIDES')
        self.spec_file_path = os.path.join(self.host_config_dir, config.get('config_rpm_prefix') + '-' + self.hostname + '.spec')
        self.config_viewer_host_dir = os.path.join(config.get('config_viewer_dir'), 'hosts', self.hostname + '.new')
        self.rpm_build_dir = os.path.join(self.work_dir, 'rpmbuild')

    def build(self):
        print "Building config rpm for host %s" % (self.hostname)

        if os.path.exists(self.host_config_dir):
            raise Exception("ERROR: '%s' exists already whereas I should be creating it now." % self.host_config_dir)

        os.mkdir(self.host_config_dir)
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

        self._generate_patch_info()

        self._copy_files_for_config_viewer()

        self._filter_tokens_in_rpm_sources()

        self._build_rpm()

    def _build_rpm(self):
        tar_path = self._tar_sources()

        for name in ['tmp','RPMS','RPMS/x86_64,RPMS/noarch','BUILD','SRPMS','SPECS','SOURCES']:
            path = os.path.join(self.rpm_build_dir, name)
            if not os.path.exists(path):
                os.makedirs(path)

        my_env = os.environ.copy()
        my_env['HOME'] = os.path.abspath(self.work_dir)
        rpmbuild_cmd = "rpmbuild --define '_topdir %s' -ta %s" % (os.path.abspath(self.rpm_build_dir), tar_path)
        print "Executing '%s' ..." % rpmbuild_cmd
        p = subprocess.Popen(rpmbuild_cmd, shell=True, env=my_env)
        p.communicate()
        if p.returncode:
            raise Exception("Could not build RPM for host '%s'" % self.hostname)

    def _tar_sources(self):
        output_file = self.host_config_dir + '.tar.gz'
        tar_cmd = 'tar -cvzf "%s" -C %s %s-%s' % (output_file, self.work_dir, self.config_rpm_prefix, self.hostname)
        print "Executing %s ..." % tar_cmd
        p = subprocess.Popen(tar_cmd, shell=True)
        p.communicate()
        if p.returncode:
            raise Exception("Creating tar of config dir failed.")

        return output_file

    def _filter_tokens_in_rpm_sources(self):
        cli.init_logging()
        TokenReplacer.filter_directory(self.host_config_dir, self.variables_dir)


    def _copy_files_for_config_viewer(self):
        if os.path.exists(self.config_viewer_host_dir):
            shutil.rmtree(self.config_viewer_host_dir)

        shutil.copytree(self.host_config_dir, self.config_viewer_host_dir, symlinks=True)
        shutil.copytree(self.variables_dir, os.path.join(self.config_viewer_host_dir, 'VARIABLES'))

    def _generate_patch_info(self):
        variables = filter(lambda name: name != 'SVNLOG' and name != 'OVERLAYING', os.listdir(self.variables_dir))
        variables = [var_name.rjust(40) + ' : ' + self._get_content(os.path.join(self.variables_dir, var_name)) for var_name in variables]
        self._write_file(os.path.join(self.variables_dir, 'VARIABLES'), "\n".join(variables))

    def _save_network_variables(self):
        ip, fqdn, aliases = HostResolver().resolve(self.hostname)
        if not ip:
            if config.get('allow_unknown_hosts'):
                ip = "127.0.0.1"
                fqdn = "localhost.localdomain"
                aliases = ""
            else:
                raise Exception("Could not lookup '%s' with 'getent hosts'" % self.hostname)

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
        logs = [log for svn_path in svn_paths for log in self.svn_service.log(svn_path, self.revision, 5)]
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

        content = "\n".join([overlaying[path].rjust(25) + ' : ' + path for path in sorted(overlaying.keys())])
        self._write_file(os.path.join(self.variables_dir, 'OVERLAYING'), content)



    def _render_log(self, log):
        return """
------------------------------------------------------------------------
r%s | %s | %s
Change set:
   %s

%s""" % (log['revision'].number,
         log['author'],
         datetime.fromtimestamp(log['date']).strftime("%Y-%m-%d %H:%M:%S"),
         "\n   ".join([path['action'] + ' ' + path['path'] for path in log['changed_paths']]),
         log['message']
        )

    def _export_spec_file(self):
        self.svn_service.export(config.get('path_to_spec_file'), self.spec_file_path, self.revision)

    def _overlay_segment(self, segment):
        requires = []
        provides = []
        svn_base_paths = []
        exported_paths = []
        for svn_path in segment.get_svn_paths(self.hostname):
            try:
                exported_paths = self.svn_service.export(svn_path, self.host_config_dir, self.revision)
                svn_base_paths.append(svn_path)
                requires += self._parse_dependency_file(self.rpm_requires_path)
                provides += self._parse_dependency_file(self.rpm_requires_path)
            except ClientError as e:
                pass

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

    def _write_dependency_file(self, dependencies, file_path, collapse_duplicates = False, filter_regex='.*', positive_filter=True):
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

