import re

class HostnameSegment(object):

    def get(self, hostname):
        pass

    def get_svn_prefix(self):
        pass

    def get_svn_paths(self, hostname):
        return [self.get_svn_prefix() + part for part in self.get(hostname)]

    def get_variable_name(self):
        return self.__class__.__name__.upper()

class All(HostnameSegment):

    def get(self, hostname):
        return ['all', ]

    def get_svn_prefix(self):
        return ''

class Typ(HostnameSegment):

    def get(self, hostname):
        typ = hostname[3:6]
        return [typ, ]

    def get_svn_prefix(self):
        return 'typ/'

class Loc(HostnameSegment):

    def get(self, hostname):
        loc = hostname[0:3]
        if loc == 'ber' or loc == 'ham':
            return ['pro', loc, ]
        else:
            return [loc, ]

    def get_svn_prefix(self):
        return 'loc/'

class LocTyp(HostnameSegment):

    def get(self, hostname):
        locs = Loc().get(hostname)
        typs = Typ().get(hostname)

        result = []
        for typ in typs:
            for loc in locs:
                result.append(loc + typ)

        return result

    def get_svn_prefix(self):
        return 'loctyp/'

class Host(HostnameSegment):

    def get(self, hostname):
        return [hostname, ]

    def get_svn_prefix(self):
        return 'host/'

class HostNr(HostnameSegment):

    def get(self, hostname):
        return [hostname[6:], ]

class Short_HostNr(HostnameSegment):

    def get(self, hostname):
        hostNr = hostname[6:]
        short_hostNr = re.sub("^0+", "", hostNr)
        return [short_hostNr, ]

OVERLAY_ORDER = [All(), Typ(), Loc(), LocTyp(), Host()]
ALL_SEGEMENTS = OVERLAY_ORDER + [HostNr(), Short_HostNr()]
