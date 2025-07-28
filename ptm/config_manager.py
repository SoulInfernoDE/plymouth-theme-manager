import os
import configparser

CONFIG_DIR = "/usr/share/plymouth/themes_manager"
CONFIG_PATH = os.path.join(CONFIG_DIR, "ptm.conf")

def ensure_dirs():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    # Auch Verzeichnis für konvertierte GIFs anlegen
    from .resize import CONVERTED_DIR
    if not os.path.exists(CONVERTED_DIR):
        os.makedirs(CONVERTED_DIR, exist_ok=True)

def ensure_config():
    ensure_dirs()
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            f.write("[converted_gifs]\n\n[installed_themes]\n\n[current_theme]\n")

def load_config():
    ensure_config()
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    for section in ["converted_gifs", "installed_themes", "current_theme"]:
        if not config.has_section(section):
            config.add_section(section)
    return config

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        config.write(f)

