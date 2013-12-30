# Configuration

## Environment Variables

| Variable Name                     | Fallback Value             | Description                |
|-----------------------------------|----------------------------|----------------------------|
| YADT_CONFIG_RPM_MAKER_CONFIG_FILE | yadt-config-rpm-maker.yaml | Path to configuration file |

## Configuration File

The configuration file is a [YAML](http://yaml.org/) file.
Please have a look at the [example configuration file.](https://github.com/yadt/yadt-config-rpm-maker/blob/master/yadt-config-rpm-maker.yaml)

| Property Name           | Fallback Value | Description |
|-------------------------|----------------|-------------|
| log_level               | DEBUG          | Has to be one of `DEBUG`, `ERROR` or `INFO`. Defines the log level of the written files. The log level for syslog is by default DEBUG (see [Syslog](#syslog) for more information) and the log level for the console is by default INFO. Please have a look at usage info by adding option `--help` to understand how to change the loglevel of console.
| thread_count            | 1              | Defines how many threads will be started to build your RPMs. Use 0 if you want to start exactly one thread for each affected host.
| allow_unknown_hosts     | True           | config-rpm-maker will try to resolve the hosts it builds configuration RPMs for. If this property is set to `true` config-rpm-maker will not fail (and therefore exit) when it can not resolve the host.
| config_rpm_prefix       | yadt-config-   | A prefix which will be prepended to the configuration RPMs file names.
| config_viewer_hosts_dir | /tmp           | The directory where to put the config viewer data.
| custom_dns_searchlist   | []             | Helps to resolve the hosts. If your organisation has hosts in `*.datacenter.intern` and in `*.organisation.intern` you can set this to `['datacenter.intern', 'organisation.intern']`
| error_log_dir           |                | The directory from where your config viewer will serve the error files.
| error_log_url           |                | The url under which the config viewer will be accessible.
| path_to_spec_file       | default.spec   | The path within the configuration subversion repository where to find the template spec file for your configuration RPMs.
| max_file_size           | 100 * 1024     | Maximum size of files allowed in config RPMs. This limit may prevent people from putting code or data into the config.
| max_failed_hosts        | 3              | Maximum number of host builds that might fail. If the maximum is hit the build for all other RPMs will be stopped.
| repo_packages_regex     | .\*-repo.\*    | This filter will be applied when writing the dependencies into the RPM.
| rpm_upload_chunk_size   | 10             | Building the configuration RPMs will happen in chunks. The number you specify here will define how many RPMs will be built at the same time.
| rpm_upload_cmd          |                | The command which will be used to upload the RPMs. The command will get the list RPMs to build as arguments. How many RPMs will be given is defined via `rpm_upload_chunk_size`. If this is not defined no command will be executed. If None is given upload will not be executed.
| svn_path_to_config      | /config        | The path within the configuration subversion repository where to find the configuration directory structure.
| thread_count            | 1              | Number of threads building the RPMs at the same time.
| temp_dir                | /tmp           | This directory is used as a working directory when building RPMs. You will find the error log files here.

## Syslog

The logging of yadt-config-rpm-maker's `SysLogHandler` is set to `DEBUG`.
On most systems the log level for `/var/log/messages` will be `*.info` by default.
If you want to see more logging details you will have to configure the log level within
`/etc/syslog.conf` or `/etc/rsyslog.conf`.
