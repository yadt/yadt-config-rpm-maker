#!/usr/bin/env python

from os.path import exists
from shutil import copytree
from random import choice, randint

MAX_DEVELOPMENT_HOSTS = 5
MAX_TEST_HOSTS = 5
MAX_PRODUCTION_HOSTS = 20

MIN_DEVELOPMENT_HOSTS = 3
MIN_TEST_HOSTS = 1
MIN_PRODUCTION_HOSTS = 5

CONFIGURATION_DIRECTORY = 'testdata/svn_repo/config'

BASE_DEVELOPMENT_HOST = '{configuration_directory}/host/devweb01'.format(configuration_directory=CONFIGURATION_DIRECTORY)
BASE_TEST_HOST = '{configuration_directory}/host/tuvweb01'.format(configuration_directory=CONFIGURATION_DIRECTORY)
BASE_PRODUCTION_HOST = '{configuration_directory}/host/berweb01'.format(configuration_directory=CONFIGURATION_DIRECTORY)

DEVELOPMENT_HOST_DESTINATION = '{configuration_directory}/host/dev{abbreviation}%02d'
TEST_HOST_DESTINATION = '{configuration_directory}/host/tuv{abbreviation}%02d'
PRODUCTION_HOST_DESTINATION = '{configuration_directory}/host/ber{abbreviation}%02d'


def create_development_host(abbreviation, host_number):
    dev_format = DEVELOPMENT_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                                     abbreviation=abbreviation)
    host_dir = dev_format % host_number
    if not exists(host_dir):
        copytree(BASE_DEVELOPMENT_HOST, host_dir)


def create_test_host(abbreviation, host_number):
    tuv_format = TEST_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                              abbreviation=abbreviation)
    host_dir = tuv_format % host_number
    if not exists(host_dir):
        copytree(BASE_TEST_HOST, host_dir)


def create_production_host(abbreviation, host_number):
    prod_format = PRODUCTION_HOST_DESTINATION.format(configuration_directory=CONFIGURATION_DIRECTORY,
                                                     abbreviation=abbreviation)
    host_dir = prod_format % host_number
    if not exists(host_dir):
        copytree(BASE_PRODUCTION_HOST, host_dir)


def create_type(abbreviation):
    count_of_development_hosts = randint(MIN_DEVELOPMENT_HOSTS, MAX_DEVELOPMENT_HOSTS)
    for host_number in range(1, count_of_development_hosts):
        create_development_host(abbreviation, host_number)

    count_of_test_hosts = randint(MIN_TEST_HOSTS, MAX_TEST_HOSTS)
    for host_number in range(1, count_of_test_hosts):
        create_test_host(abbreviation, host_number)

    count_of_production_hosts = randint(MIN_PRODUCTION_HOSTS, MAX_PRODUCTION_HOSTS)
    for host_number in range(1, count_of_production_hosts):
        create_production_host(abbreviation, host_number)

    print 'type "%s": %02d dev   %02d tuv   %02d ber' % (abbreviation,
                                                        count_of_development_hosts,
                                                        count_of_test_hosts,
                                                        count_of_production_hosts)

    return count_of_development_hosts + count_of_test_hosts + count_of_production_hosts


if __name__ == '__main__':
    min_count_of_hosts = 1000

    first_character = 'abcdefghijklmnopqrstuvxyz'
    second_character = 'abcdefghijklmnopqrstuvwxyz'
    third_character = 'abcdefghijklmnopqrstuvwxyz'

    count_of_hosts = 0
    while count_of_hosts < min_count_of_hosts:
        abbreviation = choice(first_character) + choice(second_character) + choice(third_character)
        count_of_hosts += create_type(abbreviation)

    print "Created %d hosts" % count_of_hosts
