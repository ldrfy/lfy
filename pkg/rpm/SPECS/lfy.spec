%define Name @APP_NAME@
%define _topdir %(echo $PWD)/..

Name: %{Name}
Version: @VERSION@
Release: 1
Summary: Translation software for read paper
Summary(zh_CN): 一个非常好用的翻译软件，看文献的好帮手
License:  GPLv3+
URL:      https://github.com/yuhldr/%{Name}
Requires: python3 python3-requests python3-gobject libadwaita

%description
An easy and pleasant way to translate.
Support many translation services. Especially suitable for document translation.

%description -l zh_CN
一个非常好用的翻译软件，专注于文献翻译，可以复制翻译、截图翻译，支持百度、腾讯等翻译接口


%files
/usr/bin/%{Name}
/usr/lib/%{Name}
/usr/share


%install
mv %{_builddir}/../usr %{buildroot}
