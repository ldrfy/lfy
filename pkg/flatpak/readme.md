# lfy

[flatpak-builder-tools](https://github.com/flatpak/flatpak-builder-tools/tree/master/pip)


[doc-submission](https://docs.flathub.org/docs/for-app-authors/submission/)

```bash
# 更新requests
flatpak-pip-generator requests --yaml

# 检查yaml
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest cool.ldr.lfy.yaml

# 构建安装
flatpak-builder --force-clean --sandbox --user --install --install-deps-from=flathub --ccache --mirror-screenshots-url=https://dl.flathub.org/media/ --repo=repo builddir cool.ldr.lfy.yaml

# 检查仓库，appstream-missing-screenshots可忽略
flatpak run --command=flatpak-builder-lint org.flatpak.Builder repo repo
``