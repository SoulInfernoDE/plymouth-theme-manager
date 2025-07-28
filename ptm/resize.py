from PIL import Image
import io

def scale_gif_bytes(gif_bytes, target_height):
    try:
        with Image.open(io.BytesIO(gif_bytes)) as img:
            frames = []
            for frame in range(0, img.n_frames):
                img.seek(frame)
                frame_img = img.copy()
                scale = target_height / frame_img.height
                new_width = int(frame_img.width * scale)
                frame_img = frame_img.resize((new_width, target_height), Image.ANTIALIAS)
                frames.append(frame_img.convert("RGBA"))

            output_bytes = io.BytesIO()
            frames[0].save(
                output_bytes,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                loop=0,
                transparency=0,
                disposal=2,
            )
            return output_bytes.getvalue()
    except Exception as e:
        print("Fehler bei GIF-Skalierung:", e)
        return None

