# 兰译 lfy <img src="data/resources/icons/hicolor/scalable/apps/cool.ldr.lfy.svg" width="36" height="36" alt="兰译" style="vertical-align: middle;" />

<div align="center">

[![CHI](https://img.shields.io/badge/CHI-中文-red?style=for-the-badge)](README_ZH.md) [![ENG](https://img.shields.io/badge/ENG-English-blue?style=for-the-badge)](README.md)

</div>

<div align="center">

### 🖥️ GTK Version
<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/ldrfy/docs/main/images/gtk/main.png" alt="Home" width="100%"></td>
    <td><img src="https://raw.githubusercontent.com/ldrfy/docs/main/images/gtk/preference.png" alt="Settings" width="100%"></td>
    <td><img src="https://raw.githubusercontent.com/ldrfy/docs/main/images/gtk/preference1.png" alt="Settings1" width="100%"></td>
  </tr>
</table>

### 🧩 Qt Version
<table>
  <tr>
    <td><img src="https://raw.githubusercontent.com/ldrfy/docs/main/images/qt/main.png" alt="Home" width="100%"></td>
    <td><img src="https://raw.githubusercontent.com/ldrfy/docs/main/images/qt/preference.png" alt="Settings" width="100%"></td>
    <td><img src="https://raw.githubusercontent.com/ldrfy/docs/main/images/qt/preference1.png" alt="Settings1" width="100%"></td>
  </tr>
</table>

</div>

---

## 🚀 Installation

> If you have Python and pip installed, you can quickly install the Qt version via terminal:

```bash
pip install lfy
```

Run:
```bash
lfy
```

---

### 📦 Auto-compiled versions are also available:

🔗 [Click here to download](https://github.com/ldrfy/lfy/releases/tag/auto):  
Includes `rpm`, `deb`, `flatpak`, `archlinux`, `whl`

✅ Supported systems:
- Arch Linux (latest)
- Ubuntu 24.04
- openSUSE Tumbleweed
- Fedora 41

🔁 Use **Flatpak** for cross-platform support:

[![Download on Flathub](https://flathub.org/assets/badges/flathub-badge-en.png)](https://flathub.org/apps/details/cool.ldr.lfy)

---

### 🏗️ Manual Compilation

Ensure you have the necessary dependencies installed, then execute:

**Method 1 - Python:**
```bash
git clone https://github.com/ldrfy/lfy.git
cd lfy
python -m build
pip install dist/*.whl
```

**Method 2 - Meson:**
```bash
git clone https://github.com/ldrfy/lfy.git
cd lfy
meson setup builddir
meson compile -C builddir
sudo meson install -C builddir
```

---

## 📚 Documentation & Community

- 📘 [Software Documentation](https://github.com/ldrfy/docs)
- 🛠️ [Contributing Guide](https://github.com/ldrfy/docs/blob/main/CONTRIBUTE.md)
- 🌐 [Translation Guide](https://github.com/ldrfy/docs/blob/main/TRANSLATE.md)
- 📝 [Changelog](https://github.com/ldrfy/docs/blob/main/CHANGELOG.md)
