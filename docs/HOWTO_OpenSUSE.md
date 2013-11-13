# Developing on OpenSUSE 12

## Get the sources

Install git
```bash
zypper install git
```

and cloen the repo
```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

## Install Dependencies

```bash
zypper install python-yaml rpm-python python-pysvn rpm-build python-mock
```

## Running Tests

```bash
cd yadt-config-rpm-maker
```

and execute tests
```bash
./setup.py test
```
