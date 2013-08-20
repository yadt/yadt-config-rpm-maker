yadt-config-rpm-maker
=====================

This program is called as a post-commit hook in a config SVN repository.  
It automatically creates configuration RPMs after every commit and puts them in the configured RPM repository.
Only the configuration affected by the commit is rebuilt.

## Build  
### Install build dependencies
pysvn (a python library for SVN) is required, but not available by usual python means (pip & easy_install).
So you need to install it from your distribution repository.
```bash
sudo yum install pysvn
# install additional build dependency
sudo pip install PyYAML
```
### Test the code
When you run the integration tests with `python setup.py test`, the config-rpm-maker will build test RPMs. It is required that
your /bin/sh points to a bash, not a dash!  
[Dash is the default in Ubuntu](https://wiki.ubuntu.com/DashAsBinSh).  
You can set /bin/sh back to bash by running `sudo dpkg-reconfigure dash`

### Build RPM
```bash
python setup.py bdist_rpm
```


## Usage
The code fragment below builds all relevant RPMs for the SVN repository at `/foo/bar/svn/test` in revision 123.
```bash
config-rpm-maker file:///foo/bar/svn/test 123
```

## Example Content for Config SVN

The [testdata](https://github.com/yadt/yadt-config-rpm-maker/tree/master/testdata/svn_repo/) directory contains an example tree for a config SVN. It also contains the SPEC file template that is used to build the config RPMs. Use this as a starting point to setup your own environment.
