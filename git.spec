%{?scl:%scl_package git}
%{!?scl:%global pkg_name %{name}}
# Pass --without docs to rpmbuild if you don't want the documentation

# Settings for EL-5
# - Leave git-* binaries in %{_bindir}
# - Don't use noarch subpackages
# - Use proper libcurl devel package
# - Patch emacs and tweak docbook spaces
# - Explicitly enable ipv6 for git-daemon
# - Use prebuilt documentation, asciidoc is too old
# - Define missing python macro
%if 0%{?rhel} && 0%{?rhel} <= 5
%global gitcoredir          %{_bindir}
%global noarch_sub          0
%global libcurl_devel       curl-devel
%global emacs_old           1
%global docbook_suppress_sp 1
%global enable_ipv6         1
%global use_prebuilt_docs   1
%global filter_yaml_any     1
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%else
%global gitcoredir          %{_libexecdir}/git-core
%global noarch_sub          1
%global libcurl_devel       libcurl-devel
%global emacs_old           0
%global docbook_suppress_sp 0
%global enable_ipv6         0
%global use_prebuilt_docs   0
%global filter_yaml_any     0
%endif

# Settings for F-19+ and EL-7+
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%global bashcomp_pkgconfig  1
%global bashcompdir         %{_scl_root}%(pkg-config --variable=completionsdir bash-completion 2>/dev/null)
%global bashcomproot        %(dirname %{bashcompdir} 2>/dev/null)
%global desktop_vendor_tag  0
%global gnome_keyring       1
%global use_new_rpm_filters 1
%global use_systemd         1
%else
%global bashcomp_pkgconfig  0
%global bashcompdir         %{_sysconfdir}/bash_completion.d
%global bashcomproot        %{bashcompdir}
%global desktop_vendor_tag  1
%global gnome_keyring       0
%global use_new_rpm_filters 0
%global use_systemd         0
%endif

# Settings for EL <= 7
%if 0%{?rhel} && 0%{?rhel} <= 7
%{!?__global_ldflags: %global __global_ldflags -Wl,-z,relro}
%endif

Name:           %{?scl_prefix}git
Version:        2.9.2
Release:        1%{?dist}
Summary:        Fast Version Control System
License:        GPLv2
Group:          Development/Tools
URL:            https://git-scm.com/
Source0:        https://www.kernel.org/pub/software/scm/git/%{pkg_name}-%{version}.tar.xz
Source1:        https://www.kernel.org/pub/software/scm/git/%{pkg_name}-htmldocs-%{version}.tar.xz
Source2:        https://www.kernel.org/pub/software/scm/git/%{pkg_name}-manpages-%{version}.tar.xz
Source3:        https://www.kernel.org/pub/software/scm/git/%{pkg_name}-%{version}.tar.sign
Source4:        https://www.kernel.org/pub/software/scm/git/%{pkg_name}-htmldocs-%{version}.tar.sign
Source5:        https://www.kernel.org/pub/software/scm/git/%{pkg_name}-manpages-%{version}.tar.sign

# Junio C Hamano's key is used to sign git releases, it can be found in the
# junio-gpg-pub tag within git.
#
# (Note that the tagged blob in git contains a version of the key with an
# expired signing subkey.  The subkey expiration has been extended on the
# public keyservers, but the blob in git has not been updated.)
#
# https://git.kernel.org/cgit/git/git.git/tag/?h=junio-gpg-pub
# https://git.kernel.org/cgit/git/git.git/blob/?h=junio-gpg-pub&id=7214aea37915ee2c4f6369eb9dea520aec7d855b
Source9:        gpgkey-junio.asc

