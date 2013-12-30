#!/bin/bash
#
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

set -e

readonly WORKING_DIRECTORY="/home/vagrant"
readonly ALREADY_PROVISIONED="${WORKING_DIRECTORY}/.provisioning_was_successful"

# Please modify this if you would like to clone your own fork.
readonly SOURCE_REPOSITORY="https://github.com/yadt/yadt-config-rpm-maker"
readonly SOURCE_DIRECTORY="${WORKING_DIRECTORY}/yadt-config-rpm-maker"

readonly SOURCE_RPM="yadt-config-rpm-maker-3.2-1.src.rpm"
readonly RESULT_RPM="yadt-config-rpm-maker-3.2-1.noarch.rpm"

readonly CONFIGURATION_REPOSITORY="${WORKING_DIRECTORY}/configuration-repository"
readonly HOOKS_DIRECTORY="${CONFIGURATION_REPOSITORY}/hooks"
readonly SUBVERSION_CONFIGURATION_FILE="${CONFIGURATION_REPOSITORY}/conf/svnserve.conf"

readonly SHARED_DIRECTORY="/vagrant"
