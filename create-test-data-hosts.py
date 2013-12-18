#!/usr/bin/env python

from os.path import exists
from shutil import copytree
from random import choice, randint
from string import ascii_letters

MAX_TYPE1_HOSTS = 5
MAX_TYPE2_HOSTS = 5
MAX_TYPE3_HOSTS = 20

MIN_TYPE1_HOSTS = 3
MIN_TYPE2_HOSTS = 1
MIN_TYPE3_HOSTS = 5

CONFIGURATION_DIRECTORY = 'testdata/svn_repo/config'

BASE_TYPE1_HOST = '{configuration_directory}/host/devweb01'.format(configuration_directory=CONFIGURATION_DIRECTORY)
BASE_TYPE2_HOST = '{configuration_directory}/host/tuvweb01'.format(configuration_directory=CONFIGURATION_DIRECTORY)
BASE_TYPE3_HOST = '{configuration_directory}/host/berweb01'.format(configuration_directory=CONFIGURATION_DIRECTORY)

TYPE1_HOST_DESTINATION = '{configuration_directory}/host/dev{abbreviation}%02d'
TYPE2_HOST_DESTINATION = '{configuration_directory}/host/tuv{abbreviation}%02d'
TYPE3_HOST_DESTINATION = '{configuration_directory}/host/ber{abbreviation}%02d'


def create_type1_host(abbreviation, host_number):
    dev_format = TYPE1_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                               abbreviation=abbreviation)
    host_dir = dev_format % host_number
    if not exists(host_dir):
        copytree(BASE_TYPE1_HOST, host_dir)


def create_type2_host(abbreviation, host_number):
    tuv_format = TYPE2_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                               abbreviation=abbreviation)
    host_dir = tuv_format % host_number
    if not exists(host_dir):
        copytree(BASE_TYPE2_HOST, host_dir)


def create_type3_host(abbreviation, host_number):
    prod_format = TYPE3_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                                abbreviation=abbreviation)
    host_dir = prod_format % host_number
    if not exists(host_dir):
        copytree(BASE_TYPE3_HOST, host_dir)


def create_type(abbreviation):

    count_of_development_hosts = randint(MIN_TYPE1_HOSTS, MAX_TYPE1_HOSTS)
    for host_number in range(1, count_of_development_hosts):
        create_type1_host(abbreviation, host_number)

    count_of_test_hosts = randint(MIN_TYPE2_HOSTS, MAX_TYPE2_HOSTS)
    for host_number in range(1, count_of_test_hosts):
        create_type2_host(abbreviation, host_number)

    count_of_production_hosts = randint(MIN_TYPE3_HOSTS, MAX_TYPE3_HOSTS)
    for host_number in range(1, count_of_production_hosts):
        create_type3_host(abbreviation, host_number)

    print 'type "%s": %02d dev   %02d tuv   %02d ber' % (abbreviation,
                                                         count_of_development_hosts,
                                                         count_of_test_hosts,
                                                         count_of_production_hosts)

    return count_of_development_hosts + count_of_test_hosts + count_of_production_hosts


def main():
    min_count_of_hosts = 1000

    count_of_hosts = 0
    while count_of_hosts < min_count_of_hosts:
        abbreviation = choice(ascii_letters) + choice(ascii_letters) + choice(ascii_letters)
        count_of_hosts += create_type(abbreviation)

    print "Created %d hosts" % count_of_hosts


if __name__ == '__main__':
    main()
