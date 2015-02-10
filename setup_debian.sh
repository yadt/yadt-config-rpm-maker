# Setup script for Ubuntu/Debian
# Run this program to get an initial setup that allows you to run unit tests.

# python-svn is not available via "pip", so we need to install it in the main
# system. To make pysvn available in the virtual environment, it needs to be
# set up with "--system-site-packages".
sudo apt-get install python-svn python-virtualenv python-rpm
virtualenv --system-site-packages venv

# Enter the virtual environment before "pip install ...", so that things get
# installed in venv, not in the main system.
source venv/bin/activate
pip install pyyaml mock

echo "Use 'dpkg-reconfigure dash' to set your system shell to bash, to get the integration tests working."