# Local sources begin at 10 to allow for additional future upstream sources
Source10:       git-init.el
Source11:       git.xinetd.in
Source12:       git.conf.httpd
Source13:       git-gui.desktop
Source14:       gitweb.conf.in
Source15:       git@.service
Source16:       git.socket
Patch0:         git-1.5-gitweb-home-link.patch
# https://bugzilla.redhat.com/490602
Patch1:         git-cvsimport-Ignore-cvsps-2.2b1-Branches-output.patch
# https://bugzilla.redhat.com/600411
Patch3:         git-1.7-el5-emacs-support.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if ! %{use_prebuilt_docs} && ! 0%{?_without_docs}
BuildRequires:  asciidoc >= 8.4.1
BuildRequires:  xmlto
%endif
BuildRequires:  desktop-file-utils
BuildRequires:  emacs
BuildRequires:  expat-devel
BuildRequires:  gettext
BuildRequires:  gnupg2
BuildRequires:  %{libcurl_devel}
%if %{gnome_keyring}
BuildRequires:  libgnome-keyring-devel
%endif
BuildRequires:  pcre-devel
%if 0%{?fedora} && 0%{?fedora} >= 21
BuildRequires:  perl-generators
%endif
BuildRequires:  perl(Test)
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel >= 1.2
%if %{bashcomp_pkgconfig}
BuildRequires:  pkgconfig(bash-completion)
%endif
%if %{use_systemd}
# For macros
BuildRequires:  systemd
%endif
%{?scl:Requires:%scl_runtime}

Requires:       %{?scl_prefix}git-core = %{version}-%{release}
Requires:       %{?scl_prefix}git-core-doc = %{version}-%{release}
Requires:       %{?scl_prefix}perl(Git)
Requires:       perl(Error)
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
Requires:       %{?scl_prefix}perl-Git = %{version}-%{release}

%if 0%{?fedora} >= 16 || 0%{?rhel} >= 7
Requires:       emacs-filesystem >= %{_emacs_version}
# These can be removed in Fedora 26
Obsoletes:      %{?scl_prefix}emacs-git <= 2.4.5
Obsoletes:      %{?scl_prefix}emacs-git-el <= 2.4.5
Provides:       %{?scl_prefix}emacs-git <= 2.4.5
Provides:       %{?scl_prefix}emacs-git-el <= 2.4.5
%endif

#Provides:       git-core = %{version}-%{release}
#%if 0%{?rhel} && 0%{?rhel} <= 5
#Obsoletes:      git-core <= 1.5.4.3
#%endif

# Obsolete git-arch
Obsoletes:      %{?scl_prefix}git-arch < %{version}-%{release}

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs common set of tools which are usually using with
small amount of dependencies. To install all git packages, including
tools for integrating with other SCMs, install the git-all meta-package.

%package all
Summary:        Meta-package to pull in all git tools
Group:          Development/Tools
%if %{noarch_sub}
BuildArch:      noarch
%endif
%{?scl:Requires:%scl_runtime}
Requires:       %{?scl_prefix}git = %{version}-%{release}
Requires:       %{?scl_prefix}git-cvs = %{version}-%{release}
Requires:       %{?scl_prefix}git-email = %{version}-%{release}
Requires:       %{?scl_prefix}git-gui = %{version}-%{release}
Requires:       %{?scl_prefix}git-svn = %{version}-%{release}
Requires:       %{?scl_prefix}git-p4 = %{version}-%{release}
Requires:       %{?scl_prefix}gitk = %{version}-%{release}
Requires:       %{?scl_prefix}perl-Git = %{version}-%{release}
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:       %{?scl_prefix}emacs-git = %{version}-%{release}
%endif
Obsoletes:      %{?scl_prefix}git <= 1.5.4.3

%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package core
Summary:        Core package of git with minimal funcionality
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
Requires:       less
Requires:       openssh-clients
Requires:       rsync
Requires:       zlib >= 1.2

%description core
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git-core rpm installs really the core tools with minimal
dependencies. Install git package for common set of tools.
To install all git packages, including tools for integrating with
other SCMs, install the git-all meta-package.

%package core-doc
Summary:        Documentation files for git-core
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
Requires:       %{?scl_prefix}git-core = %{version}-%{release}

%description core-doc
Documentation files for git-core package including man pages.

%package daemon
Summary:        Git protocol daemon
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
Requires:       %{?scl_prefix}git = %{version}-%{release}
%if %{use_systemd}
Requires:       systemd
Requires(post): systemd
Requires(preun):  systemd
Requires(postun): systemd
%else
Requires:       xinetd
%endif

%description daemon
The git daemon for supporting git:// access to git repositories

%package -n %{?scl_prefix}gitweb
Summary:        Simple web interface to git repositories
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}

%description -n %{?scl_prefix}gitweb
Simple web interface to track changes in git repositories

%package p4
Summary:        Git tools for working with Perforce depots
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
BuildRequires:  python
Requires:       %{?scl_prefix}git = %{version}-%{release}

%description p4
%{summary}.

