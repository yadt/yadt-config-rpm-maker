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
CONFIGURATION_REPOSITORY="$WORKING_DIRECTORY/configuration-repository"

# Please modify this if you would like to check out your own fork.
SOURCE_REPOSITORY="https://github.com/aelgru/yadt-config-rpm-maker"
SOURCE_DIRECTORY="$WORKING_DIRECTORY/yadt-config-rpm-maker"

SOURCE_RPM="yadt-config-rpm-maker-2.0-1.src.rpm"
RESULT_RPM="yadt-config-rpm-maker-2.0-1.noarch.rpm"

# Enable EPEL repository
wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
sudo rpm -ivH epel-release-6*.rpm

# Install dependencies
sudo yum install subversion rpm-build mock -y
sudo yum install python-devel python-setuptools pysvn python-yaml python-mock -y

# Install git and clone repository
sudo yum install git -y

git clone ${SOURCE_REPOSITORY} ${SOURCE_DIRECTORY}
cd ${SOURCE_DIRECTORY}

./setup.py bdist_rpm --source-only
cd dist
sudo mock rebuild ${SOURCE_RPM} -v
cd /var/lib/mock/epel-6-*/result
sudo rpm -ivH ${RESULT_RPM}

svnadmin create $HOME/configuration-repository

rm ${CONFIGURATION_REPOSITORY}/conf/svnserve.conf
cp /vagrant/svnserve.conf ${CONFIGURATION_REPOSITORY}/conf/svnserve.conf
cp /vagrant/post-commit ${CONFIGURATION_REPOSITORY}/hooks
chmod 755 ${CONFIGURATION_REPOSITORY}/hooks/post-commit
cp yadt-config-rpm-maker.yaml ${CONFIGURATION_REPOSITORY}/conf

svn import ${SOURCE_DIRECTORY}/testdata/svn_repo/ file:///${CONFIGURATION_REPOSITORY}/ -m "Initial commit"
svnserve -r ${CONFIGURATION_REPOSITORY} -d
