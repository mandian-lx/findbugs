# Copyright (c) 2000-2005, JPackage Project
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

%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section free

Name:           findbugs
Version:        1.2.1
Release:        %mkrel 1.1.4
Epoch:          0
Summary:        Bug Pattern Detector for Java
License:        LGPL
URL:            http://findbugs.sourceforge.net/
Group:          Development/Java
Source0:        http://osdn.dl.sourceforge.net/findbugs/findbugs-%{version}-source.zip
Source1:        %{name}-script
Source2:        %{name}-16x16.png
Source3:        %{name}-32x32.png
Source4:        %{name}-48x48.png
Source5:        %{name}.desktop
Source6:        %{name}-sinjdoc.patch
Patch0:         %{name}-build_xml.patch
Patch1:         %{name}-no-com-sun-management.patch
Patch2:         %{name}-xml-reader.patch
Patch3:         %{name}-bcel.patch
Patch4:         %{name}-java-util-regex-gcj.patch
Patch5:         %{name}-no-com-apple.patch
Patch6:         %{name}-sorter-dialog.patch
Patch7:         %{name}-no-recompile-before-api-docs.patch
Patch8:         %{name}-location.patch
Requires:       asm3
Requires:       bcel5.3
Requires:       dom4j
Requires:       jaxen
Requires:       jpackage-utils >= 0:1.6
Requires:       java >= 0:1.4
BuildRequires:  ant >= 0:1.6
BuildRequires:  ant-nodeps >= 0:1.6
BuildRequires:  ant-junit >= 0:1.6
BuildRequires:  asm3
BuildRequires:  bcel5.3
BuildRequires:  dom4j
BuildRequires:  java-devel >= 0:1.4
BuildRequires:  jaxen
BuildRequires:  java-rpmbuild >= 0:1.6
BuildRequires:  java-devel >= 0:1.5
%if %{gcj_support}
BuildRequires:  java-gcj-compat-devel
%endif
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRequires:  desktop-file-utils
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
FindBugs is a program to find bugs in Java programs. It looks for 
instances of ``bug patterns''---code instances that are likely to be 
errors.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires(post): /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description javadoc
%{summary}.

%package manual
Summary:        Documents for %{name}
Group:          Development/Java

