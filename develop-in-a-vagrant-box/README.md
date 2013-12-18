# Build and install in a vagrant box

In this tutorial we will use a [vagrant](http://www.vagrantup.com/) box from [vagrantbox.es](http://vagrantbox.es/) to
build and install `yadt-config-rpm-maker` on the destination distribution regardless of your developer machine.

## Setup a vagrant box

Initialize the vagrant box and start provisioning:
```bash
cd develop-in-a-vagrant-box
vagrant up
```
This might take a while since the provisioning script will clone the repository into the vm, build the RPM and
install it. We are using [mock](http://fedoraproject.org/wiki/Projects/Mock) to build the rpm.
Mock will at a certain perform `yum --installroot ...`. Unfortunately this is quite time consuming.

## Installation from source

Now you should have a svnserve daemon running on your vagrant box.
Let's login to the vm.
```bash
vagrant ssh
```

Checkout the configuration repository including the test data.
```bash
svn checkout svn://localhost.localdomain/ working-copy
```

As a first example step we could add a new requirement to the host `berweb01`.
Change directory into `working-copy` and add `httpd` to the variable file `RPM_REQUIRES`.
```bash
cd working-copy
vi config/host/berweb01/VARIABLES/RPM_REQUIRES
```

Commit those changes.
```bash
svn commit -m "We will need httpd since we are building a web application."
```

## Reinstalling

After you made code changes and committed them to your fork you might want to reinstall `yadt-config-rpm-maker` to
your vagrant box to verify your changes are working as expected. Please adapt the constant `SOURCE_REPOSITORY` within
the `configuration.sh` to point to your fork. Afterwards execute the reinstall script in your vm.
```bash
cd /vagrant
./reinstall
```
Of course you can modify your vagrant box in such a way that you can access the local clone of your repository too.
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
