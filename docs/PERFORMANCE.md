# Performance tweaking

While building RPMs yadt-config-rpm-maker will have to create a lot of files.
You can influence this by making sure your spec file does clean up after the build process is finished.
If you have a lot of hosts in your datacenter, triggering the build on a normal machine might end up in a "out of space" error.
Each file will consume at least one inode. So the space itself might not be the problem, but the fact that all inodes are used.

Adding options `--verbose` and `--debug` will give you more information about the disk usage just before the
working directory will be clean up. During the build process yadt-config-rpm-maker will have to consume even more disk
space.

The example below shows you the output on a slow

```bash
[ INFO] Found 20 files in directory "target/tmp/yadt-config-rpm-maker.NCyG1f.1" with a total size of 2259767 bytes
[ INFO]         6 files with total size of      12212 bytes in directory "target/tmp/yadt-config-rpm-maker.NCyG1f.1"
[ INFO]         5 files with total size of    2166784 bytes in directory "target/tmp/yadt-config-rpm-maker.NCyG1f.1/.rpmdb"
[ INFO]         9 files with total size of      80771 bytes in directory "target/tmp/yadt-config-rpm-maker.NCyG1f.1/rpmbuild"
[DEBUG] Cleaning up working directory "target/tmp/yadt-config-rpm-maker.NCyG1f.1"
[DEBUG] Removing error log "target/tmp/yadt-config-rpm-makerIdZPNz.error.log"
```

By adding the `--debug` option you will also get information on the execution times of those methods where the
`mesaure_execution_time` decorator has been applied.

```bash
[ INFO] Elapsed time: 5.71s
[DEBUG] Execution times summary (keep in mind thread_count was set to 4):
[DEBUG]         1 times with average  0.03s = sum    0.03s : ConfigRpmMaker._upload_rpms
[DEBUG]         3 times with average   2.6s = sum    7.79s : HostRpmBuilder._build_rpm_using_rpmbuild
[DEBUG]         3 times with average  0.05s = sum    0.13s : HostRpmBuilder._copy_files_for_config_viewer
[DEBUG]         3 times with average  0.14s = sum    0.41s : HostRpmBuilder._filter_tokens_in_rpm_sources
[DEBUG]        23 times with average  0.01s = sum     0.1s : HostRpmBuilder._get_next_svn_service_from_queue
[DEBUG]         3 times with average  1.69s = sum    5.07s : HostRpmBuilder._save_network_variables
[DEBUG]         3 times with average  0.03s = sum    0.09s : HostRpmBuilder._tar_sources
[DEBUG]        15 times with average  0.01s = sum    0.07s : SvnService.export
[DEBUG]         1 times with average  0.02s = sum    0.02s : SvnService.get_change_set
[DEBUG]         1 times with average  0.01s = sum    0.01s : SvnService.get_hosts
[DEBUG]         8 times with average  0.01s = sum    0.03s : SvnService.log
[ INFO] Success.
```

Please keep in mind that calculating the data for the directory summary consume additional computing time.
Which means adding `--verbose` increases elapsed time a bit.
