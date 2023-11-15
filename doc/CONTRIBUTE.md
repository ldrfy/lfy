# 贡献说明


我目前仅在 `archlinux最新版 gnome桌面环境(45)` 开发测试，使用gtk4，不支持旧版

## 依赖

- 编译工具 meson

    ```bash
    sudo pacman -S meson
    ```

- 其他：

    ```bash
    sudo pacman -S python-gobject
    ```

## 测试

安装在 `~/.local/` 所以请把 `export PATH="$HOME/.local/bin:$PATH"` 添加到环境变量

- 安装

    ```bash
    make install && lfy
    ```

- 卸载

    ```bash
    make rm
    ```
