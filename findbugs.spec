%{?_javapackages_macros:%_javapackages_macros}

%global noupdatechecks_version 20140707gitcce19ac

Name:           findbugs
Version:        3.0.1
Release:        8
Summary:        Find bugs in Java code

Group:          Development/Java
License:        LGPLv2+
URL:            http://findbugs.sourceforge.net/
Source0:        http://downloads.sourceforge.net/%{name}/%{name}-%{version}-source.zip
Source1:        findbugs-ant
Source2:        findbugs-tools-README

Source3:        http://repo1.maven.org/maven2/com/google/code/findbugs/findbugs/3.0.1/findbugs-3.0.1.pom
Source4:        http://repo1.maven.org/maven2/com/google/code/findbugs/annotations/3.0.0/annotations-3.0.0.pom

# This archive contains the source for the noUpdateChecks plugin.
# It was created with:
#   $ git clone --bare https://code.google.com/p/findbugs
#   $ git --git-dir=findbugs.git archive --format tgz cce19ac plugins/noUpdateChecks -o noUpdateChecks-plugin-20140707gitcce19ac.tgz
Source5:        noUpdateChecks-plugin-%{noupdatechecks_version}.tgz

Source6:        http://repo1.maven.org/maven2/com/google/code/findbugs/findbugs-ant/3.0.0/findbugs-ant-3.0.0.pom

# This patch has not been submitted upstream, as it contains Fedora-specific
# changes.  It looks in /usr/share/java for jar files at compile time, instead
# of in findbugs' lib directory.
Patch0:         findbugs-build.patch

# Fedora-specific patch:
#  - Remove Class-Path entry from findbugs.jar manifest; use build-classpath
#    instead (#575632)
#  - Simplify shell fragment that determines findbugs_home (also fixes #848612)
Patch1:         findbugs-fedora.patch

# Fedora-specific patch to allow Ant task to work even though findbugs.jar has
# no Class-Path attribute in its manifest (bug #1080682)
Patch2:         findbugs-ant-task-classpath.patch

Patch3:         findbugs-manual.patch

BuildArch:      noarch

BuildRequires:  findbugs-bcel
BuildRequires:  ant
BuildRequires:  docbook-style-xsl
BuildRequires:  apache-commons-lang
BuildRequires:  dom4j
BuildRequires:  java-devel >= 1:1.6.0
BuildRequires:  jaxen
BuildRequires:  jcip-annotations
BuildRequires:  jdepend
BuildRequires:  jFormatString
BuildRequires:  jpackage-utils
BuildRequires:  jsr-305
BuildRequires:  junit
BuildRequires:  make
BuildRequires:  objectweb-asm
BuildRequires:  perl
#BuildRequires:  perl-generators
BuildRequires:  texlive
#BuildRequires:  tex(latex)
#BuildRequires:  texlive-preprint

# For generating HTML version of manual using xsltproc
BuildRequires:  xsltproc # libxslt
BuildRequires:  docbook-style-xsl

Requires:       findbugs-bcel
Requires:       apache-commons-lang
Requires:       dom4j
Requires:       java >= 1:1.6.0
Requires:       jaxen
Requires:       jcip-annotations
Requires:       jFormatString
Requires:       jpackage-utils
Requires:       jsr-305
Requires:       junit
Requires:       objectweb-asm

%description
Findbugs is a program which uses static analysis to look for bugs in Java code.
It can check for null pointer exceptions, multithreaded code errors, and other
bugs.

%package -n ant-findbugs
Group:          Development/Java
Summary:        Ant task for findbugs
Requires:       %{name} = %{version}-%{release}
Requires:       ant

%description -n ant-findbugs
This package defines an ant task for findbugs for easy integration of findbugs
into your ant-controlled project.

%package javadoc
Group:          Development/Java
Summary:        Javadoc documentation for findbugs

%description javadoc
Javadoc documentation for findbugs.

%package tools
Group:          Development/Java
Summary:        Addon tools for findbugs
Requires:       %{name} = %{version}-%{release}
Requires:       junit

%description tools
This package contains additional tools for use with findbugs.  See
README.fedora for more information.

%prep
%setup -q
%setup -a 5
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

cp -p %{SOURCE2} README.fedora

