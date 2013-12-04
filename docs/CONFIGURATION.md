# Configuration

## Environment Variables

| Variable Name                     | Fallback Value             | Description                             |
|-----------------------------------|----------------------------|-----------------------------------------|
| KEEPWORKDIR                       | False                      | If this variable is defined the working directory will not be erased.
| YADT_CONFIG_RPM_MAKER_CONFIG_FILE | yadt-config-rpm-maker.yaml | Path to configuration file

## Configuration File

The configuration file is a [YAML](http://yaml.org/) file.
Please have a look at the [example configuration file.](https://github.com/yadt/yadt-config-rpm-maker/blob/master/yadt-config-rpm-maker.yaml)

| Property Name           | Fallback Value   | Description                             |
|-----------------------  |------------------|-----------------------------------------|
| log_level               | INFO             | Defines the log level of the written files. The log level for syslog is by default DEBUG and the log level for the console is by default INFO (see usage info how to change the loglevel of console) Has to be one of DEBUG, ERROR or INFO
| thread_count            | 1                | Defines how many threads will be start to build your rpms. Use 0 if you want to start exactly one thread for each affected host.
| allow_unknown_hosts     | True             | config-rpm-maker will try to resolve the hosts it builds configuration rpms for. If this property is set to "true" config-rpm-maker will not fail when it can not resolve the host.
| config_rpm_prefix       | yadt-config-     | A prefix which will be prepended to the configuration rpms file names.
| config_viewer_hosts_dir | /tmp             | The directory where to put the config_viewer data.
| custom_dns_searchlist   | []               | Helps to resolve the hosts. If your organisation has hosts in "*.datacenter.intern" and in "*.organisation.intern" you can set this to ['datacenter.intern', 'organisation.intern']
| error_log_dir           |                  | The directory from where your config viewer will serve the error files.
| error_log_url           |                  | The url under which the config viewer will be accessible.
| path_to_spec_file       | default.spec     | The path within the configuration subversion repository where to find the template spec file for your configuration rpms.
| max_file_size           | 1024 * 100       | Maximum size of files allowed in config RPMs. This limit may prevent people from putting code or data into the config.
| repo_packages_regex     | ^yadt-.*-repos?$ | This filter will be applied when writing the dependencies into the rpm.
| rpm_upload_chunk_size   | 10               | Building the configuration rpms will happen in chunks. The number you specify here will define how many rpms will be built at the same time.
| rpm_upload_cmd          |                  | The command which will be used to upload the rpms. The command will get the list rpms to build as arguments. How many rpms will be given is defined via 'rpm_upload_chunk_size'. If this is not defined no command will be executed.
| svn_path_to_config      | /config          | The path within the configuration subversion repository where to find the configuration directory structure.
| thread_count            | 1                | Number of threads building the rpms at the same time.
| temp_dir                | /tmp             | This directory is used as a working directory when building rpms. You will find the error log files here.
