import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import io
import random
import datetime
import zipfile
import time

# =================== PAGE CONFIG ===================
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply Greetings, Watermarks, Fonts, Wishes & More</h4>
""", unsafe_allow_html=True)

# =================== UTILS ===================
def list_files(folder, exts):
    if not os.path.exists(folder):
        return []
    return [f for f in os.listdir(folder) if any(f.lower().endswith(ext) for ext in exts)]

def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))

def safe_randint(a, b):
    if a > b:
        a, b = b, a
    return random.randint(a, b)

def place_logo_random(img, logo):
    w, h = img.size
    logo_w, logo_h = logo.size
    max_x = max(0, w - logo_w - 30)
    max_y = max(0, h - logo_h - 30)
    x = safe_randint(20, max_x)
    y = safe_randint(20, max_y)
    opacity = random.uniform(0.45, 1.0)
    watermark = logo.copy()
    watermark = ImageEnhance.Brightness(watermark).enhance(opacity)
    img.paste(watermark, (x, y), watermark)
    return img

def overlay_theme_overlays(img, greeting_type):
    base_folder = "assets/overlays"
    themes = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    if not themes:
        return img

    chosen_theme = random.choice(themes)
    theme_path = os.path.join(base_folder, chosen_theme)

    overlays_to_add = ["GOOD"]
    if greeting_type == "Good Morning":
        overlays_to_add += ["MORNING", "HAVEANICEDAY"]
    elif greeting_type == "Good Night":
        overlays_to_add += ["NIGHT", "SWEETDREAM"]

    iw, ih = img.size

    for overlay_name in overlays_to_add:
        file_path = os.path.join(theme_path, f"{overlay_name}.png")
        if os.path.exists(file_path):
            try:
                overlay = Image.open(file_path).convert("RGBA")
                ow, oh = overlay.size

                scale = random.uniform(0.2, 0.4)
                overlay = overlay.resize((int(iw * scale), int(oh * scale)))

                px = safe_randint(30, iw - overlay.width - 30)
                py = safe_randint(30, ih - overlay.height - 30)

                img.paste(overlay, (px, py), overlay)
            except Exception as e:
                print(f"Overlay error: {e}")
                continue
    return img

# =================== SIDEBAR ===================
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])
use_png_overlay = st.sidebar.checkbox("🖼️ Use PNG Overlay Wishes Instead of Text", value=True)
show_date = st.sidebar.checkbox("Add Today's Date", value=False)

available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
font_file = st.sidebar.selectbox("Choose Font (for text mode only)", available_fonts)

available_logos = list_files("assets/logos", [".png"])
logo_file = st.sidebar.selectbox("Choose Watermark Logo", available_logos)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

results = []

# =================== MAIN ===================
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait."):

            status_text = st.empty()
            logo_path = os.path.join("assets/logos", logo_file)
            font_path = os.path.join("assets/fonts", font_file) if font_file else None

            for idx, image_file in enumerate(uploaded_images, start=1):
                try:
                    status_text.markdown(f"🔧 Processing **{image_file.name}** ({idx}/{len(uploaded_images)})...")
                    time.sleep(0.2)

                    image = Image.open(image_file).convert("RGBA")
                    image = crop_to_3_4(image)
                    w, h = image.size

                    if use_png_overlay:
                        image = overlay_theme_overlays(image.copy(), greeting_type)
                    else:
                        # Fallback to text rendering if someone unchecks overlays
                        if font_path:
                            draw = ImageDraw.Draw(image)
                            main_font = ImageFont.truetype(font_path, 80)
                            color = (255, 255, 255)
                            x = safe_randint(30, w - 300)
                            y = safe_randint(30, h - 150)
                            draw.text((x, y), greeting_type, font=main_font, fill=color)

                    if show_date:
                        if font_path:
                            draw = ImageDraw.Draw(image)
                            date_font = ImageFont.truetype(font_path, 50)
                            today = datetime.datetime.now().strftime("%d %B %Y")
                            dx = safe_randint(30, w - 300)
                            dy = safe_randint(30, h - 100)
                            draw.text((dx, dy), today, font=date_font, fill=(255, 255, 255))

                    logo = Image.open(logo_path).convert("RGBA")
                    logo.thumbnail((int(w * 0.25), int(h * 0.25)))
                    image = place_logo_random(image, logo)

                    final = image.convert("RGB")
                    results.append((image_file.name, final))

                except Exception as e:
                    st.error(f"❌ Error Occurred: {str(e)}")

            status_text.success("✅ All images processed successfully!")

        for name, img in results:
            st.image(img, caption=name, use_container_width=True)
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=100, optimize=True)
            renamed = f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg"
            st.download_button(
                label=f"⬇️ Download {renamed}",
                data=img_bytes.getvalue(),
                file_name=renamed,
                mime="image/jpeg"
            )

# =================== ZIP DOWNLOAD ===================
if results:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for _, img in results:
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=100, optimize=True)
            zipf.writestr(f"Picsart_{datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S-%f')}.jpg", img_bytes.getvalue())
    zip_buffer.seek(0)

    st.download_button(
        label="📦 Download All as ZIP",
        data=zip_buffer,
        file_name="Shivam_Images.zip",
        mime="application/zip"
    )
else:
    st.info("📂 Upload and generate images first to enable ZIP download.")
