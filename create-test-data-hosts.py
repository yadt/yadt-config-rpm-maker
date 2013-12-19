#!/usr/bin/env python
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

"""
    This script will create more test data by copying the existing host
    directories.
"""

from os.path import exists, join
from shutil import copytree
from random import choice
from string import ascii_letters

DEFAULT_MIN_COUNT_OF_HOSTS = 1000

HOST_DIRECTORY = join(join('testdata', 'svn_repo', 'config'), 'host')

LOCATION1_NAME = 'dev'
LOCATION1_HOSTS_COUNT = 5
LOCATION1_BASE_HOST = 'devweb01'

LOCATION2_NAME = 'tuv'
LOCATION2_HOSTS_COUNT = 5
LOCATION2_BASE_HOST = 'tuvweb01'

LOCATION3_NAME = 'ber'
LOCATION3_HOSTS_COUNT = 20
LOCATION3_BASE_HOST = 'berweb01'

total_count_of_created_hosts = 0


def create_host(type_name, location_name, host_number, base_host_name):

    global total_count_of_created_hosts

    host_name = "%s%s%02d" % (location_name, type_name, host_number)
    destination_host_directory = join(HOST_DIRECTORY, host_name)
    if not exists(destination_host_directory):
        source_host_directory = join(HOST_DIRECTORY, base_host_name)
        copytree(source_host_directory, destination_host_directory)
        total_count_of_created_hosts += 1


def create_hosts_in_location(type_name, location_name, count_of_hosts):

    for host_number in range(1, count_of_hosts):
        create_host(location_name, type_name, host_number)


def create_hosts_for_type(type_name):

    create_hosts_in_location(type_name, LOCATION1_NAME, LOCATION1_HOSTS_COUNT, LOCATION1_BASE_HOST)
    create_hosts_in_location(type_name, LOCATION2_NAME, LOCATION2_HOSTS_COUNT, LOCATION2_BASE_HOST)
    create_hosts_in_location(type_name, LOCATION3_NAME, LOCATION3_HOSTS_COUNT, LOCATION3_BASE_HOST)


def main():

    global total_count_of_created_hosts

    while total_count_of_created_hosts < DEFAULT_MIN_COUNT_OF_HOSTS:
        random_type_name = choice(ascii_letters) + choice(ascii_letters) + choice(ascii_letters)
        create_hosts_for_type(random_type_name)

    print "Created %d hosts." % total_count_of_created_hosts


if __name__ == '__main__':
    main()
