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

import traceback
import sys

from logging import getLogger

from config_rpm_maker.configRpmMaker import ConfigRpmMaker
from config_rpm_maker.svn import SvnService
from config_rpm_maker.exceptions import BaseConfigRpmMakerException
from config_rpm_maker import config


LOGGER = getLogger()


def main(args=sys.argv[1:]):

    if len(args) != 2:
        LOGGER.error("You need to provide 2 parameters (repo dir, revision). Arguments were %s " % str(args))
        sys.exit(1)

    if not (args[1].isdigit() and int(args[1]) >= 0):
        LOGGER.error("Revision must be a positive integer.\nGiven revision was '%s'" % args[1])
        sys.exit(1)

    try:
        # first use case is post-commit hook. repo dir can be used as file:/// SVN URL
        svn_service = SvnService(
            base_url='file://' + args[0],
            path_to_config=config.get('svn_path_to_config')
        )
        ConfigRpmMaker(revision=args[1], svn_service=svn_service).build()

    except BaseConfigRpmMakerException as e:
        for line in str(e).split("\n"):
            LOGGER.error(line)
        sys.exit(1)

    except Exception:
        traceback.print_exc(5)
        sys.exit(2)
