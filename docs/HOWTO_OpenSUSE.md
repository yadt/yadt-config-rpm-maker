# Developing on OpenSUSE 12

## Get the sources

We need `git` to clone the repository
```bash
zypper install git
```

Clone the yadt-config-rpm-maker repository
```bash
git clone https://github.com/yadt/yadt-config-rpm-maker
```

## Install Dependencies

Install python development dependencies.
```bash
zypper python-mock
```

Install `yadt-config-rpm-maker` runtime dependencies.
```bash
zypper install python-yaml rpm-python python-pysvn rpm-build
```

## Running Tests

```bash
cd yadt-config-rpm-maker
```

and execute tests
```bash
./setup.py test
```