%description manual
%{summary}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%{_bindir}/find . -name '*.jar' | %{_bindir}/xargs -t %{__rm}
%{__rm} src/java/edu/umd/cs/findbugs/gui/OSXAdapter.java
%{__rm} src/java5/edu/umd/cs/findbugs/gui2/OSXAdapter.java
%{__perl} -pi -e 's|^Class-Path:.*$||g' etc/*.MF
%{__perl} -pi -e 's|<javac|<javac nowarn="true"|g' build.xml
%{__perl} -pi -e 's/\r$//g' bin/*.bat


%build
export CLASSPATH=$(build-classpath asm3/asm3 asm3/asm3-commons asm3/asm3-tree bcel5.3 dom4j jaxen junit):`pwd`/build/classes
export OPT_JAR_LIST="ant/ant-nodeps ant/ant-junit junit"
%{ant} -Dbuild.sysclasspath=only -Djar.dir=lib build
%{ant} -Dbuild.sysclasspath=only -Djar.dir=lib runjunit
# XXX: Must run this last
%{__patch} -p1 < %{SOURCE6}
%{ant} -Dbuild.sysclasspath=only -Djar.dir=lib apiJavadoc

%install
%{__rm} -rf %{buildroot}

# jars
%{__mkdir_p} %{buildroot}%{_javadir}/%{name}
%{__cp} -a lib/findbugs.jar %{buildroot}%{_javadir}/%{name}/findbugs-%{version}.jar
%{__cp} -a lib/findbugs-ant.jar %{buildroot}%{_javadir}/%{name}/findbugs-ant-%{version}.jar
%{__cp} -a lib/findbugsGUI.jar %{buildroot}%{_javadir}/%{name}/findbugs-gui-%{version}.jar
%{__ln_s} findbugs-gui-%{version}.jar %{buildroot}%{_javadir}/%{name}/findbugsGUI-%{version}.jar
%{__cp} -a lib/annotations.jar %{buildroot}%{_javadir}/%{name}/findbugs-annotations-%{version}.jar
%{__ln_s} findbugs-annotations-%{version}.jar %{buildroot}%{_javadir}/%{name}/annotations-%{version}.jar
%{__mkdir_p} %{buildroot}%{_javadir}/%{name}/plugin
%{__cp} -a plugin/coreplugin.jar %{buildroot}%{_javadir}/%{name}/plugin/findbugs-coreplugin-%{version}.jar
%{__ln_s} findbugs-coreplugin-%{version}.jar %{buildroot}%{_javadir}/%{name}/plugin/coreplugin-%{version}.jar
(cd %{buildroot}%{_javadir}/%{name} && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)
(cd %{buildroot}%{_javadir}/%{name}/plugin && for jar in *-%{version}*; do %{__ln_s} ${jar} ${jar/-%{version}/}; done)

%{__mkdir_p} %{buildroot}%{_sysconfdir}/ant.d
%{__cat} > %{buildroot}%{_sysconfdir}/ant.d/%{name} << EOF
asm3/asm3 asm3/asm3-commons asm3/asm3-tree bcel5.3 dom4j findbugs jaxen
EOF

# script
%{__mkdir_p} %{buildroot}%{_bindir}
%{__cp} -a %{SOURCE1} %{buildroot}%{_bindir}/findbugs

# javadoc
%{__mkdir_p} %{buildroot}%{_javadocdir}/%{name}-%{version}
%{__cp} -a apiJavaDoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
(cd %{buildroot}%{_javadocdir} && %{__ln_s} %{name}-%{version} %{name})

# freedesktop.org menu entry
%{__mkdir_p} %{buildroot}%{_datadir}/applications
%{_bindir}/desktop-file-install --vendor mandriva            \
        --dir ${RPM_BUILD_ROOT}%{_datadir}/applications      \
        --add-category X-MandrivaLinux-MoreApplications-Development-Tools \
        --remove-category Application                        \
        %{SOURCE5}

# icons for freedesktop.org and legacy menu entries
%{__install} -D -p -m 644 %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/16x16/apps/%{name}.png
%{__install} -D -p -m 644 %{SOURCE3} %{buildroot}%{_datadir}/icons/hicolor/32x32/apps/%{name}.png
%{__install} -D -p -m 644 %{SOURCE4} %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{__install} -D -p -m 644 %{SOURCE4} %{buildroot}%{_datadir}/pixmaps/%{name}.png

# manual
%{__mkdir_p} %{buildroot}%{_docdir}/%{name}-%{version}
%{__cp} -a doc/* %{buildroot}%{_docdir}/%{name}-%{version}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm --exclude %{_javadir}/findbugs/findbugs-%{version}.jar
%endif

%clean
%__rm -rf %{buildroot}

%post
%if %{gcj_support}
%{update_gcjdb}
%endif
%{update_desktop_database}
%update_icon_cache hicolor

%postun
%if %{gcj_support}
%{clean_gcjdb}
%endif
%{clean_desktop_database}
%clean_icon_cache hicolor

%files
%defattr(0644,root,root,0755)
%doc LICENSE.txt README.txt bin/* design
%attr(0755,root,root) %{_bindir}/findbugs
%{_javadir}/*
%config(noreplace) %{_sysconfdir}/ant.d/%{name}
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/*
%endif
%{_datadir}/applications/*%{name}.desktop
%{_datadir}/icons/*/*/apps/*
%{_datadir}/pixmaps/%{name}.png

%files javadoc
%defattr(0644,root,root,0755)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
%dir %{_javadocdir}/%{name}

%files manual
%defattr(0644,root,root,0755)
%dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/*
