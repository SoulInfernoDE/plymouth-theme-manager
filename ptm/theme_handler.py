import os
import subprocess
import shutil
import tarfile
import tempfile
import requests
from ptm.config import mark_theme_installed, remove_installed_theme, get_installed_themes

PLYMOUTH_THEMES_DIR = "/usr/share/plymouth/themes"
PREVIEW_DIR = "/usr/share/icons/animated/themes"

def install_theme(theme_name, download_url):
    tmp_dir = tempfile.mkdtemp(prefix="ptm_install_")
    tar_path = os.path.join(tmp_dir, f"{theme_name}.tar.gz")

    try:
        r = requests.get(download_url, stream=True, timeout=30)
        r.raise_for_status()
        with open(tar_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=tmp_dir)

        found = None
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith(".plymouth"):
                    found = os.path.join(root, file)
                    break
            if found:
                break

        if not found:
            print("❌ .plymouth-Datei nicht gefunden im Archiv")
            return False

        real_name = os.path.splitext(os.path.basename(found))[0]
        theme_dir = os.path.join(PLYMOUTH_THEMES_DIR, real_name)
        os.makedirs(theme_dir, exist_ok=True)

        extracted_root = os.path.dirname(found)
        for item in os.listdir(extracted_root):
            s = os.path.join(extracted_root, item)
            d = os.path.join(theme_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        plymouth_target = os.path.join(theme_dir, f"{real_name}.plymouth")
        subprocess.run([
            "sudo", "update-alternatives", "--install",
            "/usr/share/plymouth/themes/default.plymouth",
            "default.plymouth",
            plymouth_target,
            "100"
        ], check=True)

        subprocess.run(["sudo", "update-initramfs", "-u"], check=True)
        return True

    except Exception as e:
        print(f"❌ Fehler bei Installation von {theme_name}: {e}")
        return False

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

def uninstall_theme_full(theme_name):
    plymouth_path = os.path.join(PLYMOUTH_THEMES_DIR, theme_name, f"{theme_name}.plymouth")

    try:
        if os.path.exists(plymouth_path):
            subprocess.run([
                "sudo", "update-alternatives", "--remove", "default.plymouth", plymouth_path
            ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Entfernen aus update-alternatives: {e}")
        return False

    theme_dir = os.path.join(PLYMOUTH_THEMES_DIR, theme_name)
    if os.path.isdir(theme_dir):
        try:
            shutil.rmtree(theme_dir)
            print(f"Theme-Verzeichnis {theme_dir} gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen des Theme-Verzeichnisses: {e}")

    gif_path = os.path.join(PREVIEW_DIR, f"{theme_name}_preview.gif")
    if os.path.exists(gif_path):
        try:
            os.remove(gif_path)
            print(f"Vorschau-Datei {gif_path} gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen der Vorschau-Datei: {e}")

    remove_installed_theme(theme_name)

    try:
        subprocess.run(["sudo", "update-initramfs", "-uk", "all"], check=True)
    except Exception as e:
        print(f"Fehler beim Aktualisieren von initramfs: {e}")

    return True
