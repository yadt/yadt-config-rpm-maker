#!/usr/bin/env python

from os.path import exists, join
from shutil import copytree
from random import choice, randint
from string import ascii_letters

MAX_LOCATION1_HOSTS = 5
MAX_LOCATION2_HOSTS = 5
MAX_LOCATION3_HOSTS = 20

MIN_LOCATION1_HOSTS = 3
MIN_LOCATION2_HOSTS = 1
MIN_LOCATION3_HOSTS = 5

CONFIGURATION_DIRECTORY = 'testdata/svn_repo/config'

BASE_LOCATION1_HOST = join(CONFIGURATION_DIRECTORY, 'host', 'devweb01')
BASE_LOCATION2_HOST = join(CONFIGURATION_DIRECTORY, 'host', 'tuvweb01')
BASE_LOCATION3_HOST = join(CONFIGURATION_DIRECTORY, 'host', 'berweb01')

LOCATION1_HOST_DESTINATION = '{configuration_directory}/host/dev{abbreviation}%02d'
LOCATION2_HOST_DESTINATION = '{configuration_directory}/host/tuv{abbreviation}%02d'
LOCATION3_HOST_DESTINATION = '{configuration_directory}/host/ber{abbreviation}%02d'


def create_type1_host(abbreviation, host_number):
    dev_format = LOCATION1_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                                   abbreviation=abbreviation)
    host_dir = dev_format % host_number
    if not exists(host_dir):
        copytree(BASE_LOCATION1_HOST, host_dir)


def create_type2_host(abbreviation, host_number):
    tuv_format = LOCATION2_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                                   abbreviation=abbreviation)
    host_dir = tuv_format % host_number
    if not exists(host_dir):
        copytree(BASE_LOCATION2_HOST, host_dir)


def create_type3_host(abbreviation, host_number):
    prod_format = LOCATION3_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                                    abbreviation=abbreviation)
    host_dir = prod_format % host_number
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
    min_count_of_hosts = 1000

    count_of_hosts = 0
    while count_of_hosts < min_count_of_hosts:
        abbreviation = choice(ascii_letters) + choice(ascii_letters) + choice(ascii_letters)
        count_of_hosts += create_type(abbreviation)

    print "Created %d hosts" % count_of_hosts


if __name__ == '__main__':
    main()
