# How to set up a development environment on Debian 7

  
It is required that your /bin/sh points to a bash, not a dash!  
[Dash is the default in Ubuntu](https://wiki.ubuntu.com/DashAsBinSh).
```bash
sudo rm /bin/sh
sudo ln -s /bin/bash /bin/sh
```
You can set /bin/sh back to bash by running `sudo dpkg-reconfigure dash`


```bash
sudo apt-get install git
```

```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

```bash
sudo apt-get install python-setuptools python pip subversion
```

```bash
sudo apt-get install python-svn rpm python-rpm python-yaml
```


```bash
sudo pip install flake8 docopt mock
```

```bash
python setup.py test
```
