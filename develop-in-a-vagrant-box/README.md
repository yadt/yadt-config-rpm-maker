# How to develop in a vagrant box

In this tutorial we will use a [vagrant](http://www.vagrantup.com/) box from [vagrantbox.es](http://vagrantbox.es/) to
develop on the destination distribution regardless of your developer machine.

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

Now you are ready to run the `bootstrap.sh` script.
This might take a while since we are using [mock](http://fedoraproject.org/wiki/Projects/Mock) to build the rpm.
Mock will at a certain perform `yum --installroot ...`. Unfortunately this is quite time consuming.

Please check the `boostrap.sh` and configure the git repository URL within the script if you want to clone your own fork.

```bash
bash bootstrap.sh
```

Now you should have a svnserve daemon running on your vagrant box.

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