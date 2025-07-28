import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import os
import requests
import tempfile
import subprocess
import tarfile
import json

# Pfad zur zentralen Theme-Liste auf GitHub
THEME_LIST_URL = "https://raw.githubusercontent.com/SoulInfernoDE/plymouth-theme-manager/main/plymouth_theme_manager/themes.json"
THEME_DIR = "/usr/share/plymouth/themes/"

class Theme:
    def __init__(self, name, description, theme_url, preview_url):
        self.name = name
        self.description = description
        self.theme_url = theme_url
        self.preview_url = preview_url

class ThemeManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Plymouth Theme Manager")
        self.set_border_width(10)
        self.set_default_size(800, 600)
        self.theme_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(self.theme_box)
        self.load_themes()

    def load_themes(self):
        try:
            r = requests.get(THEME_LIST_URL)
            themes = r.json()
        except Exception as e:
            self.show_error(f"Fehler beim Laden: {e}")
            return
        for th in themes:
            self.add_theme_widget(Theme(**th))

    def add_theme_widget(self, theme):
        box = Gtk.Box(spacing=10)
        try:
            img = requests.get(theme.preview_url).content
            loader = GdkPixbuf.PixbufLoader.new_with_type("gif" if theme.preview_url.endswith(".gif") else "png")
            loader.write(img)
            loader.close()
            image = Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
        except:
            image = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)

        label = Gtk.Label()
        label.set_markup(f"<b>{theme.name}</b>\n{theme.description}")
        label.set_xalign(0)

        btn = Gtk.Button(label="Installieren")
        btn.connect("clicked", self.install_theme, theme)

        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, True, 0)
        box.pack_start(btn, False, False, 0)
        self.theme_box.pack_start(box, False, False, 10)
        self.show_all()

    def install_theme(self, _, theme):
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False)
            r = requests.get(theme.theme_url, stream=True)
            for chunk in r.iter_content(1024):
                if chunk:
                    tmp.write(chunk)
            tmp.flush()

            with tempfile.TemporaryDirectory() as tmpd:
                tarfile.open(tmp.name).extractall(path=tmpd)
                sub = next(os.walk(tmpd))[1][0]
                src = os.path.join(tmpd, sub)
                dst = os.path.join(THEME_DIR, theme.name)
                subprocess.run(["sudo", "mkdir", "-p", dst])
                subprocess.run(["sudo", "cp", "-r", src + "/.", dst])

                ply = next(f for f in os.listdir(dst) if f.endswith(".plymouth"))
                full = os.path.join(dst, ply)
                subprocess.run(["sudo", "update-alternatives", "--install",
                                "/usr/share/plymouth/themes/default.plymouth",
                                "default.plymouth", full, "100"])
                subprocess.run(["sudo", "update-alternatives", "--set",
                                "default.plymouth", full])
                subprocess.run(["sudo", "update-initramfs", "-u"])

            self.show_info(f"Theme '{theme.name}' installiert.")
        except Exception as e:
            self.show_error(f"Fehler: {e}")

    def show_error(self, msg):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Fehler"
        )
        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()

    def show_info(self, msg):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Information"
        )
        dialog.format_secondary_text(msg)
        dialog.run()
        dialog.destroy()

def main():
    win = ThemeManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

