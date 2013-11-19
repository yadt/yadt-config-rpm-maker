#!/bin/bash
set -e

# Enable EPEL repository
wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
sudo rpm -ivH epel-release-6*.rpm

# Install dependencies
sudo yum install subversion rpm-build mock -y
sudo yum install python-devel python-setuptools pysvn python-yaml python-mock -y

# Install git and clone repository
sudo yum install git -y

git clone https://github.com/yadt/yadt-config-rpm-maker $HOME/yadt-config-rpm-maker
cd $HOME/yadt-config-rpm-maker

./setup.py bdist_rpm --source-only
cd dist
sudo mock yadt-config-rpm-maker-2.0-1.src.rpm
