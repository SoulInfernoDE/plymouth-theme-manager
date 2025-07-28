import gi
gi.require_version('Gtk', '3.0')
import os
import requests
import json
from ptm.resize import get_or_create_scaled_gif
from ptm.theme_handler import install_theme, uninstall_theme_full as uninstall_theme
from ptm.config import mark_theme_installed, remove_installed_theme, get_installed_themes

from gi.repository import Gtk, GdkPixbuf

APP_ICON_PATH = os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')
CONFIG_DIR = "/usr/share/plymouth/themes_manager"
CONFIG_FILE = os.path.join(CONFIG_DIR, "ptm.conf")
LOCAL_THEME_CACHE = os.path.join(CONFIG_DIR, "themes.json")
THEMES_JSON_URL = "https://raw.githubusercontent.com/SoulInfernoDE/plymouth-theme-manager/refs/heads/main/plymouth_theme_manager/themes.json"

class ThemeManager(Gtk.Window):
    def __init__(self):
        super().__init__(title="Plymouth Theme Manager")
        self.set_default_size(800, 600)
        self.set_icon_name("application-x-executable")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        menubar = Gtk.MenuBar()
        vbox.pack_start(menubar, False, False, 0)

        aktionen_menu = Gtk.Menu()
        aktionen_item = Gtk.MenuItem(label="Aktionen")
        aktionen_item.set_submenu(aktionen_menu)

        install_item = Gtk.MenuItem(label="Installieren")
        install_item.connect("activate", self.on_install_view)
        aktionen_menu.append(install_item)

        uninstall_item = Gtk.MenuItem(label="Deinstallieren")
        uninstall_item.connect("activate", self.on_uninstall_view)
        aktionen_menu.append(uninstall_item)

        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Hilfe")
        help_item.set_submenu(help_menu)

        about_item = Gtk.MenuItem(label="Über")
        about_item.connect("activate", self.on_about)
        help_menu.append(about_item)

        menubar.append(aktionen_item)
        menubar.append(help_item)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        vbox.pack_start(self.stack, True, True, 0)

        self.install_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.stack.add_titled(self.install_box, "install", "Installieren")

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(2)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.flowbox)
        self.install_box.pack_start(scroll, True, True, 0)

        icon = Gtk.Image.new_from_file(APP_ICON_PATH)
        icon.set_halign(Gtk.Align.CENTER)
        self.install_box.pack_end(icon, False, False, 10)

        self.sync_installed_themes()
        self.load_themes()

    def on_install_view(self, widget):
        self.stack.set_visible_child_name("install")

    def on_uninstall_view(self, widget):
        installed = get_installed_themes()
        dialog = Gtk.Dialog(title="Theme deinstallieren", parent=self, flags=0)
        dialog.set_default_size(400, 300)
        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("Deinstallieren", Gtk.ResponseType.OK)

        box = dialog.get_content_area()
        combo = Gtk.ComboBoxText()
        for theme_name in installed:
            combo.append_text(theme_name)
        combo.set_active(0)
        box.add(combo)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected = combo.get_active_text()
            if selected:
                if uninstall_theme(selected):
                    remove_installed_theme(selected)
                    print(f"{selected} erfolgreich deinstalliert.")
                else:
                    print(f"Deinstallation von {selected} fehlgeschlagen.")
        dialog.destroy()

    def on_about(self, widget):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name("Plymouth Theme Manager")
        dialog.set_version("1.0")
        dialog.set_website("https://github.com/SoulInfernoDE/plymouth-theme-manager")
        dialog.set_website_label("Projekt auf GitHub")
        dialog.set_comments("Open Source Software von SoulInfernoDE Icons: https://icons8.de")
        dialog.set_logo(Gtk.Image.new_from_file(APP_ICON_PATH).get_pixbuf())
        dialog.set_transient_for(self)
        dialog.run()
        dialog.destroy()

    def sync_installed_themes(self):
        import subprocess

        try:
            output = subprocess.check_output(["sudo", "update-alternatives", "--list", "default.plymouth"], text=True)
            paths = [line.strip() for line in output.splitlines() if line.strip()]
        except Exception as e:
            print("Fehler beim Ausführen von update-alternatives:", e)
            paths = []

        for path in paths:
            if not path.endswith(".plymouth"):
                continue
            name = os.path.basename(os.path.dirname(path))
            gif_path = os.path.join("/usr/share/icons/animated/themes", f"{name}_preview.gif")
            if os.path.exists(gif_path):
                mark_theme_installed(name, gif_path)

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

        installed_themes = get_installed_themes()

        for theme in themes:
            self.add_theme_card(theme, installed_themes)

        rows = (len(themes) + 1) // 2
        height = min(200 * rows + 120, 1000)
        self.set_default_size(800, height)

    def add_theme_card(self, theme, installed_themes):
        name = theme.get("name")
        preview_url = theme.get("preview_url")
        theme_url = theme.get("theme_url")

        frame = Gtk.Frame()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        frame.add(box)

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

        install_btn = Gtk.Button(label="Installieren")
        install_btn.connect("clicked", self.on_install_clicked, name, theme_url, preview_url, box)
        box.pack_start(install_btn, False, False, 0)

        preview_btn = Gtk.Button(label="Live Vorschau")
        preview_btn.set_visible(name in installed_themes)
        preview_btn.connect("clicked", self.on_preview_clicked, name)
        box.pack_start(preview_btn, False, False, 0)

        frame.show_all()
        self.flowbox.add(frame)
        install_btn.preview_btn = preview_btn

    def on_install_clicked(self, button, theme_name, theme_url, preview_url, box):
        print(f"Installiere Theme: {theme_name}")
        success = install_theme(theme_name, theme_url)
        if success:
            gif_path = get_or_create_scaled_gif(theme_name, preview_url)
            mark_theme_installed(theme_name, gif_path)
            preview_btn = getattr(button, "preview_btn", None)
            if preview_btn:
                preview_btn.set_visible(True)

    def on_preview_clicked(self, button, theme_name):
        print(f"Starte einmalige Vorschau für: {theme_name}")
        os.system("pgrep plymouthd || sudo plymouthd")
        os.system("sudo plymouth --show-splash; sleep 5; sudo plymouth quit")

def main():
    win = ThemeManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
