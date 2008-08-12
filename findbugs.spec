# Copyright (c) 2000-2008, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define gcj_support 0

%define section free

Name:           findbugs
Version:        1.3.4
Release:        %mkrel 2.0.1
Epoch:          0
Summary:        Bug Pattern Detector for Java
License:        LGPLv2+
URL:            http://findbugs.sourceforge.net/
Group:          Development/Java
Source0:        http://download.sourceforge.net/findbugs/findbugs-%{version}-source.zip
Source1:        findbugs-script
Source2:        findbugs-16x16.png
Source3:        findbugs-32x32.png
Source4:        findbugs-48x48.png
Source5:        findbugs.desktop
Source6:        findbugs-1.3.4.pom
Source7:        findbugs-annotations-1.3.4.pom
Source8:        findbugs-ant-1.3.4.pom
Source9:        findbugs-coreplugin-1.3.4.pom
Source10:       findbugsGUI-1.3.4.pom
Patch0:         findbugs-build_xml.patch
Patch1:         findbugs-Project.patch
Patch2:         findbugs-SortedBugCollection.patch
Patch3:         findbugs-bcel.patch
Patch4:         findbugs-manifest.patch
Requires(post): jpackage-utils >= 0:1.7.4
Requires(postun): jpackage-utils >= 0:1.7.4
Requires:       bcel5.3
Requires:       dom4j
Requires:       jaxen
Requires:       java >= 0:1.5.0
Requires:       jcip-annotations
Requires:       jpackage-utils >= 0:1.7.4
Requires:       jsr-305
BuildRequires:  ant >= 0:1.6.5
BuildRequires:  ant-nodeps
BuildRequires:  ant-junit
BuildRequires:  bcel5.3
BuildRequires:  desktop-file-utils
BuildRequires:  dom4j
BuildRequires:  java-rpmbuild
BuildRequires:  jaxen
BuildRequires:  jcip-annotations
BuildRequires:  jpackage-utils >= 0:1.7.4
BuildRequires:  jsr-305
BuildRequires:  junit
BuildRequires:  asm3 >= 0:3.0
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%else
BuildArch:      noarch
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
FindBugs is a program to find bugs in Java programs. It looks for 
instances of ``bug patterns''---code instances that are likely to be 
errors.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.

%prep
%setup -q
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p1
%patch4 -p1

find . -name "*.bat" | xargs -t %{__rm}
find . -name "*.jar" | xargs -t %{__rm}

%{__rm} src/java/edu/umd/cs/findbugs/gui/OSXAdapter.java
%{__rm} src/java5/edu/umd/cs/findbugs/gui2/OSXAdapter.java

%{__rm} -r src/java5/net/jcip/annotations

# FIXME: setup is monolithic right now, as especially the ant task
# doesn't read the CLASSPATH
#%%{__perl} -p -i -e 's|^Class-Path:.*\n||g' etc/*.MF

pushd lib
%{__ln_s} $(build-classpath bcel5.3)
%{__ln_s} $(build-classpath dom4j)
%{__ln_s} $(build-classpath jaxen)
%{__ln_s} $(build-classpath jcip-annotations)
%{__ln_s} $(build-classpath jsr-305)
%{__ln_s} $(build-classpath junit)
%{__ln_s} $(build-classpath asm3/asm3)
%{__ln_s} $(build-classpath asm3/asm3-commons)
%{__ln_s} $(build-classpath asm3/asm3-tree)
popd

%build
export CLASSPATH=
export OPT_JAR_LIST="ant/ant-nodeps ant/ant-junit junit"
%{ant} build apiJavadoc 
#runjunit

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}/%{name}/lib
%{__cp} -a lib/findbugs.jar %{buildroot}%{_javadir}/%{name}/lib/findbugs-%{version}.jar
%{__cp} -a lib/findbugsGUI.jar %{buildroot}%{_javadir}/%{name}/lib/findbugsGUI-%{version}.jar
%{__cp} -a lib/findbugs-ant.jar %{buildroot}%{_javadir}/%{name}/lib/findbugs-ant-%{version}.jar
%{__cp} -a lib/annotations.jar %{buildroot}%{_javadir}/%{name}/lib/annotations-%{version}.jar

