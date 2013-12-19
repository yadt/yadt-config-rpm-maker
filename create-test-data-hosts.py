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

HOST_DIRECTORY = join('testdata', 'svn_repo', 'config', 'host')


class Location(object):

    def __init__(self, name, base_host, hosts_count):
        self.name = name
        self.base_host = base_host
        self.hosts_count = hosts_count


class ProductionLocation(Location):

    def __init__(self, hosts_count):
        Location.__init__(self, 'prd', 'tuvweb01', hosts_count)


class PreProductionLocation(Location):

    def __init__(self, hosts_count):
        Location.__init__(self, 'pre', 'devweb01', hosts_count)


class TestLocation(Location):

    def __init__(self, hosts_count):
        Location.__init__(self, 'tst', 'berweb01', hosts_count)


LOCATIONS = [ProductionLocation(5),
             PreProductionLocation(5),
             TestLocation(20)]

TYPE_NAMES = ['app', 'fun', 'foo', 'bar', 'srv', 'sta']

total_count_of_created_hosts = 0


def create_host(type_name, location, host_number):

    global total_count_of_created_hosts

    host_name = "%s%s%02d" % (location.name, type_name, host_number)
    destination_host_directory = join(HOST_DIRECTORY, host_name)
    if not exists(destination_host_directory):
        source_host_directory = join(HOST_DIRECTORY, location.base_host)
        copytree(source_host_directory, destination_host_directory)
        total_count_of_created_hosts += 1


def create_hosts_in_location(type_name, location):

    for host_number in range(1, location.hosts_count):
        create_host(type_name, location, host_number)


def create_hosts_for_type(type_name, locations):

    for location in locations:
        create_hosts_in_location(type_name, location)


def main():

    global total_count_of_created_hosts

    for type_name in TYPE_NAMES:
        create_hosts_for_type(type_name, LOCATIONS)

    print "Created %d hosts." % total_count_of_created_hosts


if __name__ == '__main__':
    main()
