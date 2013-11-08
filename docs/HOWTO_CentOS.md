# How to set up a development environment on Centos 6

We need `git` to clone the repository
```bash
sudo yum install git -y
```

Clone the yadt-config-rpm-maker repository
```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

[Enable EPEL repository](http://www.rackspace.com/knowledge_center/article/installing-rhel-epel-repo-on-centos-5x-or-6x)

This is required to install pysvn

Install everything we need to develop with python

```bash
yum install python-devel python-setuptools -y
yum install subversion rpm-build install pysvn python-docopt PyYAML -y
easy_install pip
pip install PyYAML
```

Move into the cloned repository
```bash
cd yadt-config-rpm-maker
```

Execute tests
```bash
./setup.py test
```
