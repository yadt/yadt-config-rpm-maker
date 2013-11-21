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


WORKING_DIRECTORY="$HOME"

# Please modify this if you would like to clone your own fork.
SOURCE_REPOSITORY="https://github.com/yadt/yadt-config-rpm-maker"
SOURCE_DIRECTORY="$WORKING_DIRECTORY/yadt-config-rpm-maker"

SOURCE_RPM="yadt-config-rpm-maker-2.0-1.src.rpm"
RESULT_RPM="yadt-config-rpm-maker-2.0-1.noarch.rpm"

CONFIGURATION_REPOSITORY="$WORKING_DIRECTORY/configuration-repository"
HOOKS_DIRECTORY="${CONFIGURATION_REPOSITORY}/hooks"
SUBVERSION_CONFIGURATION_FILE="${CONFIGURATION_REPOSITORY}/conf/svnserve.conf"

function install_dependencies() {
    # Enable EPEL repository
    wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    sudo rpm -ivH epel-release-6*.rpm

    # install build dependencies
    sudo yum install python-devel python-setuptools python-mock mock -y

    # install dependencies
    sudo yum install subversion rpm-build pysvn python-yaml -y

    # Install git because we need it to clone the repository
    sudo yum install git -y
}


function build_and_install_config_rpm_maker() {
    # clone repository
    git clone ${SOURCE_REPOSITORY} ${SOURCE_DIRECTORY}

    # build source rpm
    cd ${SOURCE_DIRECTORY}
    ./setup.py bdist_rpm --source-only

    # build rpm from source rpm
    cd dist
    sudo mock rebuild ${SOURCE_RPM} -v

    # install built rpm
    cd /var/lib/mock/epel-6-*/result
    sudo rpm -ivH ${RESULT_RPM}
}


function setup_svn_server_with_test_data_and_start_it() {
    svnadmin create ${CONFIGURATION_REPOSITORY}

    # configure svn server
    rm ${SUBVERSION_CONFIGURATION_FILE}
    cp /vagrant/svnserve.conf ${SUBVERSION_CONFIGURATION_FILE}
    cp /vagrant/post-commit ${HOOKS_DIRECTORY}
    chmod 755 ${HOOKS_DIRECTORY}/post-commit
    cp /vagrant/yadt-config-rpm-maker.yaml ${HOOKS_DIRECTORY}

    # Import the test data into the configuration repository
    svn import ${SOURCE_DIRECTORY}/testdata/svn_repo/ file:///${CONFIGURATION_REPOSITORY}/ -m "Initial commit"

    # start subversion server
    svnserve -r ${CONFIGURATION_REPOSITORY} -d
}


install_dependencies
build_and_install_config_rpm_maker
setup_svn_server_with_test_data_and_start_it
