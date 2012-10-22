yadt-config-rpm-maker
=====================

This program is called as a commit hook in a config SVN repository  and automatically creates the necessary config RPMs after every commit and puts them in the configured RPM repository.

## Build  
### Install build dependencies
```bash
# pysvn is not on pypi
sudo yum install pysvn
# create a virtual environment for building
virtualenv ve
# activate the virtual environment
source ve/bin/activate
# install additional build dependency in the virtual environment
pip install PyYAML
```
After building you can disable the virtual environment with 
`deactivate`

### Build RPM
```bash
python setup.py bdist_rpm
```