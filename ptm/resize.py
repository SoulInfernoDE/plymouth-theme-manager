import io
import tempfile
from PIL import Image, ImageSequence

def scale_gif_bytes(gif_bytes, target_height=192):
    """
    Skaliert eine GIF-Animation aus Bytes auf die gewünschte Höhe,
    behält das Seitenverhältnis bei und speichert das Ergebnis temporär als GIF-Datei.
    Gibt den Pfad zur temporären GIF-Datei zurück oder None bei Fehlern.
    """
    try:
        im = Image.open(io.BytesIO(gif_bytes))
        frames = []
        scale = target_height / im.height
        target_width = int(im.width * scale)

        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            resized_frame = frame.resize((target_width, target_height), Image.LANCZOS)
            frames.append(resized_frame)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".gif")
        frames[0].save(
            temp_file.name,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=im.info.get('duration', 100),
            disposal=2
        )
        temp_file.close()
        return temp_file.name

    except Exception as e:
        print(f"Fehler bei GIF Skalierung: {e}")
        return None

