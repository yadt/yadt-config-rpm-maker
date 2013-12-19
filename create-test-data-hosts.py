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


#  Please adapt the TEST_DATA list to generate test data which
#  might look like the host structure in your datacenter.
#
#  First entry explained:
#     a host group type called "app".
#     For example a host group serving a web application.

TEST_DATA = [('app', [ProductionLocation(20),    # 20 hosts in production
                                                 # this will generate host names from: prdapp01 to prdapp20

                      PreProductionLocation(5),  # 5 hosts in pre-production
                                                 # this will generate host names from: preapp01 to preapp05

                      TestLocation(3)]),         # 3 hosts in test
                                                 # this will generate host names from: tstapp01 to tstapp03

             ('cld', [ProductionLocation(3),
                      PreProductionLocation(1),
                      TestLocation(1)]),
             ('mem', [ProductionLocation(15),
                      PreProductionLocation(5),
                      TestLocation(5)]),
             ('bet', [ProductionLocation(15),
                      PreProductionLocation(5),
                      TestLocation(5)]),
             ('bus', [ProductionLocation(15),
                      PreProductionLocation(5),
                      TestLocation(5)]),
             ('cor', [ProductionLocation(99),
                      PreProductionLocation(10),
                      TestLocation(10)]),
             ('cit', [ProductionLocation(15),
                      PreProductionLocation(5),
                      TestLocation(5)]),
             ('def', [ProductionLocation(15),
                      PreProductionLocation(5),
                      TestLocation(5)]),
             ('int', [ProductionLocation(65),
                      PreProductionLocation(45),
                      TestLocation(20)]),
             ('mgo', [ProductionLocation(30),
                      PreProductionLocation(25),
                      TestLocation(56)]),
             ('www', [ProductionLocation(99),
                      PreProductionLocation(20),
                      TestLocation(17)]),
             ('wik', [ProductionLocation(1),
                      PreProductionLocation(1),
                      TestLocation(1)]),
             ('med', [ProductionLocation(80),
                      PreProductionLocation(10),
                      TestLocation(10)]),
             ('dns', [ProductionLocation(10),
                      PreProductionLocation(5),
                      TestLocation(5)]),
             ('dbs', [ProductionLocation(75),
                      PreProductionLocation(50),
                      TestLocation(50)]),
             ('dev', [ProductionLocation(5),
                      PreProductionLocation(36),
                      TestLocation(80)])]

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

    for host_number in range(1, location.hosts_count + 1):
        create_host(type_name, location, host_number)


def create_hosts_for_type(type_name, locations):

    for location in locations:
        create_hosts_in_location(type_name, location)


def main():

    global total_count_of_created_hosts

    for type_name, locations in TEST_DATA:
        create_hosts_for_type(type_name, locations)

    print "Created %d hosts." % total_count_of_created_hosts


if __name__ == '__main__':
    main()
