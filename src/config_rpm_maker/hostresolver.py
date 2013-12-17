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

from config_rpm_maker.configuration.properties import are_unknown_hosts_allowed, get_custom_dns_search_list

LOGGER = getLogger(__name__)


class HostResolver(object):

    def resolve(self, hostname):
        dns_searchlist = get_custom_dns_search_list()

        if dns_searchlist:
            for dns_entry in dns_searchlist:
                try:
                    return self._resolve(hostname + '.' + dns_entry)
                except Exception:
                    pass
        else:
            try:
                return self._resolve(hostname)
            except Exception:
                pass

        if not are_unknown_hosts_allowed():
            raise Exception("Could not lookup '%s' with 'getent hosts'" % hostname)

        ip = "127.0.0.1"
        fqdn = "localhost.localdomain"
        aliases = ""
        return ip, fqdn, aliases

    def _resolve(self, hostname):
        host, aliaslist, ipaddrlist = socket.gethostbyname_ex(hostname)
        return ipaddrlist[0], host, ' '.join(aliaslist)