%package svn
Summary:        Git tools for importing Subversion repositories
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
Requires:       %{?scl_prefix}git = %{version}-%{release}, subversion
Requires:       perl(Digest::MD5)
%if ! %{defined perl_bootstrap}
Requires:       perl(Term::ReadKey)
%endif

%description svn
Git tools for importing Subversion repositories.

%package cvs
Summary:        Git tools for importing CVS repositories
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}, cvs
Requires:       cvsps
Requires:       perl(DBD::SQLite)
Requires:       %{scl_prefix}perl(Git)

%description cvs
Git tools for importing CVS repositories.

%package email
Summary:        Git tools for sending email
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}, %{?scl_prefix}perl-Git = %{version}-%{release}
Requires:       perl(Authen::SASL)
Requires:       perl(Net::SMTP::SSL)
Requires:       %{scl_prefix}perl(Git)

%description email
Git tools for sending email.

%package gui
Summary:        Git GUI tool
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}, tk >= 8.4
#FIXME: fitk? gui? should we package that?
Requires:       gitk = %{version}-%{release}

%description gui
Git GUI tool.

%package -n %{?scl_prefix}gitk
Summary:        Git revision tree visualiser
Group:          Development/Tools
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}, tk >= 8.4

%description -n %{?scl_prefix}gitk
Git revision tree visualiser.

%package -n %{?scl_prefix}perl-Git
Summary:        Perl interface to Git
Group:          Development/Libraries
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}
BuildRequires:  perl(Error), perl(ExtUtils::MakeMaker)
Requires:       perl(Error)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%{?scl:
Provides:       %{?scl_prefix}perl(Git) = 0.01
Provides:       %{?scl_prefix}perl(Git::Error::Command)
Provides:       %{?scl_prefix}perl(Git::I18N)
Provides:       %{?scl_prefix}perl(Git::IndexInfo)
Provides:       %{?scl_prefix}perl(Git::activestate_pipe)
Requires:       %{?scl_prefix}perl(Git)
}

%description -n %{?scl_prefix}perl-Git
Perl interface to Git.

%package -n %{?scl_prefix}perl-Git-SVN
Summary:        Perl interface to Git::SVN
Group:          Development/Libraries
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}git = %{version}-%{release}
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%{?scl:
Provides:       %{?scl_prefix}perl(Git::SVN)
Provides:       %{?scl_prefix}perl(Git::SVN::Editor)
Provides:       %{?scl_prefix}perl(Git::SVN::Fetcher)
Provides:       %{?scl_prefix}perl(Git::SVN::GlobSpec)
Provides:       %{?scl_prefix}perl(Git::SVN::Log)
Provides:       %{?scl_prefix}perl(Git::SVN::Memoize::YAML)
Provides:       %{?scl_prefix}perl(Git::SVN::Migration)
Provides:       %{?scl_prefix}perl(Git::SVN::Prompt)
Provides:       %{?scl_prefix}perl(Git::SVN::Ra)
Provides:       %{?scl_prefix}perl(Git::SVN::Utils)
Requires:       %{?scl_prefix}perl(Git)
Requires:       %{?scl_prefix}perl(Git::SVN::Utils)
} # scl

%description -n %{?scl_prefix}perl-Git-SVN
Perl interface to Git.

%if 0%{?rhel} && 0%{?rhel} <= 6
%package -n %{?scl_prefix}emacs-git
Summary:        Git version control system support for Emacs
Group:          Applications/Editors
%{?scl:Requires:%scl_runtime}
Requires:       %{?scl_prefix}git = %{version}-%{release}
%if %{noarch_sub}
BuildArch:      noarch
Requires:       emacs(bin) >= %{_emacs_version}
%else
Requires:       emacs-common
%endif

%description -n %{?scl_prefix}emacs-git
%{summary}.

%package -n %{?scl_prefix}emacs-git-el
Summary:        Elisp source files for git version control system support for Emacs
Group:          Applications/Editors
%{?scl:Requires:%scl_runtime}
%if %{noarch_sub}
BuildArch:      noarch
%endif
Requires:       %{?scl_prefix}emacs-git = %{version}-%{release}

%description -n %{?scl_prefix}emacs-git-el
%{summary}.
%endif

