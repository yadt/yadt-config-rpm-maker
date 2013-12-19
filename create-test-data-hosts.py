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
from random import choice, randint
from string import ascii_letters

DEFAULT_MIN_COUNT_OF_HOSTS = 1000

MAX_LOCATION1_HOSTS = 5
MAX_LOCATION2_HOSTS = 5
MAX_LOCATION3_HOSTS = 20

MIN_LOCATION1_HOSTS = 3
MIN_LOCATION2_HOSTS = 1
MIN_LOCATION3_HOSTS = 5

CONFIGURATION_DIRECTORY = join('testdata', 'svn_repo', 'config')

BASE_LOCATION1_HOST = join(CONFIGURATION_DIRECTORY, 'host', 'devweb01')
BASE_LOCATION2_HOST = join(CONFIGURATION_DIRECTORY, 'host', 'tuvweb01')
BASE_LOCATION3_HOST = join(CONFIGURATION_DIRECTORY, 'host', 'berweb01')

HOST_DIRECTORY = join(CONFIGURATION_DIRECTORY, 'host')

LOCATION1_NAME = 'dev'
LOCATION2_NAME = 'tuv'
LOCATION3_NAME = 'ber'


def create_type1_host(abbreviation, host_number):

    host_name = "%s%s%02d" % (LOCATION1_NAME, abbreviation, host_number)
    host_dir = join(HOST_DIRECTORY, host_name)
    if not exists(host_dir):
        copytree(BASE_LOCATION1_HOST, host_dir)


def create_type2_host(abbreviation, host_number):

    host_name = "%s%s%02d" % (LOCATION2_NAME, abbreviation, host_number)
    host_dir = join(HOST_DIRECTORY, host_name)
    if not exists(host_dir):
        copytree(BASE_LOCATION2_HOST, host_dir)


def create_type3_host(abbreviation, host_number):

    host_name = "%s%s%02d" % (LOCATION3_NAME, abbreviation, host_number)
    host_dir = join(HOST_DIRECTORY, host_name)
    if not exists(host_dir):
        copytree(BASE_LOCATION3_HOST, host_dir)


def create_type(abbreviation):

    count_of_location1_hosts = randint(MIN_LOCATION1_HOSTS, MAX_LOCATION1_HOSTS)
    for host_number in range(1, count_of_location1_hosts):
        create_type1_host(abbreviation, host_number)

    count_of_location2_hosts = randint(MIN_LOCATION2_HOSTS, MAX_LOCATION2_HOSTS)
    for host_number in range(1, count_of_location2_hosts):
        create_type2_host(abbreviation, host_number)

    count_of_location3_hosts = randint(MIN_LOCATION3_HOSTS, MAX_LOCATION3_HOSTS)
    for host_number in range(1, count_of_location3_hosts):
        create_type3_host(abbreviation, host_number)

    print 'type "%s": %02d location1   %02d location2   %02d location3' % (abbreviation,
                                                                           count_of_location1_hosts,
                                                                           count_of_location2_hosts,
                                                                           count_of_location3_hosts)

    return count_of_location1_hosts + count_of_location2_hosts + count_of_location3_hosts


def main():
    count_of_hosts = 0
    while count_of_hosts < DEFAULT_MIN_COUNT_OF_HOSTS:
        abbreviation = choice(ascii_letters) + choice(ascii_letters) + choice(ascii_letters)
        count_of_hosts += create_type(abbreviation)

    print "Created %d hosts" % count_of_hosts


if __name__ == '__main__':
    main()
