import os
import subprocess

PLYMOUTH_THEMES_DIR = "/usr/share/plymouth/themes/"
ANIMATED_THEMES_DIR = "/usr/share/icons/animated/themes"

def get_installed_themes():
    # Prüfe, welche Themes via update-alternatives registriert sind
    try:
        output = subprocess.check_output(
            ["update-alternatives", "--list", "default.plymouth"], text=True
        )
        themes = [os.path.dirname(line.strip()) for line in output.splitlines()]
        return themes
    except Exception as e:
        print("Fehler bei Abfrage installierter Themes:", e)
        return []

def install_theme(theme_name, download_url):
    # Hier Beispielimplementierung: entpacke Tarball in themes dir
    import requests
    import tarfile
    import tempfile
    import shutil

    tmp_dir = tempfile.mkdtemp(prefix="ptm_install_")
    tar_path = os.path.join(tmp_dir, "theme.tar.gz")

    try:
        r = requests.get(download_url, stream=True, timeout=30)
        r.raise_for_status()
        with open(tar_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=PLYMOUTH_THEMES_DIR)

        print(f"Theme {theme_name} installiert")
        return True
    except Exception as e:
        print(f"Fehler bei Installation von {theme_name}: {e}")
        return False
    finally:
        shutil.rmtree(tmp_dir)

def uninstall_theme(theme_name):
    # Entfernt Theme-Verzeichnis, wenn vorhanden
    theme_path = os.path.join(PLYMOUTH_THEMES_DIR, theme_name)
    if os.path.exists(theme_path):
        try:
            import shutil
            shutil.rmtree(theme_path)
            print(f"Theme {theme_name} deinstalliert")
            return True
        except Exception as e:
            print(f"Fehler bei Deinstallation von {theme_name}: {e}")
            return False
    else:
        print(f"Theme {theme_name} nicht gefunden zum Deinstallieren")
        return False

