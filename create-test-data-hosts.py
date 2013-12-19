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

LOCATION1_HOSTS_COUNT = 5
LOCATION2_HOSTS_COUNT = 5
LOCATION3_HOSTS_COUNT = 20

CONFIGURATION_DIRECTORY = join('testdata', 'svn_repo', 'config')

HOST_DIRECTORY = join(CONFIGURATION_DIRECTORY, 'host')

BASE_LOCATION1_HOST = 'devweb01'
BASE_LOCATION2_HOST = 'tuvweb01'
BASE_LOCATION3_HOST = 'berweb01'

LOCATION1_NAME = 'dev'
LOCATION2_NAME = 'tuv'
LOCATION3_NAME = 'ber'


total_count_of_created_hosts = 0


def create_host(location_name, abbreviation, host_number, base_host_name):

    global total_count_of_created_hosts

    host_name = "%s%s%02d" % (location_name, abbreviation, host_number)
    destination_host_directory = join(HOST_DIRECTORY, host_name)
    if not exists(destination_host_directory):
        source_host_directory = join(HOST_DIRECTORY, base_host_name)
        copytree(source_host_directory, destination_host_directory)
        total_count_of_created_hosts += 1


def create_hosts_in_location(location_name, type_name, count_of_hosts):

    for host_number in range(1, count_of_hosts):
        create_host(location_name, type_name, host_number)


def create_hosts_for_type(type_name):

    create_hosts_in_location(LOCATION1_NAME, type_name, LOCATION1_HOSTS_COUNT, BASE_LOCATION1_HOST)
    create_hosts_in_location(LOCATION2_NAME, type_name, LOCATION2_HOSTS_COUNT, BASE_LOCATION2_HOST)
    create_hosts_in_location(LOCATION3_NAME, type_name, LOCATION3_HOSTS_COUNT, BASE_LOCATION3_HOST)


def main():

    global total_count_of_created_hosts

    while total_count_of_created_hosts < DEFAULT_MIN_COUNT_OF_HOSTS:
        random_type_name = choice(ascii_letters) + choice(ascii_letters) + choice(ascii_letters)
        create_hosts_for_type(random_type_name)

    print "Created %d hosts." % total_count_of_created_hosts


if __name__ == '__main__':
    main()
