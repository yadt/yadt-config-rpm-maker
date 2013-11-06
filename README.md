yadt-config-rpm-maker [![Build Status](https://travis-ci.org/yadt/yadt-config-rpm-maker.png?branch=master)](https://travis-ci.org/yadt/yadt-config-rpm-maker)
=====================

* Organize your system configuration in a subversion repository.
* Call `config-rpm-maker` as a post-commit hook.  
* yadt-config-rpm-maker creates RPMs containing the configuration for each host .
* Only the configuration for the affected hosts is built.

## Usage

```bash
config-rpm-maker file:///foo/bar/svn/test 123
```
Builds all relevant RPMs for the SVN repository at `/foo/bar/svn/test` in revision `123`.

## Example Content for Config SVN

The [testdata](https://github.com/yadt/yadt-config-rpm-maker/tree/master/testdata/svn_repo/) directory contains
an example tree for a config SVN. It also contains the SPEC file template that is used to
build the config RPMs. Use this as a starting point to setup your own environment.

## Build

### Dependencies

pysvn (a python library for SVN) is required, but not available by usual python means (pip & easy_install).

#### Red Hat

```bash
sudo yum install pysvn
```

Additional build dependency
```
sudo pip install PyYAML
```

#### Debian

```bash
sudo apt-get install rpm python-rpm python-svn python-yaml
```

### Test the code

When you run the integration tests with `python setup.py test`, the config-rpm-maker will build test RPMs.
It is required that your /bin/sh points to a bash, not a dash!  
[Dash is the default in Ubuntu](https://wiki.ubuntu.com/DashAsBinSh).  
You can set /bin/sh back to bash by running `sudo dpkg-reconfigure dash`

### Build RPM

```bash
python setup.py bdist_rpm
```

License
=======

yadt-config-rpm-maker
Copyright (C) 2012-2013 Immobilien Scout GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