# Make sure we don't accidentally use any existing JAR files
rm -f lib/*.jar

# Get rid of code for Mac OS X that depends on a jar from Apple
rm -f src/gui/edu/umd/cs/findbugs/gui2/OSXAdapter.java
%pom_remove_dep com.apple:AppleJavaExtensions %{SOURCE3}

%build
# Build the class files and docs
ant docs build

# Build the javadocs
ant apiJavadoc

# Build the architecture PDF
pushd design/architecture
make depend
make
popd

# Package up the tools
pushd build/classes
jar cf ../../lib/findbugs-tools.jar edu/umd/cs/findbugs/tools
popd

# Build the noUpdateChecks plugin
pushd plugins/noUpdateChecks
ant plugin-jar
popd

%install
# Install the jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}
cp -p lib/annotations.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-annotations.jar
cp -p lib/%{name}-tools.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-tools.jar
cp -p lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}.jar

# Install the ant task
mkdir -p $RPM_BUILD_ROOT%{_javadir}/ant
cp -p lib/%{name}-ant.jar $RPM_BUILD_ROOT%{_javadir}/ant/ant-%{name}.jar
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/ant.d
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/ant.d/%{name}

# Install the javadocs
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}
cp -a apiJavaDoc $RPM_BUILD_ROOT%{_javadocdir}/%{name}

# Install the scripts
mkdir -p $RPM_BUILD_ROOT%{_bindir}
for f in $(find bin -maxdepth 1 -type f \! -name '*.bat' \! -name '*.ico'); do
  cp -p $f $RPM_BUILD_ROOT%{_bindir}
done

# Install the shared files
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -a etc plugin $RPM_BUILD_ROOT%{_datadir}/%{name}

# Install the noUpdateChecks plugin
cp -p plugins/noUpdateChecks/build/noUpdateChecks.jar $RPM_BUILD_ROOT%{_datadir}/%{name}/plugin

# Create /usr/share/findbugs/lib directory containing symlinks to required JARs (bug #1080682)
# List is based on the Class-Path attribute in etc/MANIFEST-findbugs.MF
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/lib
for i in findbugs findbugs-bcel dom4j jaxen objectweb-asm/asm-debug-all jsr-305 \
  jFormatString apache-commons-lang; do
    ln -s %{_javadir}/$i.jar $RPM_BUILD_ROOT%{_datadir}/%{name}/lib
done

# Remove now unnecessary build-only manual files so %%doc doesn't get them
rm -f build/doc/manual*.xml build/doc/manual*.xsl

# Install poms
mkdir -p $RPM_BUILD_ROOT%{_mavenpomdir}
sed -i 's/3\.0\.0/3\.0\.1/g' %{SOURCE4} %{SOURCE6}
cp %{SOURCE3} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
cp %{SOURCE4} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}-annotations.pom
cp %{SOURCE6} $RPM_BUILD_ROOT%{_mavenpomdir}/JPP.ant-ant-%{name}.pom

# Add depmaps
%add_maven_depmap -a net.sourceforge.findbugs:findbugs JPP-%{name}.pom %{name}.jar
%add_maven_depmap -a net.sourceforge.findbugs:annotations JPP-%{name}-annotations.pom %{name}-annotations.jar
%add_maven_depmap -a net.sourceforge.findbugs:findbugs-ant JPP.ant-ant-%{name}.pom ant/ant-findbugs.jar -f ant

%pretrans javadoc -p <lua>
path = "%{_javadocdir}/%{name}"
st = posix.stat(path)
if st and st.type == "link" then
  os.remove(path)
end

%files -f .mfiles
%doc licenses/LICENSE.txt design/DecouplingFromBCEL.txt design/VisitingAndCaching.txt
%doc README.txt plugin #"design/eclipse findbugs plugin features.sxw"
%doc design/architecture/architecture.pdf build/doc
%{_bindir}/*
%{_datadir}/%{name}

%files -n ant-findbugs -f .mfiles-ant
%doc licenses/LICENSE.txt
%config(noreplace) %{_sysconfdir}/ant.d/%{name}

%files javadoc
%{_javadocdir}/*

%files tools
%doc licenses/LICENSE.txt README.fedora
%{_javadir}/findbugs-tools.jar

%changelog
* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.0.1-7
- Add missing build-requires on make

* Thu Sep 22 2016 Richard Fearn <richardfearn@gmail.com> - 3.0.1-6
- Add missing dependency on dom4j (bug #1375367)

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Aug 25 2015 Richard Fearn <richardfearn@gmail.com> - 3.0.1-4
- findbugs-javadoc no longer depends on findbugs

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Richard Fearn <richardfearn@gmail.com> - 3.0.1-2
- Remove com.apple:AppleJavaExtensions dependency from POM (bug #1195809)

* Sun Mar 15 2015 Richard Fearn <richardfearn@gmail.com> - 3.0.1-1
- Update to 3.0.1 (bug #1199681)

* Thu Jan 08 2015 Richard Fearn <richardfearn@gmail.com> - 3.0.0-4
- Install Javadoc into unversioned directory (bug #1068943)

* Sun Jul 13 2014 Richard Fearn <richardfearn@gmail.com> - 3.0.0-3
- Use current POMs

* Tue Jul 08 2014 Richard Fearn <richardfearn@gmail.com> - 3.0.0-2
- Generate HTML manual (using xsltproc) and include in main package

* Tue Jul 08 2014 Richard Fearn <richardfearn@gmail.com> - 3.0.0-1
- Update to 3.0.0 (bug #1116843)

* Mon Jul 07 2014 Richard Fearn <richardfearn@gmail.com> - 2.0.3-9
- Revert back to installing Javadoc into versioned directory

* Sun Jun 22 2014 Richard Fearn <richardfearn@gmail.com> - 2.0.3-8
- Allow Ant task to work even though findbugs.jar has no Class-Path attribute
  in its manifest (bug #1080682)

* Sat Jun 21 2014 Richard Fearn <richardfearn@gmail.com> - 2.0.3-7
- Add findbugs-ant POM (bug #1080360) - thanks to gil cattaneo for the patch
- Use .mfiles for ant-findbugs package

* Tue Jun 10 2014 Richard Fearn <richardfearn@gmail.com> - 2.0.3-6
- Switch to .mfiles

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 23 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.0.3-4
- Fix requires on junit

* Mon Jan 13 2014 Marek Goldmann <mgoldman@redhat.com> - 2.0.3-3
- Use current POM's, RHBZ#1052081

* Wed Jan  8 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.0.3-2
- Add Maven alias for groupId net.sourceforge.findbugs
- Resolves: rhbz#1049949

* Fri Dec 27 2013 Richard Fearn <richardfearn@gmail.com> - 2.0.3-1
- Update to 2.0.3
- Drop findbugs-bug-1157.patch as the bug is fixed in 2.0.3

* Fri Dec 27 2013 Richard Fearn <richardfearn@gmail.com> - 2.0.2-5
- Use actual 2.0.2 POMs from Maven Central

* Sun Dec 08 2013 Richard Fearn <richardfearn@gmail.com> - 2.0.2-4
- Install Javadoc into unversioned directory

* Sun Dec 08 2013 Richard Fearn <richardfearn@gmail.com> - 2.0.2-3
- Depend on objectweb-asm3 (objectweb-asm is now ASM 5)

* Sat Oct 26 2013 Richard Fearn <richardfearn@gmail.com> - 2.0.2-2
- Add noUpdateChecks plugin, and fix bug #1157

* Wed Sep 11 2013 Richard Fearn <richardfearn@gmail.com> - 2.0.2-1
- Update to 2.0.2

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.9-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 1.3.9-16
- Perl 5.18 rebuild

* Sun Feb 24 2013 Richard Fearn <richardfearn@gmail.com> - 1.3.9-15
- Properly quote "eclipse findbugs plugin features.sxw" filename

* Sun Feb 24 2013 Richard Fearn <richardfearn@gmail.com> - 1.3.9-14
- Add BR for texlive-preprint, needed to build architecture PDF

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.9-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Aug 16 2012 Richard Fearn <richardfearn@gmail.com> - 1.3.9-12
- Allow FindBugs launcher scripts to be run from /bin or /usr/bin (#848612)

* Sat Jul 28 2012 Richard Fearn <richardfearn@gmail.com> - 1.3.9-11
- Remove Class-Path entry from findbugs.jar manifest (#575632); also remove
  Main-Class entry

* Sat Jul 28 2012 Richard Fearn <richardfearn@gmail.com> - 1.3.9-10
- Use Fedora JAR filenames (fixes FTBFS)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.9-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Mar 14 2012 Marek Goldmann <mgoldman@redhat.com> 1.3.9-8
- Added POMS (RHBZ#803352)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.9-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Aug 25 2011 Alexander Kurtakov <akurtako@redhat.com> 1.3.9-6
- Adapt for building/running with openjdk 7.
- Remove not needed parts.

* Mon Jun 27 2011 Richard Fearn <richardfearn@gmail.com> - 1.3.9-5
- Rebuild for ASM 3.3

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.9-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jun  2 2010 Richard Fearn <richardfearn@gmail.com> - 1.3.9-3
- Rebuild for ASM 3.2

* Thu Jan 14 2010 Jerry James <loganjerry@gmail.com> - 1.3.9-2
- Rebuild for jdepend 2.9.1 (bz 555476)

* Tue Aug 25 2009 Jerry James <loganjerry@gmail.com> - 1.3.9-1
- Update to 1.3.9

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar 17 2009 Jerry James <loganjerry@gmail.com> - 1.3.8-1
- Update to 1.3.8

* Tue Mar 10 2009 Jerry James <loganjerry@gmail.com> - 1.3.7-6
- Force building with OpenJDK; see GCJ note at the top of the spec file

* Tue Mar 10 2009 Jerry James <loganjerry@gmail.com> - 1.3.7-5
- Add missing ant-nodeps BR

* Fri Mar  6 2009 Jerry James <loganjerry@gmail.com> - 1.3.7-4
- Add README.fedora to the -tools package

* Thu Mar  5 2009 Jerry James <loganjerry@gmail.com> - 1.3.7-3
- Minor spec file cleanups from review

* Tue Feb 10 2009 Jerry James <loganjerry@gmail.com> - 1.3.7-2
- Rebuild for dependencies

* Fri Jan  2 2009 Jerry James <loganjerry@gmail.com> - 1.3.7-1
- Update to 1.3.7

* Tue Dec  9 2008 Jerry James <loganjerry@gmail.com> - 1.3.6-1
- Update to 1.3.6

* Fri Sep 19 2008 Jerry James <loganjerry@gmail.com> - 1.3.5-1
- Initial RPM
