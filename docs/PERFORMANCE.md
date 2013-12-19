# Performance tweaking / Troubleshooting

While building RPMs `yadt-config-rpm-maker` will have to create a lot of files.
You can reduce the amount of created files by making sure your spec file cleans up after the build process is finished.
If you have a lot of hosts in your datacenter, triggering the build on a normal machine might end up in a "out of disk
space" error. The disk space itself might not be the problem, but since each created file will consumes at least one
inode, your file system might be out of inodes. Try `df -iH` to get an overview.

Adding options `--verbose` and `--debug` will give you more information about the disk usage just before the
working directory will be clean up. During the build process yadt-config-rpm-maker will have to consume even more disk
space.

Some example output
```
[DEBUG] Found 20 files in directory "target/tmp/yadt-config-rpm-maker.GbWhc_.1" with a total size of 2264265 bytes
[DEBUG]         6 files with total size of      12154 bytes in directory "target/tmp/yadt-config-rpm-maker.GbWhc_.1"
[DEBUG]         5 files with total size of    2166784 bytes in directory "target/tmp/yadt-config-rpm-maker.GbWhc_.1/.rpmdb"
[DEBUG]         9 files with total size of      85327 bytes in directory "target/tmp/yadt-config-rpm-maker.GbWhc_.1/rpmbuild"
[DEBUG] Cleaning up working directory "target/tmp/yadt-config-rpm-maker.GbWhc_.1"
[DEBUG] Removing error log "target/tmp/yadt-config-rpm-maker.1f_zap.revision-1.error.log"
```
Please keep in mind that calculating the data for the directory summary consumes additional computing time.
Which means adding `--verbose` increases elapsed time a bit.

By adding the `--debug` option you will also get information on the execution times of those methods where the
`mesaure_execution_time` decorator has been applied.

```
[DEBUG] Execution times summary (keep in mind thread_count was set to 4):
[DEBUG]         1 times with average  0.01s = sum    0.01s : ConfigRpmMaker._upload_rpms
[DEBUG]         3 times with average  2.46s = sum    7.38s : HostRpmBuilder._build_rpm_using_rpmbuild
[DEBUG]         3 times with average  0.05s = sum    0.13s : HostRpmBuilder._copy_files_for_config_viewer
[DEBUG]         3 times with average  0.08s = sum    0.22s : HostRpmBuilder._filter_tokens_in_rpm_sources
[DEBUG]        21 times with average  0.01s = sum    0.14s : HostRpmBuilder._get_next_svn_service_from_queue
[DEBUG]         3 times with average  0.01s = sum    0.03s : HostRpmBuilder._save_network_variables
[DEBUG]         3 times with average  0.05s = sum    0.15s : HostRpmBuilder._tar_sources
[DEBUG]        14 times with average  0.01s = sum    0.07s : SvnService.export
[DEBUG]         1 times with average  0.02s = sum    0.02s : SvnService.get_changed_paths
[DEBUG]         1 times with average  0.01s = sum    0.01s : SvnService.get_hosts
[DEBUG]         9 times with average  0.01s = sum    0.06s : SvnService.log
[ INFO] Elapsed time: 3.91s
[ INFO] Success.
```
