yadt-config-rpm-maker
=====================

This program is called as a commit hook in a config SVN repository  and automatically creates the necessary config RPMs after every commit and puts them in the configured RPM repository.

## Build  
### Install build dependencies
pysvn (a python library for SVN) is required, but not available by usual python means (pip & easy_install).
So you need to install it from your distribution repository.
```bash
sudo yum install pysvn
```
It is considered good practice to install all dependencies available via pip & easy_install in a
[virtual environment](http://pypi.python.org/pypi/virtualenv) so that your development dependencies are isolated from the system-wide dependencies.
```bash
# create a virtual environment for building
virtualenv ve
# activate the virtual environment
source ve/bin/activate
# install additional build dependency in the virtual environment
pip install PyYAML
```


### Build RPM in the virtual environment
```bash
python setup.py bdist_rpm
```
After building you can disable the virtual environment with 
`deactivate`

## Usage
The code fragment below builds all relevant RPMs for the SVN repository at `/foo/bar/svn/test` in revision 123.
```bash
config-rpm-maker file:///foo/bar/svn/test 123
```