# 贡献说明


我目前仅在 `archlinux最新版 gnome桌面环境(45)` 开发测试，使用gtk4，不支持旧版

## 待完成

- [] 设置项，使用Adw.PreferencesWindow
- [] 更多引擎，腾讯不需要，我这边即将接入


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

安装在 `~/.local/` 所以请把 `export PATH="$HOME/.local/bin:$PATH"` 添加到环境变量

### 安装

    ```bash
    make install && lfy
    ```

### 卸载

    ```bash
    make rm
    ```

## 打包

### pip

```bash
make whl
```

文件生成在 `./test/dist/*.whl`

可以如此卸载或者安装whl文件

```bash
# 卸载
pip uninstall lfy --break-system-packages
# 安装（版本不变时不会安装，一定要先卸载）
pip install ./test/dist/lfy-0.1.0-py3-none-any.whl --break-system-packages
```