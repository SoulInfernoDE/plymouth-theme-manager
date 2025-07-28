import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk

import os
import requests
import tempfile
import subprocess
import tarfile
import json

APP_ICON = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
THEME_LIST_URL = "https://raw.githubusercontent.com/SoulInfernoDE/plymouth-theme-manager/refs/heads/main/plymouth_theme_manager/themes.json"
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
        self.set_icon_from_file(APP_ICON)
        self.theme_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.theme_box)
        self.add(scrolled)
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
        box = Gtk.Box(spacing=10, margin=10)
        try:
            img_data = requests.get(theme.preview_url).content
            loader = GdkPixbuf.PixbufLoader.new_with_type("gif" if theme.preview_url.endswith(".gif") else "png")
            loader.write(img_data)
            loader.close()
            pixbuf = loader.get_pixbuf().scale_simple(192, 192, GdkPixbuf.InterpType.BILINEAR)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
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

                plymouth_file = None
                for root, _, files in os.walk(tmpd):
                    for file in files:
                        if file.endswith(".plymouth"):
                            plymouth_file = os.path.join(root, file)
                            break
                if not plymouth_file:
                    raise Exception("Keine .plymouth-Datei im Theme gefunden.")

                theme_basename = os.path.splitext(os.path.basename(plymouth_file))[0]
                target_dir = os.path.join(THEME_DIR, theme_basename)

                subprocess.run(["sudo", "mkdir", "-p", target_dir])
                subprocess.run(["sudo", "cp", "-r", os.path.dirname(plymouth_file) + "/.", target_dir])

                full_ply_path = os.path.join(target_dir, f"{theme_basename}.plymouth")
                subprocess.run(["sudo", "update-alternatives", "--install",
                                "/usr/share/plymouth/themes/default.plymouth",
                                "default.plymouth", full_ply_path, "100"])
                subprocess.run(["sudo", "update-alternatives", "--set",
                                "default.plymouth", full_ply_path])
                subprocess.run(["sudo", "update-initramfs", "-u"])

            self.show_install_success(theme_basename)
        except Exception as e:
            self.show_error(f"Fehler: {e}")

    def show_install_success(self, theme_name):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=f"Theme '{theme_name}' wurde installiert und aktiviert."
        )
        dialog.set_title("Installation erfolgreich")
        dialog.set_icon_from_file(APP_ICON)

        preview_button = Gtk.Button(label="Live-Vorschau starten")
        preview_button.connect("clicked", self.run_plymouth_preview)
        dialog.get_content_area().pack_end(preview_button, False, False, 10)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def run_plymouth_preview(self, _):
        try:
            subprocess.Popen(["pkexec", "bash", "-c",
                "plymouthd ; plymouth --show-splash ; sleep 10 ; killall plymouthd"])
        except Exception as e:
            self.show_error(f"Fehler beim Starten der Vorschau: {e}")

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

def main():
    win = ThemeManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

