# 兰译

开发中……，暂时无法使用


## 开发测试

仅在 `archlinux最新版 gnome桌面环境` 开发测试

### 依赖

- 编译工具：meson `sudo pacman -S meson`
- 其他：`sudo pacman -S python-gobject`

### 测试

安装在 `~/.local/` 所以请把 `export PATH="$HOME/.local/bin:$PATH"` 添加到环境变量

```bash
make install && lt 
```

### 翻译

```bash
# 首次创建某个语言翻译 `zh_TW`
make TO_LANG=zh_TW po-init

# 更新翻译文件
make update-pot && make TO_LANG=zh_TW update-po
```
