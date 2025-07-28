import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

import os
import requests
import tempfile
import io

from ptm import resize  # resize.py im ptm Ordner

APP_ICON = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
THEME_LIST_URL = "https://raw.githubusercontent.com/SoulInfernoDE/plymouth-theme-manager/main/plymouth_theme_manager/themes.json"

class Theme:
    def __init__(self, name, preview_url, download_url):
        self.name = name
        self.preview_url = preview_url
        self.download_url = download_url

class ThemeManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Plymouth Theme Manager")
        self.set_default_size(600, 400)
        self.set_border_width(10)
        self.set_icon_from_file(APP_ICON)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)

        # Datei Menü
        filemenu = Gtk.Menu()
        filem = Gtk.MenuItem(label="Datei")
        filem.set_submenu(filemenu)
        quit_item = Gtk.MenuItem(label="Beenden")
        quit_item.connect("activate", Gtk.main_quit)
        filemenu.append(quit_item)

        # Ansicht Menü
        viewmenu = Gtk.Menu()
        viewm = Gtk.MenuItem(label="Ansicht")
        viewm.set_submenu(viewmenu)
        install_item = Gtk.MenuItem(label="Installieren")
        install_item.connect("activate", self.show_install)
        viewmenu.append(install_item)
        uninstall_item = Gtk.MenuItem(label="Deinstallieren")
        uninstall_item.connect("activate", self.show_uninstall)
        viewmenu.append(uninstall_item)
        change_item = Gtk.MenuItem(label="Theme ändern")
        change_item.connect("activate", self.show_change)
        viewmenu.append(change_item)

        # Hilfe Menü
        helpmenu = Gtk.Menu()
        helpm = Gtk.MenuItem(label="Hilfe")
        helpm.set_submenu(helpmenu)
        about_item = Gtk.MenuItem(label="Über")
        about_item.connect("activate", self.show_about)
        helpmenu.append(about_item)

        menubar.append(filem)
        menubar.append(viewm)
        menubar.append(helpm)

        # Icon mit Abstand oben erzeugen (statt set_padding)
        icon_image = Gtk.Image.new_from_file(APP_ICON)
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        icon_box.set_margin_top(40)  # 40px Abstand oben
        icon_box.set_margin_bottom(30)
        icon_box.set_halign(Gtk.Align.CENTER)
        icon_box.pack_start(icon_image, False, False, 0)

        vbox.pack_start(icon_box, False, False, 0)

        self.theme_listbox = Gtk.ListBox()
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.theme_listbox)
        vbox.pack_start(scrolled, True, True, 0)

        self.themes = []

        self.fetch_themes()

    def fetch_themes(self):
        try:
            response = requests.get(THEME_LIST_URL)
            response.raise_for_status()
            themes_json = response.json()
            self.themes.clear()
            self.theme_listbox.foreach(lambda w: self.theme_listbox.remove(w))
            for t in themes_json:
                # Sicherstellen, dass download_url existiert
                if 'download_url' not in t:
                    print(f"Warnung: Theme {t.get('name', '<unbekannt>')} hat kein 'download_url'-Feld, wird übersprungen.")
                    continue
                theme = Theme(t["name"], t["preview_url"], t["download_url"])
                self.themes.append(theme)
                self.add_theme_widget(theme)
        except Exception as e:
            self.show_error(f"Fehler beim Laden der Themes: {e}")

    def add_theme_widget(self, theme):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, margin=10)

        image = Gtk.Image()
        try:
            img_data = requests.get(theme.preview_url).content
            if theme.preview_url.lower().endswith(".gif"):
                temp_gif_path = resize.scale_gif_bytes(img_data, target_height=192)
                if temp_gif_path:
                    pix_anim = GdkPixbuf.PixbufAnimation.new_from_file(temp_gif_path)
                    image.set_from_animation(pix_anim)
                else:
                    image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
            else:
                loader = GdkPixbuf.PixbufLoader.new_with_type("png")
                loader.write(img_data)
                loader.close()
                pixbuf = loader.get_pixbuf()
                scale = 192 / pixbuf.get_height()
                width = int(pixbuf.get_width() * scale)
                scaled = pixbuf.scale_simple(width, 192, GdkPixbuf.InterpType.BILINEAR)
                image.set_from_pixbuf(scaled)
        except Exception as e:
            print(f"Bild konnte nicht geladen werden: {e}")
            image.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)

        hbox.pack_start(image, False, False, 0)

        label = Gtk.Label(label=theme.name)
        label.set_xalign(0)
        hbox.pack_start(label, True, True, 0)

        row.add(hbox)
        self.theme_listbox.add(row)
        self.theme_listbox.show_all()

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

    def show_install(self, widget):
        pass  # Noch zu implementieren

    def show_uninstall(self, widget):
        pass  # Noch zu implementieren

    def show_change(self, widget):
        pass  # Noch zu implementieren

    def show_about(self, widget):
        about = Gtk.AboutDialog()
        about.set_program_name("Plymouth Theme Manager")
        about.set_version("1.0")
        about.set_comments("Open Source Software von SoulInfernoDE")
        about.set_website("https://github.com/SoulInfernoDE/plymouth-theme-manager")
        about.set_website_label("Projekt auf GitHub")
        about.set_icon_from_file(APP_ICON)
        about.set_transient_for(self)
        about.run()
        about.destroy()

def main():
    app = ThemeManager()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