%prep
# Verify GPG signatures
gpghome="$(mktemp -qd)" # Ensure we don't use any existing gpg keyrings
key="%{SOURCE9}"
# Ignore noisy output from GnuPG 2.0, used on EL <= 7
# https://bugs.gnupg.org/gnupg/issue1555
gpg2 --dearmor --quiet --batch --yes $key >/dev/null
for src in %{SOURCE0} %{SOURCE1} %{SOURCE2}; do
    # Upstream signs the uncompressed tarballs
    tar=${src/%.xz/}
    xz -dc $src > $tar
    gpgv2 --homedir "$gpghome" --quiet --keyring $key.gpg $tar.sign $tar
    rm -f $tar
done
rm -rf "$gpghome" # Cleanup tmp gpg home dir

%setup -q -n %{pkg_name}-%{version}
%patch0 -p1
%patch1 -p1
%if %{emacs_old}
%patch3 -p1
%endif

%if %{use_prebuilt_docs}
mkdir -p prebuilt_docs/{html,man}
xz -dc %{SOURCE1} | tar xf - -C prebuilt_docs/html
xz -dc %{SOURCE2} | tar xf - -C prebuilt_docs/man
# Remove non-html files
find prebuilt_docs/html -type f ! -name '*.html' | xargs rm
find prebuilt_docs/html -type d | xargs rmdir --ignore-fail-on-non-empty
%endif

# Use these same options for every invocation of 'make'.
# Otherwise it will rebuild in %%install due to flags changes.
cat << \EOF > config.mak
V = 1
CFLAGS = %{optflags}
LDFLAGS = %{__global_ldflags}
BLK_SHA1 = 1
NEEDS_CRYPTO_WITH_SSL = 1
USE_LIBPCRE = 1
ETC_GITCONFIG = %{_sysconfdir}/gitconfig
DESTDIR = %{buildroot}
INSTALL = install -p
GITWEB_PROJECTROOT = %{_localstatedir}/lib/git
GNU_ROFF = 1
htmldir = %{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}
prefix = %{_prefix}
gitwebdir = %{_localstatedir}/www/git
EOF

%if "%{gitcoredir}" == "%{_bindir}"
echo gitexecdir = %{_bindir} >> config.mak
%endif

%if %{docbook_suppress_sp}
# This is needed for 1.69.1-1.71.0
echo DOCBOOK_SUPPRESS_SP = 1 >> config.mak
%endif

