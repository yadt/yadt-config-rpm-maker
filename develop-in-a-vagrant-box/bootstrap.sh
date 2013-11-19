#!/bin/bash

wget http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
sudo rpm -ivH epel-release-6*.rpm

sudo yum install git -y
git clone https://github.com/yadt/yadt-config-rpm-maker

yum install python-devel python-setuptools -y
yum install subversion rpm-build install pysvn python-yaml python-mock -y

cd yadt-config-rpm-maker
./setup.py test
