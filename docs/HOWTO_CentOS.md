# Developing on Centos 6

## Get the sources

We need `git` to clone the repository
```bash
sudo yum install git -y
```

Clone the yadt-config-rpm-maker repository
```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

## Install Dependencies

To install pysvn we need to [install the RHEL EPEL repository](http://www.rackspace.com/knowledge_center/article/installing-rhel-epel-repo-on-centos-5x-or-6x).
Install everything we need to develop with python

```bash
yum install python-devel python-setuptools -y
```

```bash
yum install subversion rpm-build install pysvn python-yaml python-mock -y
```

## Running Tests

Move into the cloned repository
```bash
cd yadt-config-rpm-maker
```

Execute tests
```bash
./setup.py test
```
