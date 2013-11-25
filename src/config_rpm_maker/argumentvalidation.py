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

from logging import getLogger
from urlparse import urlparse

from config_rpm_maker.exitprogram import exit_program
from config_rpm_maker.returncodes import RETURN_CODE_REVISION_IS_NOT_AN_INTEGER, RETURN_CODE_REPOSITORY_URL_INVALID

LOGGER = getLogger(__name__)

VALID_REPOSITORY_URL_SCHEMES = ['http', 'https', 'file', 'ssh', 'svn']


def ensure_valid_revision(revision):
    """ Ensures that the given argument is a valid revision and exits the program if not """

    if not revision.isdigit():
        exit_program('Given revision "%s" is not an integer.' % revision, return_code=RETURN_CODE_REVISION_IS_NOT_AN_INTEGER)

    LOGGER.debug('Accepting "%s" as a valid subversion revision.', revision)
    return revision


def ensure_valid_repository_url(repository_url):
    """ Ensures that the given url is a valid repository url """

    parsed_url = urlparse(repository_url)
    scheme = parsed_url.scheme

    if scheme in VALID_REPOSITORY_URL_SCHEMES:
        LOGGER.debug('Accepting "%s" as a valid repository url.', repository_url)
        return repository_url

    if scheme is '':
        file_uri = 'file://%s' % parsed_url.path
        LOGGER.debug('Accepting "%s" as a valid repository url.', file_uri)
        return file_uri

    return exit_program('Given repository url "%s" is invalid.' % repository_url,
                        return_code=RETURN_CODE_REPOSITORY_URL_INVALID)
