import os
import configparser

CONFIG_DIR = "/usr/share/plymouth/themes_manager"
CONFIG_FILE = os.path.join(CONFIG_DIR, "ptm.conf")

def ensure_config_file():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            f.write("[installed]\n")

def get_installed_themes():
    ensure_config_file()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config["installed"] if "installed" in config else {}

def mark_theme_installed(theme_name, gif_path):
    ensure_config_file()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if "installed" not in config:
        config["installed"] = {}
    config["installed"][theme_name] = gif_path
    with open(CONFIG_FILE, "w") as f:
        config.write(f)

def remove_installed_theme(theme_name):
    ensure_config_file()
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    if "installed" in config and theme_name in config["installed"]:
        del config["installed"][theme_name]
        with open(CONFIG_FILE, "w") as f:
            config.write(f)

