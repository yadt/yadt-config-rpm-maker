# Developing on Debian 7 / Ubuntu 12 / Mint 15

## Get the sources

We need `git` to clone the repository
```bash
sudo apt-get install git
```

Clone the yadt-config-rpm-maker repository
```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

## Install Dependencies

Install python development dependencies.
```bash
sudo apt-get install python-setuptools python-pip python-mock
```

Install `yadt-config-rpm-maker` runtime dependencies.
```bash
sudo apt-get install python-svn rpm python-rpm python-yaml subversion
```

## Running Tests

It is required that your /bin/sh points to a bash, not a dash!
[Dash is the default in Ubuntu](https://wiki.ubuntu.com/DashAsBinSh).
```bash
sudo rm /bin/sh
sudo ln -s /bin/bash /bin/sh
```
You can set /bin/sh back to bash by running `sudo dpkg-reconfigure dash`

Move to cloned repository
```bash
cd yadt-config-rpm-maker
```

Execute Tests
```bash
python setup.py test
```
