%define debug_package %{nil}
Name:		msec
Version:	0.80.10
Release:	22
Summary:	Security Level management for the Mandriva Linux distribution
License:	GPLv2+
Group:		System/Base
Url:		https://www.mandrivalinux.com/
Source0:	%{name}-%{version}.tar.bz2
Patch0:		msec-0.80.10-dont-pass-noscripts-to-rpm_-Va.patch
Patch1:		msec-0.80.10-remove.svn.patch
Patch2:		msec-0.80.10-start-networkmanager.patch
Patch3:		msec-0.80.10-glibc2.25.patch
Requires:	perl-base
Requires:	diffutils
Requires:	gawk
Requires:	coreutils
Requires:	iproute2
Requires:	setup >= 2.2.0-21mdk
Requires:	chkconfig >= 1.2.24-3mdk
Requires:	python-base >= 2.3.3-2mdk
Requires:	mailx
Requires:	python2
# at least xargs is used
Requires:	findutils
# ensure sysctl.conf and inittab are present before installing msec
Requires(post):	initscripts

Requires(pre):	rpm-helper >= 0.4
Requires(postun):	rpm-helper >= 0.4

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
%autopatch -p1
find . -name "*.py" -exec sed -i "s#/usr/bin/python#%{__python2}#" {} \;
find . -name "*.py" -exec sed -i "s#/usr/bin/env python#/usr/bin/env python2#" {} \;

%build
make CFLAGS="$RPM_OPT_FLAGS -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64"

%install

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
%_sbindir/msecgui
%_datadir/msec/msecgui.py*
%_datadir/msec/help.py*
%_datadir/msec/msec.png





%changelog
* Mon Nov 14 2011 Oden Eriksson <oeriksson@mandriva.com> 0.80.10-4.2
- built for updates

* Sat Nov 05 2011 Nicolas Lécureuil <nlecureuil@mandriva.com> 0.80.10-4.1
+ Revision: 717721
- Enable networkmanager service during install

  + Alexander Barakin <abarakin@mandriva.org>
    - remove check of /var/lib/svn
      bug: https://qa.mandriva.com/show_bug.cgi?id=63875

* Wed May 25 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.80.10-3
+ Revision: 678992
- don't pass '--noscripts' to 'rpm -Va' (#62644)

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0.80.10-2
+ Revision: 666496
- mass rebuild

* Mon Jun 28 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.10-1mdv2010.1
+ Revision: 549330
- 0.80.10:
- localization fixes

