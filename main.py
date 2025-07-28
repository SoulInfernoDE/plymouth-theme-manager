import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import os
import requests
import json
from ptm.resize import get_or_create_scaled_gif

APP_ICON_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
CONFIG_DIR = "/usr/share/plymouth/themes_manager"
CONFIG_FILE = os.path.join(CONFIG_DIR, "ptm.conf")
LOCAL_THEME_CACHE = os.path.join(CONFIG_DIR, "themes.json")
THEMES_JSON_URL = "https://raw.githubusercontent.com/SoulInfernoDE/plymouth-theme-manager/refs/heads/main/plymouth_theme_manager/themes.json"


class ThemeManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Plymouth Theme Manager")
        self.set_default_size(800, 600)
        self.set_icon_from_file(APP_ICON_PATH)

        # Hauptlayout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Menüleiste
        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)

        # Menü: Aktionen
        aktionen_menu = Gtk.Menu()
        aktionen_item = Gtk.MenuItem(label="Aktionen")
        aktionen_item.set_submenu(aktionen_menu)

        install_item = Gtk.MenuItem(label="Installieren")
        install_item.connect("activate", self.on_install_view)
        aktionen_menu.append(install_item)

        uninstall_item = Gtk.MenuItem(label="Deinstallieren")
        uninstall_item.connect("activate", self.on_uninstall_view)
        aktionen_menu.append(uninstall_item)

        change_item = Gtk.MenuItem(label="Theme ändern")
        change_item.connect("activate", self.on_change_view)
        aktionen_menu.append(change_item)

        # Menü: Hilfe
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Hilfe")
        help_item.set_submenu(help_menu)

        about_item = Gtk.MenuItem(label="Über")
        about_item.connect("activate", self.on_about)
        help_menu.append(about_item)

        menubar.append(aktionen_item)
        menubar.append(help_item)

        # Stack für verschiedene Ansichten
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        vbox.pack_start(self.stack, True, True, 0)

        # Installieren-Ansicht
        self.install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.stack.add_titled(self.install_box, "install", "Installieren")

        self.theme_listbox = Gtk.ListBox()
        self.install_box.pack_start(self.theme_listbox, True, True, 0)

        icon = Gtk.Image.new_from_file(APP_ICON_PATH)
        icon.set_halign(Gtk.Align.CENTER)
        self.install_box.pack_end(icon, False, False, 10)

        self.load_themes()

    def on_install_view(self, widget):
        self.stack.set_visible_child_name("install")

    def on_uninstall_view(self, widget):
        print("Uninstall View – noch nicht implementiert")

    def on_change_view(self, widget):
        print("Change View – noch nicht implementiert")

    def on_about(self, widget):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name("Plymouth Theme Manager")
        dialog.set_version("1.0")
        dialog.set_website("https://github.com/SoulInfernoDE/plymouth-theme-manager")
        dialog.set_website_label("Projekt auf GitHub")
        dialog.set_comments("Open Source Software von SoulInfernoDE\nIcons von https://icons8.de")
        dialog.set_logo(Gtk.Image.new_from_file(APP_ICON_PATH).get_pixbuf())
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()

    def load_themes(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            r = requests.get(THEMES_JSON_URL)
            r.raise_for_status()
            with open(LOCAL_THEME_CACHE, "w") as f:
                f.write(r.text)
        except Exception as e:
            print("Fehler beim Herunterladen der themes.json:", e)

        try:
            with open(LOCAL_THEME_CACHE, "r") as f:
                themes = json.load(f)
        except Exception as e:
            print("Fehler beim Laden der themes.json:", e)
            themes = []

        for theme in themes:
            self.add_theme_row(theme)

    def add_theme_row(self, theme):
        name = theme.get("name")
        preview_url = theme.get("preview_url")
        theme_url = theme.get("theme_url")

        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)
        row.add(box)

        label = Gtk.Label(label=name)
        label.set_xalign(0.5)
        box.pack_start(label, False, False, 0)

        image = Gtk.Image()
        try:
            scaled_path = get_or_create_scaled_gif(name, preview_url)
            anim = GdkPixbuf.PixbufAnimation.new_from_file(scaled_path)
            image.set_from_animation(anim)
        except Exception as e:
            print("Bild konnte nicht geladen werden:", e)
            image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)

        image.set_halign(Gtk.Align.CENTER)
        box.pack_start(image, False, False, 0)

        self.theme_listbox.add(row)
        self.theme_listbox.show_all()


def main():
    win = ThemeManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()

