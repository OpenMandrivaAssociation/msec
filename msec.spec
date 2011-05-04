Name:		msec
Version:	0.80.10
Release:	%mkrel 2
Summary:	Security Level management for the Mandriva Linux distribution
License:	GPLv2+
Group:		System/Base
Url:		http://www.mandrivalinux.com/
Source0:	%{name}-%{version}.tar.bz2
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

Requires(pre):		rpm-helper >= 0.4
Requires(postun):	rpm-helper >= 0.4

Suggests:	msec-gui
# using s2u for desktop notifications
# it should be pulled by xinit to reduce basesystem size
# Suggests:	s2u >= 0.9

Conflicts:	passwd < 0.67
BuildRequires:	python
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
The Mandriva Linux Security package is designed to provide security features to
the Mandriva Linux users. It allows to select from a set of preconfigured
security levels, and supports custom permission settings, user-specified
levels, and several security utilities.  This packages includes main msec
application and several programs that will be run periodically in order to test
the security of your system and alert you if needed.

%package gui
Summary:	Graphical msec interface
Group:		System/Configuration/Other
Requires:	pygtk2.0
Requires:	msec

%description gui
The Mandriva Linux Security package is designed to provide security
features to the Mandriva Linux users. It allows to select from a set
of preconfigured security levels, and also supports custom permission
settings, user-specified levels, and several security utilities.
This packages includes graphical interface to control and tune msec
permissions.


%prep
%setup -q

%build
make CFLAGS="$RPM_OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"

%install
rm -rf %{buildroot}

make install

mkdir -p %{buildroot}/%{_sysconfdir}/{logrotate.d,profile.d}
touch %{buildroot}/var/log/security.log
touch %{buildroot}/etc/security/msec/security.conf
touch %{buildroot}/etc/security/msec/perms.conf
# init script
install -d %{buildroot}/%{_initrddir}
install -m755 %{_builddir}/%{name}-%{version}/msec.init %{buildroot}/%{_initrddir}/%{name}
mkdir -p %{buildroot}/etc/X11/xinit.d
touch %{buildroot}/etc/X11/xinit.d/msec

%find_lang %name

%pre
%_pre_groupadd xgrp
%_pre_groupadd ntools
%_pre_groupadd ctools

%preun
%_preun_service msec

%post
%_post_service msec

touch /var/log/security.log

if [ $1 != 1 ]; then
        # since 0.80.3, msec has its own upgrade script, which handles upgrades from previous versions
        /usr/share/msec/upgrade.sh
fi

# creating default configuration if not installed by installer
if [ "$DURING_INSTALL" != "1" ]; then
	if [ ! -s /etc/security/msec/security.conf ]; then
		# creating default level configuration
		cp -f /etc/security/msec/level.standard /etc/security/msec/security.conf
	fi

	if [ ! -s /etc/security/msec/perms.conf ]; then
		# creating default level configuration
		cp -f /etc/security/msec/perm.standard /etc/security/msec/perms.conf
	fi
fi

%postun

if [ $1 = 0 ]; then
	# cleanup crontabs on package removal
	rm -f /etc/cron.*/msec
fi

%_postun_groupdel xgrp
%_postun_groupdel ntools
%_postun_groupdel ctools

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING README*
%doc ChangeLog doc/*.txt
%_bindir/promisc_check
%_bindir/msec_find
%{_initrddir}/%{name}
%_sbindir/msec
%_sbindir/msecperms
%_datadir/msec/msec.py*
%_datadir/msec/config.py*
%_datadir/msec/libmsec.py*
%_datadir/msec/msecperms.py*
%_datadir/msec/tools.py*
%_datadir/msec/version.py*
%_datadir/msec/*.sh
%_datadir/msec/plugins/*
%_datadir/msec/scripts/*
%_mandir/*/*.*
%lang(cs) %_mandir/cs/man?/*
%lang(et) %_mandir/et/man?/*
%lang(eu) %_mandir/eu/man?/*
%lang(fi) %_mandir/fi/man?/*
%lang(fr) %_mandir/fr/man?/*
%lang(it) %_mandir/it/man?/*
%lang(nl) %_mandir/nl/man?/*
%lang(pl) %_mandir/pl/man?/*
%lang(ru) %_mandir/ru/man?/*
%lang(uk) %_mandir/uk/man?/*
%dir /var/log/security
%dir /etc/security/msec
%config /etc/security/msec/level.*
%config /etc/security/msec/perm.*
%config /etc/security/msec/server.*
%config(noreplace) /etc/security/msec/security.conf
%config(noreplace) /etc/security/msec/perms.conf
%config(noreplace) /etc/logrotate.d/msec
/etc/profile.d/*msec*

%config %attr(0755,root,root) /etc/X11/xinit.d/msec

%ghost /var/log/security.log
%ghost /var/log/msec.log

%files gui
%defattr(-,root,root)
%_sbindir/msecgui
%_datadir/msec/msecgui.py*
%_datadir/msec/help.py*
%_datadir/msec/msec.png



