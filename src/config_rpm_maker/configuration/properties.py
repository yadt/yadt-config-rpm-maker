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

from config_rpm_maker.configuration import ConfigurationProperty

get_config_viewer_host_directory = ConfigurationProperty(key='config_viewer_hosts_dir', default='/tmp')
get_config_rpm_prefix = ConfigurationProperty(key='config_rpm_prefix', default='yadt-config-')
get_custom_dns_search_list = ConfigurationProperty(key='custom_dns_searchlist', default=[])
get_error_log_directory = ConfigurationProperty(key='error_log_dir', default="")
get_error_log_url = ConfigurationProperty(key='error_log_url', default='')
get_log_format = ConfigurationProperty(key="log_format", default="[%(levelname)5s] %(message)s")
get_log_level = ConfigurationProperty(key="log_level", default='DEBUG')
get_max_failed_hosts = ConfigurationProperty(key='max_failed_hosts', default=3)
get_max_file_size = ConfigurationProperty(key='max_file_size', default=100 * 1024)
get_path_to_spec_file = ConfigurationProperty(key='path_to_spec_file', default='default.spec')
get_repo_packages_regex = ConfigurationProperty(key='repo_packages_regex', default='.*-repo.*')
get_rpm_upload_chunk_size = ConfigurationProperty(key='rpm_upload_chunk_size', default=10)
get_rpm_upload_command = ConfigurationProperty(key='rpm_upload_cmd', default=None)
get_svn_path_to_config = ConfigurationProperty(key='svn_path_to_config', default='/config')
get_thread_count = ConfigurationProperty(key='thread_count', default=1)
get_temporary_directory = ConfigurationProperty(key='temp_dir', default='/tmp')

is_config_viewer_only_enabled = ConfigurationProperty(key='config_viewer_only', default=False)
is_no_clean_up_enabled = ConfigurationProperty(key='no_clean_up', default=False)
is_verbose_enabled = ConfigurationProperty(key='verbose', default=False)

unknown_hosts_are_allowed = ConfigurationProperty(key='allow_unknown_hosts', default=True)
