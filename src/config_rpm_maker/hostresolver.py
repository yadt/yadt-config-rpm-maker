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

import socket

from logging import getLogger

from config_rpm_maker.utilities.logutils import verbose
from config_rpm_maker.configuration.properties import unknown_hosts_are_allowed, get_custom_dns_search_list

LOGGER = getLogger(__name__)


class HostResolver(object):

    def resolve(self, hostname):
        dns_searchlist = get_custom_dns_search_list()

        if dns_searchlist:
            for dns_suffix in dns_searchlist:
                fqdn_hostname = hostname + '.' + dns_suffix
                try:
                    result = self._resolve(fqdn_hostname)
                    verbose(LOGGER).debug('Host name "%s" resolved to %s', fqdn_hostname, result)
                    return result

                except Exception as exception:
                    verbose(LOGGER).debug('Resolving "%s" resulted in error: %s', fqdn_hostname, str(exception))

        else:
            try:
                result = self._resolve(hostname)
                verbose(LOGGER).debug('Host name "%s" resolved to %s', hostname, result)
                return result
            except Exception as exception:
                verbose(LOGGER).debug('Resolving "%s" resulted in error: %s', hostname, str(exception))

        if not unknown_hosts_are_allowed():
            raise Exception("Could not lookup '%s' with 'getent hosts'" % hostname)

        ip = "127.0.0.1"
        fqdn = "localhost.localdomain"
        aliases = ""
        verbose(LOGGER).debug('Could not resolve "%s" using default values %s', hostname, (ip, fqdn, aliases))
        return ip, fqdn, aliases

    def _resolve(self, hostname):
        host, aliaslist, ipaddrlist = socket.gethostbyname_ex(hostname)
        return ipaddrlist[0], host, ' '.join(aliaslist)