# Filter bogus perl requires
# packed-refs comes from a comment in contrib/hooks/update-paranoid
# YAML::Any is optional and not available on el5
%if %{use_new_rpm_filters}
%{?perl_default_filter}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(packed-refs\\)
# Filter bogus perl provides and requires when build SCLs because %%scl_prefix
# is requied in that case, e.g.: rh-git29-perl(Git)
%{?scl:
  %global __provides_exclude %{?__provides_exclude:%__provides_exclude|}^perl\\(
  %global __requires_exclude %{?__requires_exclude:%__requires_exclude|}^perl\\(Git
}
%if ! %{defined perl_bootstrap}
%global __requires_exclude %{?__requires_exclude:%__requires_exclude|}perl\\(Term::ReadKey\\)
%endif
%else # ! use_new_rpm_filters

%{?filter_setup:
%{?filter_yaml_any:%filter_from_provides /perl(YAML::Any)/d}
%{?scl:%filter_from_provides /^perl(Git.*)/d}
%{?scl:%filter_from_requires /^perl(Git.*)/d}
%filter_from_provides /perl(packed-refs)/d
%filter_setup
}

%endif

%build
make %{?_smp_mflags} all
%if ! %{use_prebuilt_docs} && ! 0%{?_without_docs}
make %{?_smp_mflags} doc
%endif

make -C contrib/emacs

%if %{gnome_keyring}
make -C contrib/credential/gnome-keyring/
%endif
make -C contrib/credential/netrc/

make -C contrib/subtree/

# Remove shebang from bash-completion script
sed -i '/^#!bash/,+1 d' contrib/completion/git-completion.bash

%install
rm -rf %{buildroot}
make %{?_smp_mflags} INSTALLDIRS=vendor install
%if ! %{use_prebuilt_docs} && ! 0%{?_without_docs}
make %{?_smp_mflags} INSTALLDIRS=vendor install-doc
%else
cp -a prebuilt_docs/man/* %{buildroot}%{_mandir}
cp -a prebuilt_docs/html/* Documentation/
%endif

%if %{emacs_old}
%global _emacs_sitelispdir %{_datadir}/emacs/site-lisp
%global _emacs_sitestartdir %{_emacs_sitelispdir}/site-start.d
%else
# scl is not relevant for rhel <= 5
%{expand:%global _emacs_sitelispdir %{_scl_root}%{?_emacs_sitelispdir}}
%{expand:%global _emacs_sitestartdir %{_scl_root}%{?_emacs_sitestartdir}}
%endif
%global elispdir %{_emacs_sitelispdir}/git

make -C contrib/emacs install \
    emacsdir=%{buildroot}%{elispdir}
for elc in %{buildroot}%{elispdir}/*.elc ; do
    install -pm 644 contrib/emacs/$(basename $elc .elc).el \
    %{buildroot}%{elispdir}
done
install -Dpm 644 %{SOURCE10} \
    %{buildroot}%{_emacs_sitestartdir}/git-init.el

%if %{gnome_keyring}
install -pm 755 contrib/credential/gnome-keyring/git-credential-gnome-keyring \
    %{buildroot}%{gitcoredir}
# Remove built binary files, otherwise they will be installed in doc
make -C contrib/credential/gnome-keyring/ clean
%endif
install -pm 755 contrib/credential/netrc/git-credential-netrc \
    %{buildroot}%{gitcoredir}

make -C contrib/subtree install
%if ! %{use_prebuilt_docs}
make -C contrib/subtree install-doc
%endif
# it's ugly hack, but this file don't need to be copied to this directory
# it's already part of git-core-doc and it's alone here
rm -f %{buildroot}%{?_pkgdocdir}%{!?_pkgdocdir:%{_docdir}/%{name}-%{version}}/git-subtree.html

mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
install -pm 0644 %{SOURCE12} %{buildroot}%{_sysconfdir}/httpd/conf.d/git.conf
sed "s|@PROJECTROOT@|%{_localstatedir}/lib/git|g" \
    %{SOURCE14} > %{buildroot}%{_sysconfdir}/gitweb.conf

find %{buildroot} -type f -name .packlist -exec rm -f {} ';'
find %{buildroot} -type f -name '*.bs' -empty -exec rm -f {} ';'
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} ';'

#FIXME:
# Remove remote-helper python libraries and scripts, these are not ready for
# use yet
rm -rf %{buildroot}%{_scl_root}%{python_sitelib} %{buildroot}%{_scl_root}%{gitcoredir}/git-remote-testgit

# git-archimport is not supported
find %{buildroot} Documentation -type f -name 'git-archimport*' -exec rm -f {} ';'

#TODO: check this!!!
exclude_re="archimport|email|git-citool|git-cvs|git-daemon|git-gui|git-remote-bzr|git-remote-hg|gitk|p4|svn"
(find %{buildroot}{%{_bindir},%{_libexecdir}} -type f | grep -vE "$exclude_re" | sed -e s@^%{buildroot}@@) > bin-man-doc-files
(find %{buildroot}{%{_bindir},%{_libexecdir}} -mindepth 1 -type d | grep -vE "$exclude_re" | sed -e 's@^%{buildroot}@%dir @') >> bin-man-doc-files
(find %{buildroot}%{_scl_root}%{perl_vendorlib} -type f | sed -e s@^%{buildroot}@@) > perl-git-files
(find %{buildroot}%{_scl_root}%{perl_vendorlib} -mindepth 1 -type d | sed -e 's@^%{buildroot}@%dir @') >> perl-git-files
# Split out Git::SVN files
grep Git/SVN perl-git-files > perl-git-svn-files
sed -i "/Git\/SVN/ d" perl-git-files
%if %{!?_without_docs:1}0
(find %{buildroot}%{_mandir} -type f | grep -vE "$exclude_re|Git" | sed -e s@^%{buildroot}@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf %{buildroot}%{_mandir}
%endif

mkdir -p %{buildroot}%{_localstatedir}/lib/git
%if %{use_systemd}
mkdir -p %{buildroot}%{_unitdir}
cp -a %{SOURCE15} %{buildroot}%{_unitdir}/%{scl_prefix}git@.service
cp -a %{SOURCE16} %{buildroot}%{_unitdir}/%{scl_prefix}git.socket
%else
mkdir -p %{buildroot}%{_sysconfdir}/xinetd.d
# On EL <= 5, xinetd does not enable IPv6 by default
enable_ipv6="        # xinetd does not enable IPv6 by default
        flags           = IPv6"
perl -p \
    -e "s|\@GITCOREDIR\@|%{gitcoredir}|g;" \
    -e "s|\@BASE_PATH\@|%{_localstatedir}/lib/git|g;" \
%if %{enable_ipv6}
    -e "s|^}|$enable_ipv6\n$&|;" \
%endif
    %{SOURCE11} > %{buildroot}%{_sysconfdir}/xinetd.d/git
%endif

# Setup bash completion
install -Dpm 644 contrib/completion/git-completion.bash %{buildroot}%{bashcompdir}/git
ln -s git %{buildroot}%{bashcompdir}/gitk

# Install tcsh completion
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-completion.tcsh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# Move contrib/hooks out of %%docdir and make them executable
mkdir -p %{buildroot}%{_datadir}/git-core/contrib
mv contrib/hooks %{buildroot}%{_datadir}/git-core/contrib
chmod +x %{buildroot}%{_datadir}/git-core/contrib/hooks/*
pushd contrib > /dev/null
ln -s ../../../git-core/contrib/hooks
popd > /dev/null

# Install git-prompt.sh
mkdir -p %{buildroot}%{_datadir}/git-core/contrib/completion
install -pm 644 contrib/completion/git-prompt.sh \
    %{buildroot}%{_datadir}/git-core/contrib/completion/

# install git-gui .desktop file
desktop-file-install \
%if %{desktop_vendor_tag}
  --vendor fedora \
%endif
  --dir=%{buildroot}%{_datadir}/applications %{SOURCE13}

# find translations
%find_lang %{pkg_name} %{pkg_name}.lang
cat %{pkg_name}.lang >> bin-man-doc-files

# quiet some rpmlint complaints
chmod -R g-w %{buildroot}
find %{buildroot} -name git-mergetool--lib | xargs chmod a-x
# rm -f {Documentation/technical,contrib/emacs,contrib/credential/gnome-keyring}/.gitignore
# These files probably are not needed
find . -name .gitignore -delete
chmod a-x Documentation/technical/api-index.sh
find contrib -type f | xargs chmod -x

# Split core files
not_core_re="git-(add--interactive|am|credential-netrc|difftool|instaweb|relink|request-pull|send-mail|submodule)|gitweb|prepare-commit-msg|pre-rebase"
grep -vE "$not_core_re|\/man\/" bin-man-doc-files > bin-files-core
grep -vE "$not_core_re" bin-man-doc-files | grep "\/man\/" > man-doc-files-core
grep -E "$not_core_re" bin-man-doc-files > bin-man-doc-git-files


%clean
rm -rf %{buildroot}

%if %{use_systemd}
%post daemon
%systemd_post %{scl_prefix}git@.service

%preun daemon
%systemd_preun %{scl_prefix}git@.service

%postun daemon
%systemd_postun_with_restart %{scl_prefix}git@.service
%endif

%files -f bin-man-doc-git-files
%defattr(-,root,root)
%if 0%{?fedora} >= 16 || 0%{?rhel} >= 7
%{elispdir}
%{_emacs_sitestartdir}/git-init.el
%endif
%{_datadir}/git-core/contrib/hooks/update-paranoid
%{_datadir}/git-core/contrib/hooks/setgitperms.perl
#%{_datadir}/git-core/*
#%doc Documentation/*.txt
#%{!?_without_docs: %doc Documentation/*.html}
#%{!?_without_docs: %doc Documentation/howto/* Documentation/technical/*}

%files core -f bin-files-core
%defattr(-,root,root)
%{!?_licensedir:%global license %doc}
%license COPYING
# exlude is best way here because of troubles with symlinks inside git-core/
%exclude %{_datadir}/git-core/contrib/hooks/update-paranoid
%exclude %{_datadir}/git-core/contrib/hooks/setgitperms.perl
%{bashcomproot}
%{_datadir}/git-core/

%files core-doc -f man-doc-files-core
%defattr(-,root,root)
%doc README.md Documentation/*.txt Documentation/RelNotes contrib/
%{!?_without_docs: %doc Documentation/*.html Documentation/docbook-xsl.css}
%{!?_without_docs: %doc Documentation/howto Documentation/technical}
%if ! %{use_prebuilt_docs}
%{!?_without_docs: %doc contrib/subtree/git-subtree.html}
%endif


%files p4
%defattr(-,root,root)
%{gitcoredir}/*p4*
%{gitcoredir}/mergetools/p4merge
%doc Documentation/*p4*.txt
%{!?_without_docs: %{_mandir}/man1/*p4*.1*}
%{!?_without_docs: %doc Documentation/*p4*.html }

%files svn
%defattr(-,root,root)
%{gitcoredir}/*svn*
%doc Documentation/*svn*.txt
%{!?_without_docs: %{_mandir}/man1/*svn*.1*}
%{!?_without_docs: %doc Documentation/*svn*.html }

%files cvs
%defattr(-,root,root)
%doc Documentation/*git-cvs*.txt
%if "%{gitcoredir}" != "%{_bindir}"
%{_bindir}/git-cvsserver
%endif
%{gitcoredir}/*cvs*
%{!?_without_docs: %{_mandir}/man1/*cvs*.1*}
%{!?_without_docs: %doc Documentation/*git-cvs*.html }

%files email
%defattr(-,root,root)
%doc Documentation/*email*.txt
%{gitcoredir}/*email*
%{!?_without_docs: %{_mandir}/man1/*email*.1*}
%{!?_without_docs: %doc Documentation/*email*.html }

%files gui
%defattr(-,root,root)
%{gitcoredir}/git-gui*
%{gitcoredir}/git-citool
%{_datadir}/applications/*git-gui.desktop
%{_datadir}/git-gui/
%{!?_without_docs: %{_mandir}/man1/git-gui.1*}
%{!?_without_docs: %doc Documentation/git-gui.html}
%{!?_without_docs: %{_mandir}/man1/git-citool.1*}
%{!?_without_docs: %doc Documentation/git-citool.html}

%files -n %{?scl_prefix}gitk
%defattr(-,root,root)
%doc Documentation/*gitk*.txt
%{_bindir}/*gitk*
%{_datadir}/gitk
%{!?_without_docs: %{_mandir}/man1/*gitk*.1*}
%{!?_without_docs: %doc Documentation/*gitk*.html }

%files -n %{?scl_prefix}perl-Git -f perl-git-files
%defattr(-,root,root)
%exclude %{_mandir}/man3/*Git*SVN*.3pm*
%{!?_without_docs: %{_mandir}/man3/*Git*.3pm*}

%files -n %{?scl_prefix}perl-Git-SVN -f perl-git-svn-files
%defattr(-,root,root)
%{!?_without_docs: %{_mandir}/man3/*Git*SVN*.3pm*}

%if 0%{?rhel} && 0%{?rhel} <= 6
%files -n %{?scl_prefix}emacs-git
%defattr(-,root,root)
%doc contrib/emacs/README
%dir %{elispdir}
%{elispdir}/*.elc
%{_emacs_sitestartdir}/git-init.el

%files -n %{?scl_prefix}emacs-git-el
%defattr(-,root,root)
%{elispdir}/*.el
%endif

%files daemon
%defattr(-,root,root)
%doc Documentation/*daemon*.txt
%if %{use_systemd}
%{_unitdir}/%{scl_prefix}git.socket
%{_unitdir}/%{scl_prefix}git@.service
%else
%config(noreplace)%{_sysconfdir}/xinetd.d/git
%endif
%{gitcoredir}/git-daemon
%{_localstatedir}/lib/git
%{!?_without_docs: %{_mandir}/man1/*daemon*.1*}
%{!?_without_docs: %doc Documentation/*daemon*.html}

%files -n %{?scl_prefix}gitweb
%defattr(-,root,root)
%doc gitweb/INSTALL gitweb/README
%config(noreplace)%{_sysconfdir}/gitweb.conf
%config(noreplace)%{_sysconfdir}/httpd/conf.d/git.conf
%{_localstatedir}/www/git/


%files all
# No files for you!

%changelog
* Wed Jul 20 2016 Petr Stodulka <pstodulk@redhat.com> - 2.9.2-1
- Initial commit with git v2.9.2
- Fixes troubles with infinite loop in "git ls-tree" for broken symlink
  under refs/heads
- Rename git.service to git@.service to make it usable
- Resolves: #1204191 #1251460

