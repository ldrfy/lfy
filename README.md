# 兰译 lfy <img src="src/data/resources/icons/hicolor/scalable/apps/cool.ldr.lfy.svg" width = "36" height = "36" alt="兰译" align=center />

[ldr-translate](https://github.com/yuhldr/ldr-translate) 重构版

> [ldr-translate](https://github.com/yuhldr/ldr-translate) 还能用，但是不再更新，旧系统可以使用它

<center>
<div style="display: flex;">
    <img src="doc/images/main.png" alt="首页" style="width: 40%;">
    <img src="doc/images/preference.png" alt="设置1" style="width: 25%;">
    <img src="doc/images/server-preference.png" alt="设置2" style="width: 25%;">
</div>
</center>


## 优势：

- [x] 占用极小，不到 `0.2M`
- [x] 复制，自动翻译并弹窗
- [x] 支持 `gnome` 原生 `libadwaita`，简洁、美观！
- [x] 提供多种打包格式，预计推出 `archlinux` `deb` 等
- [x] 多引擎支持，目前 `百度、腾讯、谷歌、有道`，未来预计更多
- [x] 界面支持多国语言，使用 `gettext`

## 使用方法


### 方法一

打开以后，在窗口右上角，右键，选择置顶，然后可以响应复制翻译

> 我至今没找到gtk4窗口置顶的方法，而且窗口无法通过响应剪贴板弹到最上层，总是通知已经就绪


### 方法二

自己去系统设置里，设置为 `lfy` 自定义 `快捷键`（比如 `Ctrl alt L`）

然后，每次需要翻译时，先复制翻译文本，再点 `快捷键` 即可，你可以把这个窗口右键置顶，也可以关闭

> gtk4没找到不用root的全局快捷键方法，也没找到窗口不聚焦时自动关闭的方法


## 其他

> 我英语不好，所以开发此项目。软件界面默认英文，有中文翻译，但是文档字太多，我只写中文……，其他人可以翻译文档，包括代码中的注释，也可以翻译

- [贡献说明](doc/CONTRIBUTE.md)

- [翻译说明](doc/TRANSLATE.md)

- [更新说明](doc/CONTRIBUTE.md)


部分代码参考：

- [gnome-music](https://gitlab.gnome.org/GNOME/gnome-music)
- [dialect](https://github.com/dialect-app/dialect)
