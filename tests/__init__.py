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
    This module contains imports to ensure that the user gets useful feedback
    when executing "python setup.py test" and some system dependencies are missing.
"""

at_least_one_import_failed = False


try:
    import pysvn
except:
    print 'Could not import "pysvn"! Please install it.'
    at_least_one_import_failed = True


try:
    import rpm
except:
    print 'Could not import "rpm"! Please install it.'
    at_least_one_import_failed = True


try:
    import yaml
except:
    print 'Could not import "yaml"! Please install it.'
    at_least_one_import_failed = True


if at_least_one_import_failed:
    exit(1)
