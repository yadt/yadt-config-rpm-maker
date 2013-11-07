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
    Created on Sep 3, 2012

    Run package as program stub

    @author: sschapiro
"""

from logging import basicConfig, INFO

from config_rpm_maker import main


def initialize_logging():
    """ Basic initialization of logger using configuration """
    basicConfig(format="[%(levelname)s] %(message)s", level=INFO)


if __name__ == "__main__":
    initialize_logging()
    main()