* Wed Jun 23 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.9-1mdv2010.1
+ Revision: 548737
- 0.80.9:
- fix gdm/consolekit interaction (#59100)
- use 'none' level as base when no BASE_LEVEL is defined (#59683)

* Wed May 26 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.8-1mdv2010.1
+ Revision: 546167
- 0.80.8:
- do not set gdm variables which are not used by new gdm
- filter out trailing whitespace for open port checks (#59457)

* Tue May 25 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.7-1mdv2010.1
+ Revision: 545912
- 0.80.7:
- Translation updates

* Tue Apr 27 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.6-1mdv2010.1
+ Revision: 539654
- 0.80.6:
- support merging legacy perm.local into main perms.conf
- add support for displaying periodic checks results
- add support for running periodic checks manually
- add support for merging legacy perm.local file if exists
- add support for ACL (based on patch from Tiago Marques <tiago.marques@caixamagica.pt>, #58640)
- add support for IGNORE_PID_CHANGES (#56744)
- properly filter chkrootkit checks (#58076).
- do not notify when no changes were found by a diff run
- properly checking if we are run within security script
- properly handle changes in password history when pam_unix is used (#58018).
  CCBUG: 58640
  CCBUG: 56744
  CCBUG: 58076
  CCBUG: 58018
- 0.80.5:
- added sudo plugin
- do not check inside entries excluded by EXCLUDE_REGEXP
- allow setting the EXCLUDE_REGEXP value in msecgui
- added security levels 'audit_daily' and 'audit_weekly'
- correctly check for changes in groups
- save mail reports for each check period (daily, weekly, monthly and manual)
- implemented security summary screen

* Thu Feb 18 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.4-1mdv2010.1
+ Revision: 507864
- 0.80.4:
- simplified UI for msecgui
- added custom security levels: fileserver, webserver, netbook
- added support for custom levels in gui
- ignore 'vmblock' filesystem during periodic checks (#57669)
- properly separate logs for different type of checks (daily, weekly, monthly and manual)
- xguest user does not have a password, so silence report about it
- added plugin to define log file retention period.

* Mon Feb 08 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.3-1mdv2010.1
+ Revision: 502269
- 0.80.3:
- added upgrade script to simplify upgrading from previous msec version
- cleaned up spec to use upgrade script instead of doing all the work
  manually
- improved log message when unowned or world-writable files are found
- running file-related periodic checks weekly on standard security level
  to easy disk I/O load
- improved error message when the wheel group is empty (#57463).
- added support for defining periodicity for individual security checks
- added support for sectool checks
- handle level-switching and saving in msec, using msecperms only for checking
  and settings file permissions
- do not duplicate variables present in BASE_LEVEL in security.conf and
  perms.conf files
- properly check if chkrootkit is present (#51309)

* Thu Jan 14 2010 Eugeni Dodonov <eugeni@mandriva.com> 0.80.2-1mdv2010.1
+ Revision: 491429
- 0.80.2:
- save the entire log that is sent by email in /var/log/security to allow
  consulting it without relying on email messages
- do not show toolbar, as it leads to confusion

* Mon Nov 30 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.80.1-1mdv2010.1
+ Revision: 471750
- 0.80.1:
- updated list of allowed services
- fix error which prevents 'msec save' from working correctly
- fix error message when checking non-local files (#55869,#56088)

* Thu Nov 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.8-1mdv2010.1
+ Revision: 460503
- 0.70.8:
- updated translations.

* Tue Oct 13 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.7-1mdv2010.0
+ Revision: 457190
- 0.70.7:
- fix issue which prevents msec from exiting correctly in some cases (#54470)

* Wed Oct 07 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.6-1mdv2010.0
+ Revision: 455562
- 0.70.6:
- use users' home directory for temporary files (SECURE_TMP) by default to be
  backward-compatible with previous distro versions
- improved startup script
- added option to skip security checks when running on battery power
  (CHECK_ON_BATTERY)

* Wed Sep 23 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.5-1mdv2010.0
+ Revision: 447873
- 0.70.5:
- do not show error messages for non-existent audit files
- man page entries are now sorted according to plugin
- split libmsec functionality into different plugins: audit (for periodic checks),
  msec (for local security settings) and network (for network-related settings)
- support excluding path from all checks
- Remove suggests on s2u - it will be pulled by xinit to reduce basesystem size.

* Wed Sep 09 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.4-1mdv2010.0
+ Revision: 434451
- 0.70.4
- implemented GUI for exception editing
- implemented exceptions for all msec checks (#51277)
- do not check for permission changes in block/character devices (#53424)
- create a summary for msec reports
- simplified permissions policy for standard level
- support enforcing file permissions in periodic msec runs
- allow configuring inclusion of current directory into path
- do not crash if config files have empty lines (#53031)

* Tue Aug 18 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.3-1mdv2010.0
+ Revision: 417721
- 0.70.3:
- give proper permissions to diff check files.
- Properly log promisc messages.
- msecgui: Added toolbar for msecgui.
- msecgui: Showing logo when running inside MCC.

* Wed Jul 15 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.2-1mdv2010.0
+ Revision: 396304
- 0.70.2:
- Correctly enforcing permissions on startup when required (#52268).
- Added new variable SECURE_TMP to configure location of temporary files.
- Improve description of changes in periodic packages integrity check.
- Properly handle promisc_check when running standalone (#51903)

* Fri Jun 26 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.70.1-1mdv2010.0
+ Revision: 389546
- 0.70.1
- Improved rpm check, splitted into CHECK_RPM_PACKAGES and CHECK_RPM_INTEGRITY.
- Supporting check for changes in system users and groups.
- Reworked auditing code, improved logging format, added support for
  custom auditing plugins, simplified checks.
- Added support for firewall configuration checks via CHECK_FIREWALL.
- Add support for FIX_UNOWNED to change unowned files to nobody/nogroup (#51791).
- Using WIN_PARTS_UMASK=-1 value instead of '0' when umask should not be set to
  prevent users and diskdrake confusion.
- Correctly handling empty NOTIFY_WARN variables (#51364, #51464).
- Correctly handling unicode messages (#50869).

* Thu Apr 23 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.22-1mdv2009.1
+ Revision: 368833
- 0.60.22
- Changed default WIN_PARTS_UMASK to be with sync with diskdrake.

* Wed Apr 22 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.21-1mdv2009.1
+ Revision: 368763
- 0.60.21
- Properly handle invalid WIN_PARTS_UMASK parameters.
- Fixed command inversion between DNS_SPOOFING_PROTECTION and
  IP_SPOOFING_PROTECTION.
- Cleaning up duplicated variables on upgrade.

* Tue Apr 21 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.20-1mdv2009.1
+ Revision: 368520
- 0.60.20:
  Using correct locale when available (#44561).

* Mon Apr 20 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.19-1mdv2009.1
+ Revision: 368440
- 0.60.19
- Properly support NTFS-3G partitions permissions (#50125).

* Wed Apr 15 2009 Thierry Vignaud <tv@mandriva.org> 0.60.18-2mdv2009.1
+ Revision: 367538
- translation updates

  + Eugeni Dodonov <eugeni@mandriva.com>
    - Do not create duplicate entries.
    - Use right file when upgrading configuration.

* Wed Apr 01 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.17-2mdv2009.1
+ Revision: 363410
- Installing with right permissions on /etc/X11/xinit.d/msec

* Mon Mar 30 2009 Thierry Vignaud <tv@mandriva.org> 0.60.17-1mdv2009.1
+ Revision: 362419
- translation updates

* Tue Mar 24 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.16-1mdv2009.1
+ Revision: 360832
- 0.60.16:
- Added support for desktop notifications on msec periodic checks.
- Using correct logger for syslog messages.
- Updated gui layout to better fit on small displays (netbooks).

* Thu Mar 12 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.15-1mdv2009.1
+ Revision: 354242
- 0.60.15
- Added specific permission for /var/log/btmp and wtmp (#48604)
- Do not run chkrootkit on NFS partitions (#37753).
- Changed CREATE_SERVER_LINK functionality to allow/deny presets of local and
  remote services, enabling it on secure level only by default.
- Added portreserve to list of safe remote services.
- Updated list of files that should not be world-writable or not user-owned.
- Running rpm database check with "--noscripts" (#42849).

* Thu Mar 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.14-1mdv2009.1
+ Revision: 349059
- 0.60.14
- Modularization: moved pam-related functionality to pam plugin.
- Updated list of safe services (#47460).

* Tue Mar 03 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.13-1mdv2009.1
+ Revision: 347875
- 0.60.13
- Added banner for msecgui.
- Moved PolicyKit code to plugin.
- Changed default ENABLE_STARTUP parameters to be in sync with
  crontab settings.
- Correctly handling parameter name changes on upgrade.

* Wed Feb 25 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.12-1mdv2009.1
+ Revision: 344963
- 0.60.12
- Correctly handle wheel group authentication (#19091)
- Correctly handling CHECK_RPM and CHECK_CHKROOTKIT parameters.
- Updating permissions on logs changed by logrotate (#47997).
- Added support for plugins.
- Added sample plugin.
- Added MSEC init script (#21270), controlled by ENABLE_STARTUP_MSEC and
  ENABLE_STARTUP_PERMS variables, and enabled by default on 'secure' level.

* Thu Feb 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.11-1mdv2009.1
+ Revision: 337983
- 0.60.11
- Added quiet mode (for use within installer).

* Thu Feb 05 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.10-1mdv2009.1
+ Revision: 337809
- 0.6.10
- Updated spec file to better work with Mandriva installer.
- Updated spec file to show urpmi notice.
- Level name changes: 'default' to 'standard'.
- Added support for running in chroot.
- Added initial support for plugins.

* Thu Jan 29 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.9-1mdv2009.1
+ Revision: 335395
- 0.60.9
- Reviewed description text for options (#47240)
- Added localization for msec.

* Mon Jan 26 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.8-1mdv2009.1
+ Revision: 333777
- 0.60.8
- Changed without_password to without-password to prevent bogus errors.
- Running expensive msec_find only when required.
- Fixing permissions on msec-created files (#27820 #47059)
- Handling network settings as in previous msec versions (#47240).
- Added default response to msecgui 'Save' dialog.
- Implemented support for custom paths checks in msecperms.

* Wed Jan 21 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.7-1mdv2009.1
+ Revision: 332291
- 0.60.7
- Now correctly integrating with MCC.

* Tue Jan 20 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.6-2mdv2009.1
+ Revision: 331887
- Fixed a typo in upgrade check.
- 0.60.6
- Removed Authentication tab (now handled by a separate application)
- Now it is possible to save settings without quitting.
- Better detection for file modifications (such as symlinks, moves, etc)
- Now asking to save changes before quitting when necessary.
- Highlighting default option value according to current level.
- Level selection improvements.
- Checking for $DISPLAY variable.
- Added HAL to list of safe services.
- Now highlighting options which are different from default values for level.
- Improved GUI spacing between options.
- Removed Notifications tab (merged with initial screen and periodic
  checks screen).
- Better handling of non-existent files (inittab and sysctl).
  (SPEC file improvements)
- Added an URPMI note for msec.
- Do not run msec after upgrade anymore, as it could break the install.
- Change the way the old files are upgraded.

* Mon Jan 19 2009 Frederic Crozat <fcrozat@mandriva.com> 0.60.5-3mdv2009.1
+ Revision: 331178
- Do not limit services by default, was preventing hal to be started

* Fri Jan 16 2009 Frederic Crozat <fcrozat@mandriva.com> 0.60.5-2mdv2009.1
+ Revision: 330251
- Workaround msec creating sysctl.conf / inittab files too early at install time

* Wed Jan 14 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.5-1mdv2009.1
+ Revision: 329458
- 0.60.5
 - Fix for wrong msec permission enforcing (msecperms -e), which would
   enforce all permissions when changing to a different level.

* Wed Jan 14 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.4-1mdv2009.1
+ Revision: 329241
- 0.60.4
 - Updated gui to allow immediate preview of options on level change.
 - New permissions control GUI.
 - Added support for custom security levels.

* Thu Jan 08 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.3-1mdv2009.1
+ Revision: 327003
- 0.60.3
 - Fixed gdm X permissions checking.
 - Now using /etc/security/shell instead of /etc/sysconfig/msec for
   shell variables.
 - Implemented authentication tab in msecgui.
 - More verbose screen on security level selection.

* Wed Jan 07 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.2-1mdv2009.1
+ Revision: 326499
- 0.60.2
 - Correctly handling kdmrc X server permissions.
 - Updated documentation.

* Wed Jan 07 2009 Eugeni Dodonov <eugeni@mandriva.com> 0.60.1-1mdv2009.1
+ Revision: 326453
- Complete msec redesign for Mandriva 2009.1.

* Tue Dec 16 2008 Eugeni Dodonov <eugeni@mandriva.com> 0.50.11-1mdv2009.1
+ Revision: 314809
- 0.50.10
- Correctly handle permit_root_login in sshd_config on level change
  (#19726).
- Handle multibyte characters in msec reports (#26773).

* Tue Sep 30 2008 Thierry Vignaud <tv@mandriva.org> 0.50.10-1mdv2009.0
+ Revision: 290111
- cron entry:
  o blacklist cifs instead of only smbfs for samba
  o exclude /media from searching like /mnt is
  o run with idle IOnice priority (#42795)

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 0.50.9-2mdv2009.0
+ Revision: 223324
- rebuild

* Tue Mar 25 2008 Pixel <pixel@mandriva.com> 0.50.9-1mdv2008.1
+ Revision: 189939
- 0.50.9: do not allow msec to mess with umask=xxx for vfat in level 3 (#37222)

* Fri Mar 07 2008 Thierry Vignaud <tv@mandriva.org> 0.50.8-1mdv2008.1
+ Revision: 181183
- use ionice to reduce I/O pressure when running msec_find and rpm -Va
- packaging cleanups

* Fri Jan 25 2008 Andreas Hasenack <andreas@mandriva.com> 0.50.7-1mdv2008.1
+ Revision: 157928
- 0.50.7: build msec_find with large file support (#36047)

* Fri Jan 25 2008 Andreas Hasenack <andreas@mandriva.com> 0.50.6-1mdv2008.1
+ Revision: 157908
- 0.50.6: strip binary chars from report email (#36848)

* Fri Jan 11 2008 Andreas Hasenack <andreas@mandriva.com> 0.50.5-1mdv2008.1
+ Revision: 148730
- fix infinitely growing kdmrc with set variable AllowShutdown to None (#12821)

* Fri Jan 11 2008 Andreas Hasenack <andreas@mandriva.com> 0.50.4-1mdv2008.1
+ Revision: 148599
- updated to version 0.50.4, which fixes the following:
  - Argument list too long (#36656)
  - msec_find should exclude pipes and sockets when
    reporting writable files (#27530)
  - msec diff (diff_check.sh)  does not take into
    account the chkrootkit reports (#21369)
  - netstat check for open ports doesnt pick up ports
    on ipv6 addr (#19486)
  - need to resolve symlinks before testing for local
    filesystems (#14387)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Nov 13 2007 Adam Williamson <awilliamson@mandriva.org> 0.50.3-2mdv2008.1
+ Revision: 108377
- requires python (#35485)
- new license policy


* Mon Mar 05 2007 Guillaume Rousse <guillomovitch@mandriva.org> 0.50.3-1mdv2007.0
+ Revision: 132893
- drop useless and redundant file dependencies
- new version
  spec cleanup

* Mon Mar 05 2007 Olivier Thauvin <nanardon@mandriva.org> 0.50.2-1mdv2007.1
+ Revision: 132772
- 0.50.2: fix (#27956 and #12353)

* Sat Aug 12 2006 Olivier Thauvin <nanardon@mandriva.org> 0.50.1-1mdv2007.0
+ Revision: 55666
- 0.50.1

  + Nicolas Lécureuil <neoclust@mandriva.org>
    - Fix manpages (close ticket #17430)

* Sat Aug 05 2006 Olivier Thauvin <nanardon@mandriva.org> 0.50.0-1mdv2007.0
+ Revision: 52699
- 0.50.0
- Import msec

* Fri Nov 18 2005 Frederic Lepied <flepied@mandriva.com> 0.49.1-1mdk
- fix bug #17921

* Mon Nov 14 2005 Frederic Lepied <flepied@mandriva.com> 0.49-1mdk
- scripts in /etc/profile.d no more config files
- fix bug #19206 by really generating /var/lib/msec/security.conf

* Tue Sep 20 2005 Frederic Lepied <flepied@mandriva.com> 0.48-1mdk
- enable_pam_root_from_wheel: fixed too laxist config in level 2 (bug #18403).

* Sat Sep 10 2005 Frederic Lepied <flepied@mandriva.com> 0.47.5-1mdk
- remove debugging output

* Fri Sep 09 2005 Frederic Lepied <flepied@mandriva.com> 0.47.4-1mdk
- fixed security.conf path (bug #18271).
- security.sh fix parsing of rpm -Va (bug #18326 , Michael Reinsch).
- security.sh: don't check sysfs and usbfs file system (bug #14359).
- make msec.sh bourne shell compatible.
- allow_xserver_to_listen: adapt to new way of specifying X server
arguments for kdm (bug #15759).

* Fri Sep 02 2005 Frederic Lepied <flepied@mandriva.com> 0.47.3-1mdk
- make /etc/rc.d/init.d/functions always readable (bug #18080)

* Thu Aug 18 2005 Frederic Lepied <flepied@mandriva.com> 0.47.2-1mdk
- another fix for bug #17477

* Wed Aug 17 2005 Frederic Lepied <flepied@mandriva.com> 0.47.1-1mdk
- really fix bug #17477

* Sat Aug 13 2005 Frederic Lepied <flepied@mandriva.com> 0.47-1mdk
- security_check.sh: fix user or homedir with spaces in
  (bug #16237).
- perm.*: o /etc/rc.d/init.d/xprint exception
          o  manage apache files (Guillaume Rousse) (bug #12183)
- allow_user_list: fixed kdmrc settings.
- support new inittab syntax for single user mode.
- fix parsing of new chage output (bug #17477).
- Perms.py: more robust parsing
- fixed wrong kdmrc values (bug #16268).
- follow new Single user need in inittab.

* Sat Jun 18 2005 Frederic Lepied <flepied@mandriva.com> 0.46-1mdk
- Mandriva
- new function enable_pam_root_from_wheel to allow transparent root
  access for the wheel group members.

* Mon Mar 21 2005 Frederic Lepied <flepied@mandrakesoft.com> 0.45.1-1mdk
- allow to use the variable CHKROOTKIT_OPTION as an argument to
chkrootkit (Michael, bug #12687).
- fixed documentation of the use of the current keyword (bug #12866).
- fixed password_history.

* Mon Feb 21 2005 Frederic Lepied <flepied@mandrakesoft.com> 0.45-1mdk
- requires mailx (bug #13497).
- fixed the permissions of sendmail symlinks (bug #13515).
- allow to put an EXCLUDE_REGEXP variable in
/etc/security/msec/security.conf to be used in msec_find (bug #508).

* Fri Oct 01 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.44.2-1mdk
- fix allow_reboot

* Sat Jul 31 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.44.1-1mdk
- fix directory creation code

* Sat Jul 31 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.44-1mdk
- new function allow_xauth_from_root
- the perm.local config file is now forcing permissions even if it's lowering the security.
- install translated man pages
- Mandrakelinux/Mandrakesoft

* Thu Jul 08 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.43-1mdk
- fixed again mailman permissions for mailman in level 3 (bug #9319)
- use getent to parse the passwd database (bug #9904)
- fix msec.csh (Pixel)
- more servers in level 4 (Florin)

* Sat Apr 24 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.42.2-1mdk
- corrected mailman log permissions (Guillaume Rousse bug #9319)

* Sun Mar 21 2004 Frederic Lepied <flepied@mandrakesoft.com> 0.42.1-1mdk
- check files on / in the daily check (workaround strange ntfw bug #9121)

