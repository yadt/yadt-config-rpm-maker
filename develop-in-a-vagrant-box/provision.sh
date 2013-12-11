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

source "configuration.sh"
source "library.sh"

if [[ -e ${ALREADY_PROVISIONED} ]]; then
  echo ""
  echo "This VM has already been provisioned successfully."
  echo "Exiting without doing anything ..."
  exit 0
fi

install_dependencies
build_and_install_config_rpm_maker
setup_svn_server_with_test_data_and_start_it

echo ""
echo "Touching file ${ALREADY_PROVISIONED}"
echo "to mark this VM as already provisioned."
touch ${ALREADY_PROVISIONED}

echo ""
echo "Provisioning was successful."
