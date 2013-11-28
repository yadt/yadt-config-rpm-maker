# Developing on Centos 6

## Get the sources

We need `git` to clone the repository
```bash
sudo yum install git
```

Clone the yadt-config-rpm-maker repository
```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

## Install Dependencies

Install python development dependencies.
```bash
sudo yum install python-devel python-setuptools python-mock
```

Install `yadt-config-rpm-maker` runtime dependencies.
To install pysvn we need to [enable the RHEL EPEL repository](http://www.rackspace.com/knowledge_center/article/installing-rhel-epel-repo-on-centos-5x-or-6x).
```bash
sudo yum install subversion rpm-build install pysvn python-yaml
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