pushd %{buildroot}%{_javadir}/%{name}/lib
%{__ln_s} $(build-classpath bcel5.3)
%{__ln_s} $(build-classpath dom4j)
%{__ln_s} $(build-classpath jaxen)
%{__ln_s} $(build-classpath jcip-annotations)
%{__ln_s} $(build-classpath jsr-305)
%{__ln_s} $(build-classpath asm3/asm3)
%{__ln_s} $(build-classpath asm3/asm3-commons)
%{__ln_s} $(build-classpath asm3/asm3-tree)
for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done
popd

%{__cp} -a plugin %{buildroot}%{_javadir}/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/ant.d
%{__cat} > %{buildroot}%{_sysconfdir}/ant.d/%{name} << EOF
findbugs/lib/findbugs findbugs/lib/findbugs-ant
EOF

# poms
%{__mkdir_p} %{buildroot}%{_datadir}/maven2/poms
%{__cp} -a %{SOURCE6} %{buildroot}%{_datadir}/maven2/poms/JPP.findbugs.lib-findbugs.pom
%add_to_maven_depmap %{name} %{name} %{version} JPP/%{name}/lib %{name}
%{__cp} -a %{SOURCE7} %{buildroot}%{_datadir}/maven2/poms/JPP.findbugs.lib-annotations.pom
%add_to_maven_depmap %{name} annotations %{version} JPP/%{name}/lib annotations
%{__cp} -a %{SOURCE8} %{buildroot}%{_datadir}/maven2/poms/JPP.findbugs.lib-findbugs-ant.pom
%add_to_maven_depmap %{name} %{name}-ant %{version} JPP/%{name}/lib %{name}-ant
%{__cp} -a %{SOURCE9} %{buildroot}%{_datadir}/maven2/poms/JPP.findbugs.plugin-coreplugin.pom
%add_to_maven_depmap %{name} coreplugin %{version} JPP/%{name}/plugin coreplugin
%{__cp} -a %{SOURCE10} %{buildroot}%{_datadir}/maven2/poms/JPP.findbugs.lib-findbugsGUI.pom
%add_to_maven_depmap %{name} %{name}GUI %{version} JPP/%{name}/lib %{name}GUI

# script
%{__mkdir_p} %{buildroot}%{_bindir}
%{__cp} -a %{SOURCE1} %{buildroot}%{_bindir}/%{name}

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
# FIXME: (dwalluck): javadoc (openjdk6) throws NPE
%{__cp} -a apiJavaDoc/* %{buildroot}%{_javadocdir}/%{name}-%{version} || :
(cd %{buildroot}%{_javadocdir} && %{__ln_s} %{name}-%{version} %{name})

# freedesktop.org menu entry
%{__mkdir_p} %{buildroot}%{_datadir}/applications
%{_bindir}/desktop-file-install --vendor jpackage --dir %{buildroot}%{_datadir}/applications %{SOURCE5}

# icons for freedesktop.org menu entries
%{__install} -D -p -m 644 %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{__install} -D -p -m 644 %{SOURCE3} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{__install} -D -p -m 644 %{SOURCE4} %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{__install} -D -p -m 644 %{SOURCE4} %{buildroot}%{_datadir}/pixmaps/%{name}.png

# other scripts
%{__mkdir_p} %{buildroot}%{_datadir}/%{name}-%{version}/bin
%{__cp} -a bin/* %{buildroot}%{_datadir}/%{name}-%{version}/bin

# manual
%{__mkdir_p} %{buildroot}%{_docdir}/%{name}-%{version}
%{__cp} -a doc/* %{buildroot}%{_docdir}/%{name}-%{version}

%{gcj_compile}

%clean
%{__rm} -rf %{buildroot}

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt README.txt design
%attr(0755,root,root) %{_bindir}/*
%{_javadir}/%{name}
%dir %{_datadir}/%{name}-%{version}
%dir %{_datadir}/%{name}-%{version}/bin
%attr(0755,root,root) %{_datadir}/%{name}-%{version}/bin/*
%{_datadir}/maven2/poms/*.pom
%{_mavendepmapfragdir}/*
%{_sysconfdir}/ant.d/%{name}
%{gcj_files}
%{_datadir}/applications/*%{name}.desktop
%{_datadir}/icons/*/*/apps/*
%{_datadir}/pixmaps/%{name}.png

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%doc %{_docdir}/%{name}-%{version}
