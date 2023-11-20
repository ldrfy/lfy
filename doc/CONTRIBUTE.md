# 贡献说明


我目前仅在 `archlinux最新版 gnome桌面环境(45)` 开发测试，使用gtk4，不支持旧版

## 待完成

- 目前复制就翻译，后续可选快捷键翻译，即将支持。！！无需贡献！！
- 更多引擎，目前支持百度、谷歌、有道、腾讯，欢迎贡献
- 我英语不好，所以开发此项目。软件界面默认英文，有中文翻译，但是文档字太多，我只写中文……，其他人可以翻译文档，包括代码中的注释，也可以翻译


## 依赖

### 编译工具 meson

    ```bash
    sudo pacman -S meson
    ```

### 其他：

    ```bash
    sudo pacman -S python-gobject
    ```

## 测试

安装在 `/usr/local`

### 安装

```bash
make install && lfy
```

### 卸载

```bash
make uninstall
```

## 打包

### pacman

```bash
make whl
```

文件生成在 `./disk/*.pkg.tar.zst`

```bash
# 卸载
sudo pacman -U ./disk/*.pkg.tar.zst
```

### deb


