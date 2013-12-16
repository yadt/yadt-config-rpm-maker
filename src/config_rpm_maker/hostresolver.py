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

import re
import subprocess

from logging import getLogger

from config_rpm_maker import configuration
from config_rpm_maker.logutils import verbose

LOGGER = getLogger(__name__)


class HostResolver(object):

    def resolve(self, hostname):
        dns_searchlist = configuration.get_property('custom_dns_searchlist')

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

        if not configuration.get_property('allow_unknown_hosts'):
            raise Exception("Could not lookup '%s' with 'getent hosts'" % hostname)

        ip = "127.0.0.1"
        fqdn = "localhost.localdomain"
        aliases = ""
        return ip, fqdn, aliases

    def _resolve(self, hostname):
        process = subprocess.Popen("getent hosts " + hostname, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()

        verbose(LOGGER).debug('Resolving host "%s" using gentent: return_code=%d, stdout="%s", stderr="%s"', hostname, process.returncode, stdout.strip(), stderr.strip())
        if process.returncode:
            raise Exception("getent had returncode " + str(process.returncode))

        line = re.sub("\s+", " ", stdout)
        line = line[:-1]
        parts = line.split(' ')
        return parts[0], parts[1], ' '.join(parts[2:])
