# Turn off the brp-python-bytecompile script
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Name:		is24-config-@@@HOST@@@
Version:	21
Release:	@@@REVISION@@@
Summary:	YADT config RPM for @@@HOST@@@
Group:		YADT
License:	GPL
Source0:	is24-config-@@@HOST@@@.tar.gz
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:	noarch
Provides:	is24-config-all, @@@RPM_PROVIDES@@@
Requires:	yadt-client, %{name}-repos = %{version}-%{release}, hostname-@@@HOST@@@, @@@RPM_REQUIRES_NON_REPOS@@@

%description
IS24 config RPM generated automatically from SVN

Variables:
@@@VARIABLES@@@

Overlaying:
@@@OVERLAYING@@@:

Svn-Log:
@@@SVNLOG@@@:

%prep
%setup -q -n %{name}


%build
rm -f %{name}.spec

%install
rm -Rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
tar -c . | tar -C $RPM_BUILD_ROOT/ -x -v

if test "$BASH_VERSION" && set +o posix ; then
    : # RPM runs scripts under /bin/sh which puts bash into POSIX mode which does not support < <( 
else
    echo 1>&2 "ERROR: THIS RPM NEEDS /bin/sh TO BE A REAL bash (dash SUCKS) !!! BASH_VERSION = $BASH_VERSION && set +o posix $?"
    exit 1
fi


filterPercentDirectives () {
    output () {
        : OUTPUT "$@"
        if test "$@" ; then
            echo "$@"
        fi
    }

    base="$1" ; shift
    defattr="%defattr(0644,root,root,0755)"
    lastline=""
    lastdefattr=""
    lastdefattrlen=0
    echo "$defattr"
    explicit_attr=0
    while read line; do
        : "LINE: $line"
        case "$line" in
            (*.%attr|*.%verify)
                # do not output last line, aggregate information
                percent_type="${line##*.%}"
                if [[ "$percent_type" = "attr" ]] ; then
                    explicit_attr=1
                fi
                lastline="%$percent_type($(tr -cd -- '-a-zA-Z0-9,' <"$base/$line")) $lastline"
                rm -f "$base/$line"
                continue # we did all we want to do for this line, process next line
                ;;
            (*)
                # other lines either start new section (%dir, %defattr) or are plain data lines
                # hence we can output what we collected so far.
                
                # theoretically we could use the excplicit_attr variable here to automatically
                # inject a %attr(755,-,-) for those files that don't have an explicit attr set
                # but happen to be executable. HOWEVER, THIS WOULD BE A REALLY BAD IDEA!
                # Because we would be setting a *default* exectuable attr of 755 that would cause
                # havoc in some special places like /etc/sudoers.d ... 
                explicit_attr=0

                output "$lastline"
                ;;
        esac

        case "$line" in
            (*.%defattr)
                lastline=""
                echo "%defattr($(tr -cd -- '-a-zA-Z0-9,' <"$base/$line"))"
                rm -f "$base/$line"
                lastdefattr="${line%.%defattr}"
                lastdefattrlen=${#lastdefattr}
            ;;
            (*.%dir)
                lastline="%dir \"${line%.%dir}\""
                rm -f "$base/$line"
            ;;
            (*)
                lastline="\"$line\""
                lastfile="$line"
                if test "$lastdefattr" -a "${line:0:$lastdefattrlen}" != "$lastdefattr" ; then
                    echo "$defattr"
                    lastdefattr=""
                fi
             ;;
        esac
    done < <(LC_ALL=C sort)

    # read the above comment in capitals
    explicit_attr=0
    output "$lastline"
}


# collect file list for main package
find "%{buildroot}" -path "%{buildroot}"/etc/yum.repos.d -prune -o -not -type d -printf "/%%P\n"  | filterPercentDirectives "%{buildroot}" >> files.lst

# collect file list for repos subpackage
if test -d "%{buildroot}"/etc/yum.repos.d ; then
    find "%{buildroot}"/etc/yum.repos.d -not -type d -printf "/etc/yum.repos.d/%%P\n"  | filterPercentDirectives "%{buildroot}"
fi >> files-repos.lst

%clean
rm -rf $RPM_BUILD_ROOT

%files -f files.lst

# subpackage
%package -n %{name}-repos
# Requires should not be empty, so require something that is there in any case
Requires: yum, @@@RPM_REQUIRES_REPOS@@@
Group: IS24/Configuration
Summary: IS24 YUM Repo definitions and dependencies for @@@HOST@@@

%description -n %{name}-repos
This subpackage encapsulates the YUM repository definitions and dependencies 
for this host. This package should be installed before the 
is24-config-@@@HOST@@@ package as it will configure all external YUM repos. The 
main config RPM can then use packages from these repos.

%files -n %{name}-repos -f files-repos.lst
