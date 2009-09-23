Name:		msec
Version:	0.70.5
Release:	%mkrel 1
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
	# manage spelling change
     for i in /etc/security/msec/level.local /etc/security/msec/security.conf /var/lib/msec/security.conf; do
		if [ -f $i ]; then
			perl -pi -e 's/CHECK_WRITEABLE/CHECK_WRITABLE/g;s/CHECK_SUID_GROUP/CHECK_SGID/g' $i
		fi
	done
	for ext in today yesterday diff; do
		if [ -f /var/log/security/writeable.$ext ]; then
			mv -f /var/log/security/writeable.$ext /var/log/security/writable.$ext
		fi
		if [ -f /var/log/security/suid_group.$ext ]; then
			mv -f /var/log/security/suid_group.$ext /var/log/security/sgid.$ext
		fi
	done

	# find secure level
	SL=$SECURE_LEVEL
 	[ ! -r /etc/sysconfig/msec ] || SL=`sed -n 's/SECURE_LEVEL=//p' < /etc/sysconfig/msec` || :

	# upgrade from old style msec or rerun the new msec
	if grep -q "# Mandrake-Security : if you remove this comment" /etc/profile; then
		[ -z "$SL" -a -r /etc/profile.d/msec.sh ] && SL=`sed -n 's/.*SECURE_LEVEL=//p' <  /etc/profile.d/msec.sh` || :
		/usr/share/msec/cleanold.sh || :
	fi

	# remove the old way of doing the daily cron
	rm -f /etc/cron.d/msec

	# upgrading old config files
	if [ -n "$SL" ]; then
		# old msec installation, pre 2009.1
		# grab old configuration
		OLDCONFIG=`mktemp /etc/security/msec/upgrade.XXXXXX`
		[ -s /var/lib/msec/security.conf ] && cat /var/lib/msec/security.conf >> $OLDCONFIG
		[ -s /etc/security/msec/security.conf ] && cat /etc/security/msec/security.conf >> $OLDCONFIG
		if [ "$SL" -gt 3 ]; then
			NEWLEVEL="secure"
		elif [ "$SL" -gt 1 ]; then
			NEWLEVEL="standard"
		else
			NEWLEVEL="none"
		fi
		if [ ! -s /etc/security/msec/security.conf ]; then
			cp -f /etc/security/msec/level.$NEWLEVEL /etc/security/msec/security.conf
		fi
		if [ ! -s /etc/security/msec/perms.conf ]; then
			cp -f /etc/security/msec/perm.$NEWLEVEL /etc/security/msec/perms.conf
		fi

		if [ -f /etc/sysconfig/msec ]; then
			cat /etc/sysconfig/msec | grep -v SECURE_LEVEL > /etc/security/shell
		fi

		# upgrading old configuration
		if [ -s "$OLDCONFIG" ]; then
			cat ${OLDCONFIG} | sort | uniq >> /etc/security/msec/security.conf
		fi
		rm -f $OLDCONFIG
	fi

	# fixing spelling
	if [ -f /etc/security/msec/security.conf ]; then
		# without-password config setting
		sed -i -e 's/without_password/without-password/g' /etc/security/msec/security.conf
		# level name changes
		sed -i -e 's/=default$/=standard/g' /etc/security/msec/security.conf
		# variable name changes
		sed -i -e 's/RPM_CHECK=/CHECK_RPM=/g' -e 's/CHKROOTKIT_CHECK=/CHECK_CHKROOTKIT=/g' /etc/security/msec/security.conf
		# fixing WIN_PARTS_UMASK upgrade parameters
		sed -i -e 's/\(WIN_PARTS_UMASK\)=no/\1=0/g' /etc/security/msec/security.conf
		# serverlink changes
		sed -i -e 's/\(CREATE_SERVER_LINK\)=standard/\1=no/g' \
			-e 's/\(CREATE_SERVER_LINK\)=secure/\1=remote/g' \
			/etc/security/msec/security.conf
		# CHECK_RPM split into CHECK_RPM_PACKAGES and CHECK_RPM_INTEGRITY
		sed -i -e 's/CHECK_RPM=\(.*\)/CHECK_RPM_PACKAGES=\1\nCHECK_RPM_INTEGRITY=\1/g' /etc/security/msec/security.conf
		# removing duplicated entries
		TEMPFILE=`mktemp /etc/security/msec/upgrade.XXXXXX`
		cat /etc/security/msec/security.conf | sort | uniq > $TEMPFILE 2>/dev/null && mv -f $TEMPFILE /etc/security/msec/security.conf
		test -f $TEMPFILE && rm -f $TEMPFILE
	fi
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
	rm -f /etc/cron.d/msec /etc/cron.hourly/msec /etc/cron.daily/msec
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



