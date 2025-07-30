# Plymouth Theme Manager [STATE: WORK-IN-PROGRESS]

![Screenshot](assets/icon.png)

**Plymouth Theme Manager** ist eine grafische Benutzeroberfläche (GUI) zur einfachen Installation und Verwaltung von Plymouth Boot-Themes unter Ubuntu und anderen Debian-basierten Linux-Distributionen.

---

## 🚀 Funktionen

- Automatisches Laden einer Themenliste von GitHub (`themes.json`)
- Vorschau der Themes mit animierten GIFs oder PNGs
- Herunterladen & Entpacken von Themes aus dem Internet
- Automatische Installation in `/usr/share/plymouth/themes`
- Integration in das `update-alternatives`-System
- Setzen des Standard-Themes mit einem Klick
- Aktualisierung von `initramfs` für das neue Boot-Design

---

## 📦 Installation

### Voraussetzungen:

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0


The 2D Icon: 2D_tux.png is from https://icons8.de
The 3D icon: loading_and_surfing_tux.png is ' (c) ' 2025 SoulInfernoDE - If you want to use this icon you need to link to this project and ask for permission in this projects issue page
