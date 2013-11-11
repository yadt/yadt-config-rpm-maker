# Developing on Debian 7 / Ubuntu 12

## Get the sources

```bash
sudo apt-get install git
```

```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

## Install Dependencies

```bash
sudo apt-get install python-setuptools python-pip subversion
```

```bash
sudo apt-get install python-svn rpm python-rpm python-yaml
```

```bash
sudo pip install flake8 docopt mock
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
