Name:		msec
Version:	0.80.10
Release:	6
Summary:	Security Level management for the Mandriva Linux distribution
License:	GPLv2+
Group:		System/Base
Url:		http://www.mandrivalinux.com/
Source0:	%{name}-%{version}.tar.bz2
Patch0:		msec-0.80.10-dont-pass-noscripts-to-rpm_-Va.patch
Patch1:		msec-0.80.10-remove.svn.patch
Patch2:		msec-0.80.10-start-networkmanager.patch
Patch3:		msec-0.80.10-use-default-rpm-query-format.patch
Requires:	perl-base
Requires:	diffutils
Requires:	gawk
Requires:	coreutils
Requires:	iproute2
Requires:	setup >= 2.2.0-21mdk
Requires:	chkconfig >= 1.2.24-3mdk
Requires:	python-base >= 2.3.3-2mdk
Requires:	mailx
Requires:	python
# at least xargs is used
Requires:	findutils
# ensure sysctl.conf and inittab are present before installing msec
Requires(post):	initscripts

Requires(pre):	rpm-helper >= 0.4
Requires(postun):rpm-helper >= 0.4

Suggests:	msec-gui
# using s2u for desktop notifications
# it should be pulled by xinit to reduce basesystem size
# Suggests:	s2u >= 0.9

Conflicts:	passwd < 0.67
BuildRequires:	python

%description
The Mandriva Linux Security package is designed to provide security features to
the Mandriva Linux users. It allows to select from a set of preconfigured
security levels, and supports custom permission settings, user-specified
levels, and several security utilities.  This packages includes main msec
application and several programs that will be run periodically in order to test
the security of your system and alert you if needed.

%package	gui
Summary:	Graphical msec interface
Group:		System/Configuration/Other
Requires:	pygtk2.0
Requires:	msec

%description	gui
The Mandriva Linux Security package is designed to provide security
features to the Mandriva Linux users. It allows to select from a set
of preconfigured security levels, and also supports custom permission
settings, user-specified levels, and several security utilities.
This packages includes graphical interface to control and tune msec
permissions.

%prep
%setup -q
%apply_patches

%build
%make CFLAGS="$RPM_OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"

%install
make install

touch %{buildroot}%{_var}/log/security.log
touch %{buildroot}%{_sysconfdir}/security/msec/security.conf
touch %{buildroot}%{_sysconfdir}/security/msec/perms.conf
# init script
install -m755 msec.init -D %{buildroot}/%{_initrddir}/%{name}
mkdir -p %{buildroot}%{_sysconfdir}/X11/xinit.d
touch %{buildroot}%{_sysconfdir}/X11/xinit.d/msec

%find_lang %{name}

%pre
%_pre_groupadd xgrp
%_pre_groupadd ntools
%_pre_groupadd ctools

%preun
%_preun_service msec

%post
%_post_service msec

touch %{_var}/log/security.log

if [ $1 != 1 ]; then
	# since 0.80.3, msec has its own upgrade script, which handles upgrades from previous versions
	%{_datadir}/gmsec/upgrade.sh
fi

# creating default configuration if not installed by installer
if [ "$DURING_INSTALL" != "1" ]; then
	if [ ! -s %{_sysconfdir}/security/msec/security.conf ]; then
		# creating default level configuration
		cp -f %{_sysconfdir}/security/msec/level.standard %{_sysconfdir}/security/msec/security.conf
	fi

	if [ ! -s %{_sysconfdir}/security/msec/perms.conf ]; then
		# creating default level configuration
		cp -f %{_sysconfdir}/security/msec/perm.standard %{_sysconfdir}/security/msec/perms.conf
	fi
fi

%postun
if [ $1 = 0 ]; then
	# cleanup crontabs on package removal
	rm -f %{_sysconfdir}/cron.*/msec
fi

%_postun_groupdel xgrp
%_postun_groupdel ntools
%_postun_groupdel ctools

%files -f %{name}.lang
%doc AUTHORS COPYING README*
%doc ChangeLog doc/*.txt
%{_bindir}/promisc_check
%{_bindir}/msec_find
%{_initrddir}/%{name}
%{_sbindir}/msec
%{_sbindir}/msecperms
%{_datadir}/msec/msec.py*
%{_datadir}/msec/config.py*
%{_datadir}/msec/libmsec.py*
%{_datadir}/msec/msecperms.py*
%{_datadir}/msec/tools.py*
%{_datadir}/msec/version.py*
%{_datadir}/msec/*.sh
%{_datadir}/msec/plugins/*
%{_datadir}/msec/scripts/*
%{_mandir}/*/*.*
%lang(cs) %{_mandir}/cs/man?/*
%lang(et) %{_mandir}/et/man?/*
%lang(eu) %{_mandir}/eu/man?/*
%lang(fi) %{_mandir}/fi/man?/*
%lang(fr) %{_mandir}/fr/man?/*
%lang(it) %{_mandir}/it/man?/*
%lang(nl) %{_mandir}/nl/man?/*
%lang(pl) %{_mandir}/pl/man?/*
%lang(ru) %{_mandir}/ru/man?/*
%lang(uk) %{_mandir}/uk/man?/*
%dir %{_var}/log/security
%dir %{_sysconfdir}/security/msec
%config %{_sysconfdir}/security/msec/level.*
%config %{_sysconfdir}/security/msec/perm.*
%config %{_sysconfdir}/security/msec/server.*
%config(noreplace) %{_sysconfdir}/security/msec/security.conf
%config(noreplace) %{_sysconfdir}/security/msec/perms.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/msec
%{_sysconfdir}/profile.d/*msec*

%config %attr(0755,root,root) %{_sysconfdir}/X11/xinit.d/msec

%ghost %{_var}/log/security.log
%ghost %{_var}/log/msec.log

%files gui
%{_sbindir}/msecgui
%{_datadir}/msec/msecgui.py*
%{_datadir}/msec/help.py*
%{_datadir}/msec/msec.png



