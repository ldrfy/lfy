# 贡献说明

我目前仅在 `archlinux最新版 gnome桌面环境(45)` 开发测试，使用gtk4，不支持旧版

> ！！！尽可能少的依赖第三方库，或者这个库在各个发行版都很普遍也行，尽量不适应过时技术

## 待完成

- GTK4相关
    - 如何窗口置顶
    - 响应剪贴时如何弹出窗口到最上面，而不是显示“已就绪”
    - 如何优雅的完成全局快捷键（尽量不使用过时的库，比如gtk3的，也不要使用root）
    - 如何优雅的显示状态栏图标（尽量不使用过时的库，比如gtk3的）

- wayland相关
    - `wayland` 环境下，不设置 `os.environ["GDK_BACKEND"] = "x11"`，如何复制立刻翻译，而不是鼠标移动到软件窗口才开始翻译


- 更多引擎，目前支持百度、谷歌、有道、腾讯，欢迎贡献
- 我英语不好，所以开发此项目。软件界面默认英文，有中文翻译，但是文档字太多，我只写中文……，其他人可以翻译文档，包括代码中的注释，也可以翻译


## 开发说明

下方仅对 archlinux 而言，ubuntu自己参考这里和 src/pkg/deb

### 编译工具 meson

```bash
sudo pacman -S meson appstream-glib
```

### 依赖：

```bash
sudo pacman -S libadwaita python-gobject python-requests
```


### 安装测试

安装在 `~/.local`

```bash
make test && lfy
```

卸载

```bash
make uninstall
```

### 打包

#### pacman

```bash
make aur
```

文件生成在 `./disk/*.pkg.tar.zst`

安装

```bash
sudo pacman -U ./disk/*.pkg.tar.zst
```

#### deb

工具

```bash
sudo pacman -S dpkg
```

```bash
make deb
```

文件生成在 `./disk/*.deb`

安装

```bash
sudo dpkg -i ./disk/*.deb
```


#### flatpak

工具

```bash
sudo pacman -S flatpak-builder
```

```bash
make flatpak
```

文件生成在 `./disk/*.flatpak`

安装

```bash
flatpak install ./disk/*.flatpak --user
```

