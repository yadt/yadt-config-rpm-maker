yadt-config-rpm-maker [![Build Status](https://travis-ci.org/yadt/yadt-config-rpm-maker.png?branch=master)](https://travis-ci.org/yadt/yadt-config-rpm-maker)
=====================

* Organize the configuration of your datacenter hosts in a subversion repository.
* Run `config-rpm-maker` as post-commit hook of your configuration repository:
  * Builds RPMs containing the configuration for each host.
  * Builds only the configuration RPMs for the affected hosts.
  * Uploads configuration RPMs to a YUM repository.

```bash
Usage:
  config-rpm-maker <repository> <revision> [--debug]
  config-rpm-maker -h | --help
  config-rpm-maker --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --debug       Force DEBUG log level.
```

### Example

```bash
config-rpm-maker file:///foo/bar/svn/test 123
```
Builds all relevant configuration RPMs from the repository at `/foo/bar/svn/test` in revision `123`.

## Features

  * preserves encoding and will not replace tokens within binary files [see TokenReplace.filter_file](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/src/config_rpm_maker/token/tokenreplacer.py#L172)

## Getting Started

To set up `yadt-config-rpm-maker` please have a look at the
[Configuration Documentation](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/CONFIGURATION.md#configuration)

### Example Content for Configuration Repository

The [testdata](https://github.com/yadt/yadt-config-rpm-maker/tree/master/testdata/svn_repo/) directory contains
an example tree for a config repository. It also contains the SPEC file template that is used to
build the config RPMs. Use this as a starting point to setup your own environment.


## Build

### Dependencies

pysvn (a python library for SVN) is required, but not available by usual python means (pip & easy_install).

```bash
sudo yum install pysvn
```

Additional build dependency
```
sudo pip install PyYAML
```

### Development Environment on other Platforms

`yadt-config-rpm-maker` is created for Red Hat Linux Distributions.

But of course you can set up a development environment on other platforms as well:
* [CentOS](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/HOWTO_CentOS.md)
* [OpenSUSE](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/HOWTO_OpenSUSE.md)
* [Debian / Ubuntu](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/HOWTO_Debian.md)

### Linting

```bash
./lint_sources
```
To lint the code we are using flake8.

### Run Tests

```bash
python setup.py test
```

Running a single test file
```bash
PYTHONPATH=src python tests/unittests/configuration_test.py
```

The feedback of the test loader is not helping if the imports fail.
This is a known bug [issue7559](http://bugs.python.org/issue7559).
But there are import checks in [`tests/__init__.py`](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/tests/__init__.py)

Run the checks to see if you have import errors by executing:
```bash
PYTHONPATH=src python tests/__init__.py
```

When you run the integration tests, the yadt-config-rpm-maker will build test RPMs.

### Execution in the working directory

```bash
./config-rpm-maker
```
The `config-rpm-maker` script allows you to execute config-rpm-maker in your working directory.

### Build yadt-config-rpm-maker RPM

```bash
python setup.py bdist_rpm
```

License
=======

yadt-config-rpm-maker
Copyright (C) 2011-2013 Immobilien Scout GmbH

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
