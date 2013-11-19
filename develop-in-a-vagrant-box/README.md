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
bash bootstrap.sh
```