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

KEY_ALLOW_UNKNOWN_HOSTS = ConfigurationProperty(key='allow_unknown_hosts', default=True)
KEY_CONFIG_VIEWER_HOSTS_DIR = ConfigurationProperty(key='config_viewer_hosts_dir', default='/tmp')
KEY_CONFIG_VIEWER_ONLY = ConfigurationProperty(key='config_viewer_only', default=False)
KEY_CONFIG_RPM_PREFIX = ConfigurationProperty(key='config_rpm_prefix', default='yadt-config-')
KEY_CUSTOM_DNS_SEARCHLIST = ConfigurationProperty(key='custom_dns_searchlist', default=[])
KEY_ERROR_LOG_URL = ConfigurationProperty(key='error_log_url', default='')
KEY_ERROR_LOG_DIRECTORY = ConfigurationProperty(key='error_log_dir', default="")
KEY_MAX_FAILED_HOSTS = ConfigurationProperty(key='max_failed_hosts', default=3)
KEY_MAX_FILE_SIZE = ConfigurationProperty(key='max_file_size', default=100 * 1024)
KEY_LOG_FORMAT = ConfigurationProperty(key="log_format", default="[%(levelname)5s] %(message)s")
KEY_LOG_LEVEL = ConfigurationProperty(key="log_level", default='DEBUG')
KEY_NO_CLEAN_UP = ConfigurationProperty(key='no_clean_up', default=False)
KEY_PATH_TO_SPEC_FILE = ConfigurationProperty(key='path_to_spec_file', default='default.spec')
KEY_REPO_PACKAGES_REGEX = ConfigurationProperty(key='repo_packages_regex', default='.*-repo.*')
KEY_RPM_UPLOAD_CHUNK_SIZE = ConfigurationProperty(key='rpm_upload_chunk_size', default=10)
KEY_RPM_UPLOAD_COMMAND = ConfigurationProperty(key='rpm_upload_cmd', default=None)
KEY_SVN_PATH_TO_CONFIG = ConfigurationProperty(key='svn_path_to_config', default='/config')
KEY_THREAD_COUNT = ConfigurationProperty(key='thread_count', default=1)
KEY_TEMPORARY_DIRECTORY = ConfigurationProperty(key='temp_dir', default='/tmp')
KEY_VERBOSE = ConfigurationProperty(key='verbose', default=False)
