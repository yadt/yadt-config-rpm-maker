yadt-config-rpm-maker [![Build Status](https://travis-ci.org/yadt/yadt-config-rpm-maker.png?branch=master)](https://travis-ci.org/yadt/yadt-config-rpm-maker)
=====================

* Organize the configuration of your datacenter hosts in a subversion repository.
* Run `config-rpm-maker` as post-commit hook of your configuration repository:
  * Builds RPMs containing the configuration for each host.
  * Builds only the configuration RPMs for the affected hosts.
  * Uploads configuration RPMs to a YUM repository.

```
Usage: config_rpm_maker repo-url revision [options]

Arguments:
  repo-url    URL to subversion repository or absolute path on localhost
  revision    subversion revision for which the configuration rpms are going to be built

Options:
  -h, --help  show this help message and exit
  --debug     force DEBUG log level on console
  --version   show version
```

### Examples

```bash
config-rpm-maker /path-to/your/svn/repository/ 123
```
Builds all relevant configuration RPMs from the repository at `file:///path-to/your/svn/repository/` in revision `123`.

```bash
config-rpm-maker file://host/path-to/your/svn/repository/ 123
```

```bash
config-rpm-maker svn://host/repository/ 123
```


## Features

  * preserves encoding and will not replace tokens within binary files [see TokenReplace.filter_file](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/src/config_rpm_maker/token/tokenreplacer.py#L172)

## Getting Started

Set up a subversion repository. There are several tutorials available in the web.
Some examples:
  * [How To Set Up An SVN Repository In 7 Simple Steps](http://www.civicactions.com/blog/2010/may/25/how_set_svn_repository_7_simple_steps)
  * [Creating and Configuring Your Repository](http://svnbook.red-bean.com/en/1.7/svn.reposadmin.create.html)

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

Additional dependency
```
sudo yum install python-yaml
```

### Developing on other Platforms

`yadt-config-rpm-maker` is created for Red Hat Linux Distributions.

But of course you can set up a development environment on other platforms as well:
* [CentOS](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/HOWTO_CentOS.md)
* [OpenSUSE](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/HOWTO_OpenSUSE.md)
* [Debian / Ubuntu](https://github.com/aelgru/yadt-config-rpm-maker/blob/master/docs/HOWTO_Debian.md)

... or use a [vagrant box](http://www.vagrantup.com/) from [vagrantbox.es](http://vagrantbox.es/) to develop in your
destination distribution.

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

Authors
=======

* [Sebastian Herold](https://github.com/heroldus)
* [Schlomo Schapiro](https://github.com/schlomo)
* [Ingmar Krusch](https://github.com/ingmarkrusch)
* [Maximillien Riehl](https://github.com/mriehl)
* [Michael Gruber](https://github.com/aelgru)
* [Hasan Hosgel](https://github.com/alosdev)
* Konrad Hosemann

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
