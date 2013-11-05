import re
import subprocess

from config_rpm_maker import config


class HostResolver(object):
    def resolve(self, hostname):
        dns_searchlist = config.get('custom_dns_searchlist')
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

        return None, None, None

    def _resolve(self, hostname):
        p = subprocess.Popen("getent hosts " + hostname, stdout=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        if p.returncode:
            raise Exception("getent had returncode " + str(p.returncode))

        line = re.sub("\s+", " ", out)
        line = line[:-1]
        parts = line.split(' ')
        return parts[0], parts[1], ' '.join(parts[2:])
