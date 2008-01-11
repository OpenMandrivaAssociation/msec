Name:		msec
Version:	0.50.5
Release:	%mkrel 1
Summary:	Security Level management for the Mandriva Linux distribution
License:	GPLv2+
Group:		System/Base
Url:		http://www.mandrivalinux.com/
Source0:	%{name}-%{version}.tar.bz2
Source1:	msec.logrotate
Source2:	msec.sh
Source3:	msec.csh
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

Requires(pre):		rpm-helper >= 0.4
Requires(postun):	rpm-helper >= 0.4

Conflicts:	passwd < 0.67
BuildRequires:	python
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
The Mandriva Linux Security package is designed to provide generic
secure level to the Mandriva Linux users...  It will permit you to
choose between level 0 to 5 for a less -> more secured distribution.
This packages includes several programs that will be run periodically
in order to test the security of your system and alert you if needed.

%prep
%setup -q

%build
make CFLAGS="$RPM_OPT_FLAGS"

%install
rm -rf %{buildroot}

install -d %{buildroot}/etc/security/msec
install -d %{buildroot}/etc/sysconfig
install -d %{buildroot}/usr/share/msec
install -d %{buildroot}/var/lib/msec
install -d %{buildroot}/usr/sbin %{buildroot}/usr/bin
install -d %{buildroot}/var/log/security
install -d %{buildroot}%{_mandir}/man{3,8}

cp -p init-sh/cleanold.sh share/*.py share/*.pyo share/level.* cron-sh/*.sh %{buildroot}/usr/share/msec
chmod 644 %{buildroot}/usr/share/msec/{security,diff}_check.sh
install -m 755 share/msec %{buildroot}/usr/sbin
install -m 644 conf/server.* %{buildroot}/etc/security/msec
install -m 644 conf/perm.* %{buildroot}/usr/share/msec
install -m 755 src/promisc_check/promisc_check src/msec_find/msec_find %{buildroot}/usr/bin

install -m644 man/C/*8 %{buildroot}%{_mandir}/man8/
install -m644 man/C/*3 %{buildroot}%{_mandir}/man3/


for i in man/??* ; do
    install -d %{buildroot}%{_mandir}/`basename $i`/man8
    install -m 644 $i/*.8 %{buildroot}%{_mandir}/`basename $i`/man8/
    install -d %{buildroot}%{_mandir}/`basename $i`/man3
    install -m 644 $i/*.3 %{buildroot}%{_mandir}/`basename $i`/man3/ || :
done;


touch %{buildroot}/var/log/security.log %{buildroot}/%{_sysconfdir}/sysconfig/%{name}

mkdir -p %{buildroot}/%{_sysconfdir}/{logrotate.d,profile.d}
install -m 644 %{SOURCE1} %{buildroot}/etc/logrotate.d/msec
install -m 755 %{SOURCE2} %{buildroot}/etc/profile.d
install -m 755 %{SOURCE3} %{buildroot}/etc/profile.d
touch %{buildroot}/var/log/security.log

%find_lang %name

%pre
%_pre_groupadd xgrp
%_pre_groupadd ntools
%_pre_groupadd ctools

%post
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
 		[ -n "$SL" ] && msec $SL < /dev/null || :
	else
		[ -n "$SL" ] && msec < /dev/null || :
	fi

	# remove the old way of doing the daily cron
	rm -f /etc/cron.d/msec
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
%doc AUTHORS COPYING share/README share/CHANGES
%doc ChangeLog doc/*.txt
%_bindir/promisc_check
%_bindir/msec_find
%_sbindir/msec
%_datadir/msec
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
%dir /var/lib/msec

%config(noreplace) /etc/security/msec/*
%config(noreplace) /etc/logrotate.d/msec
/etc/profile.d/msec*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%ghost /var/log/security.log


