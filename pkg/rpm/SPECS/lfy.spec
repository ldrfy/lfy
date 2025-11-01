%define Name @APP_NAME@

Name: %{Name}
Version: @VERSION@
Release: 1
Summary: @APP_DES@
Summary(zh_CN): 一个非常好用的翻译软件，看文献的好帮手
License:  GPLv3+
URL:      @PACKAGE_URL@
Source0:  %{Name}-%{version}.zip
Requires: @DEPS@

%description
An easy and pleasant way to translate.
Support many translation services. Especially suitable for document translation.

%description -l zh_CN
一个非常好用的翻译软件，专注于文献翻译，可以复制翻译、截图翻译，支持百度、腾讯等翻译接口

%prep
%setup -q

%build
meson setup _build --prefix=/usr -Dbuild_type=@BUILD_TYPE@
meson compile -C _build


%check
meson test -C _build --print-errorlogs

%install
meson install -C _build --destdir=%{buildroot}


%files
/usr/bin/%{Name}
/usr/lib/%{Name}
/usr/share
