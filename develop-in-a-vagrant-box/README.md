# How to develop in a vagrant box

In this tutorial we will use a [vagrant](http://www.vagrantup.com/) box from [vagrantbox.es](http://vagrantbox.es/) to
develop on the destination distribution regardless of your developer machine.

## Setup a vagrant box

Add a CentOS6 box or a Scientific Linux Box and initialize it
```bash
vagrant box add CentOS6 url-to-your-favourite-centos-box
vagrant init CentOS6
```

Start your vagrant box, login to it and execute the bootstrap script:
```bash
vagrant up
vagrant ssh
cd /vagrant
```

## Installation from source

Now you are ready to run the `bootstrap` script.
This might take a while since we are using [mock](http://fedoraproject.org/wiki/Projects/Mock) to build the rpm.
Mock will at a certain perform `yum --installroot ...`. Unfortunately this is quite time consuming.

Please check the `configuration.sh` and configure the git repository URL within the script if you want to clone your own fork.

```bash
./bootstrap
```

Now you should have a svnserve daemon running on your vagrant box.

Change into the vagrant home directory.
```bash
cd ~
```

Checkout the configuration repository.
```bash
svn checkout svn://localhost.localdomain/ working-copy
```

As a first example step we could add a new requirement to the host `berweb01`.
Change directory into `working-copy` and add ` httpd` to the variable file `RPM_REQUIRES`.
```bash
cd working-copy
vi config/host/berweb01/VARIABLES/RPM_REQUIRES
```

Commit those changes.
```bash
svn commit -m "We will need httpd since we are building a web application."
```
## Reinstalling

After you made code changes and committed them to your fork you will want to reinstall `yadt-config-rpm-maker` to your vagrant box.
```bash
./reinstall
```
We use this quite complicated way to omit working in the vagrant directory (which can be accessed by the vagrant box).

## Manual execution of `config-rpm-maker`

If you want to execute `config-rpm-maker` for a specific revision, please set the environment variable
`YADT_CONFIG_RPM_MAKER_CONFIG_FILE` to the destination of the configuration file.

```bash
export YADT_CONFIG_RPM_MAKER_CONFIG_FILE="/home/vagrant/configuration-repository/hooks/yadt-config-rpm-maker.yaml"
```

and execute `config-rpm-maker`
```bash
config-rpm-maker /home/vagrant/configuration-repository 1
```
