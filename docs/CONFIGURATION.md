# Configuration

## Environment Variables

| Variable Name                     | Fallback Value             | Description                             |
|-----------------------------------|----------------------------|-----------------------------------------|
| KEEPWORKDIR                       | False                      | If this variable is defined the working directory will not be erased.
| YADT_CONFIG_RPM_MAKER_CONFIG_FILE | yadt-config-rpm-maker.yaml | Path to configuration file

## Configuration File

The configuration file is a [YAML](http://yaml.org/) file.
Please have a look at the [example configuration file.](https://github.com/yadt/yadt-config-rpm-maker/blob/master/yadt-config-rpm-maker.yaml)

| Property Name                     | Fallback Value             | Description                             |
|-----------------------------------|----------------------------|-----------------------------------------|
| log_level                         | INFO                       | Has to be one of DEBUG, ERROR or INFO
| temp_dir                          |          | This directory is used as a working directory when building rpms. You will find the error log files here.