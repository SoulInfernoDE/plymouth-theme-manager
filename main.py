import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import os
import requests
import tempfile
import subprocess
import tarfile
import json
import shutil

THEME_LIST_URL = "https://raw.githubusercontent.com/SoulInfernoDE/plymouth-theme-manager/refs/heads/main/plymouth_theme_manager/themes.json?token=GHSAT0AAAAAADIEEW36CO5DWG7BYRJKSBSW2EG53RA"
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
                # Entpacke Archiv
                tarfile.open(tmp.name).extractall(path=tmpd)
                # Suche nach .plymouth Datei
                plymouth_file = None
                for root, _, files in os.walk(tmpd):
                    for file in files:
                        if file.endswith(".plymouth"):
                            plymouth_file = os.path.join(root, file)
                            break
                if not plymouth_file:
                    raise Exception("Keine .plymouth-Datei im Theme gefunden.")

                # Zielordnername aus Dateiname ableiten
                theme_basename = os.path.splitext(os.path.basename(plymouth_file))[0]
                target_dir = os.path.join(THEME_DIR, theme_basename)

                # Kopiere Dateien
                subprocess.run(["sudo", "mkdir", "-p", target_dir])
                subprocess.run(["sudo", "cp", "-r", os.path.dirname(plymouth_file) + "/.", target_dir])

                # Theme als Standard setzen
                full_ply_path = os.path.join(target_dir, f"{theme_basename}.plymouth")
                subprocess.run(["sudo", "update-alternatives", "--install",
                                "/usr/share/plymouth/themes/default.plymouth",
                                "default.plymouth", full_ply_path, "100"])
                subprocess.run(["sudo", "update-alternatives", "--set",
                                "default.plymouth", full_ply_path])
                subprocess.run(["sudo", "update-initramfs", "-u"])

            self.show_info(f"Theme '{theme_basename}' installiert und aktiviert.")
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

