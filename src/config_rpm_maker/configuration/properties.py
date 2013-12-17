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

DEFAULT_ALLOW_UNKNOWN_HOSTS = True
KEY_ALLOW_UNKNOWN_HOSTS = 'allow_unknown_hosts'

KEY_CONFIG_VIEWER_HOSTS_DIR = 'config_viewer_hosts_dir'
DEFAULT_CONFIG_VIEWER_DIR = '/tmp'

DEFAULT_CONFIG_VIEWER_ONLY = False
KEY_CONFIG_VIEWER_ONLY = 'config_viewer_only'

DEFAULT_CONFIG_RPM_PREFIX = 'yadt-config-'
KEY_CONFIG_RPM_PREFIX = 'config_rpm_prefix'

DEFAULT_CUSTOM_DNS_SEARCHLIST = []
KEY_CUSTOM_DNS_SEARCHLIST = 'custom_dns_searchlist'

DEFAULT_ERROR_LOG_URL = ''
KEY_ERROR_LOG_URL = 'error_log_url'

DEFAULT_ERROR_LOG_DIRECTORY = ""
KEY_ERROR_LOG_DIRECTORY = 'error_log_dir'

DEFAULT_MAX_FAILED_HOSTS = 3
KEY_MAX_FAILED_HOSTS = 'max_failed_hosts'

DEFAULT_MAX_FILE_SIZE = 100 * 1024
KEY_MAX_FILE_SIZE = 'max_file_size'

DEFAULT_LOG_FORMAT = "[%(levelname)5s] %(message)s"
KEY_LOG_FORMAT = "log_format"

DEFAULT_LOG_LEVEL = 'DEBUG'
KEY_LOG_LEVEL = "log_level"

DEFAULT_NO_CLEAN_UP = False
KEY_NO_CLEAN_UP = 'no_clean_up'

DEFAULT_PATH_TO_SPEC_FILE = 'default.spec'
KEY_PATH_TO_SPEC_FILE = 'path_to_spec_file'

DEFAULT_REPO_PACKAGES_REGEX = '.*-repo.*'
KEY_REPO_PACKAGES_REGEX = 'repo_packages_regex'

DEFAULT_RPM_UPLOAD_CHUNK_SIZE = 10
KEY_RPM_UPLOAD_CHUNK_SIZE = 'rpm_upload_chunk_size'

DEFAULT_RPM_UPLOAD_COMMAND = None
KEY_RPM_UPLOAD_COMMAND = 'rpm_upload_cmd'

DEFAULT_SVN_PATH_TO_CONFIG = '/config'
KEY_SVN_PATH_TO_CONFIG = 'svn_path_to_config'

DEFAULT_THREAD_COUNT = 1
KEY_THREAD_COUNT = 'thread_count'

DEFAULT_TEMP_DIR = '/tmp'
KEY_TEMP_DIR = 'temp_dir'

DEFAULT_VERBOSE = False
KEY_VERBOSE = 'verbose'

KEY_SVN_PATH_TO_CONFIGURATION = 'svn_path_to_config'

KEY_TEMPORARY_DIRECTORY = "temp_dir"
