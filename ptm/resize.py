import os
from PIL import Image
from io import BytesIO
import requests

SCALED_DIR = "/usr/share/icons/animated/themes"

def get_or_create_scaled_gif(theme_name, preview_url):
    os.makedirs(SCALED_DIR, exist_ok=True)
    gif_path = os.path.join(SCALED_DIR, f"{theme_name}_preview.gif")

    if os.path.exists(gif_path):
        return gif_path

    response = requests.get(preview_url)
    response.raise_for_status()

    img_bytes = BytesIO(response.content)
    try:
        img = Image.open(img_bytes)
        frames = []
        for frame in range(img.n_frames):
            img.seek(frame)
            frame_img = img.copy()
            frame_img = frame_img.convert("RGBA")
            ratio = 192 / img.height
            new_width = int(img.width * ratio)
            frame_img = frame_img.resize((new_width, 192), Image.LANCZOS)
            frames.append(frame_img)

        frames[0].save(gif_path, save_all=True, append_images=frames[1:], loop=0, duration=img.info.get('duration', 100))
        return gif_path
    except Exception as e:
        print("Fehler bei GIF-Skalierung:", e)
        raise

