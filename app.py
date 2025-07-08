import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import io
import random
import datetime
import zipfile
import time

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="🖼️ Edit Photo in Bulk Tool ™", layout="centered")

st.markdown("""
    <h1 style='text-align: center; color: white; background-color: black; padding: 15px; border-radius: 10px;'>🖼️ Edit Photo in Bulk Tool ™</h1>
    <h4 style='text-align: center; color: grey;'>Apply Greetings, Watermarks, Fonts, Wishes & More</h4>
""", unsafe_allow_html=True)

# ==================== CONSTANTS ====================
MORNING_WISHES = [
    "Have a great day!", "Start your day with a smile", "Enjoy your coffee!",
    "Fresh start today!", "Make today beautiful", "Positive vibes only"
]

NIGHT_WISHES = [
    "Sweet dreams", "Good night, sleep tight", "Peaceful rest ahead",
    "Relax and unwind", "Nighty night!", "Sleep peacefully"
]

COLORS = [
    (255, 255, 0), (255, 0, 0), (255, 255, 255),
    (255, 192, 203), (0, 255, 0), (255, 165, 0),
    (173, 216, 230), (128, 0, 128), (255, 105, 180)
]

# ==================== UTILS ====================
def list_files(folder, exts):
    if not os.path.exists(folder): return []
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
    if a > b: a, b = b, a
    return random.randint(a, b)

def overlay_text(draw, position, text, font, fill, shadow=False, outline=False):
    x, y = position
    if shadow:
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
    if outline:
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                draw.text((x + dx, y + dy), text, font=font, fill="white")
    draw.text((x, y), text, font=font, fill=fill)

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

def get_sorted_themes():
    base = "assets/overlays"
    if not os.path.exists(base):
        return []
    themes = [f for f in os.listdir(base) if os.path.isdir(os.path.join(base, f))]
    try:
        themes.sort(key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else 0, reverse=True)
    except:
        themes.sort(reverse=True)
    return themes

def overlay_theme_overlays(img, greeting_type, selected_theme, all_themes):
    base_folder = "assets/overlays"
    themes_list = get_sorted_themes()
    if selected_theme == "Auto":
        if not themes_list:
            return img
        chosen_theme = random.choice(themes_list)
    elif selected_theme == "Random":
        chosen_theme = random.choice(all_themes)
    else:
        chosen_theme = selected_theme

    theme_path = os.path.join(base_folder, chosen_theme)
    iw, ih = img.size

    if greeting_type == "Good Morning":
        overlay_numbers = [1, 2]
    elif greeting_type == "Good Night":
        overlay_numbers = [1, 3]
    else:
        overlay_numbers = [1]

    for num in overlay_numbers:
        file_path = os.path.join(theme_path, f"{num}.png")
        if os.path.exists(file_path):
            try:
                overlay = Image.open(file_path).convert("RGBA")
                ow, oh = overlay.size
                scale = 0.4
                new_w = int(iw * scale)
                new_h = int(new_w * (oh / ow))
                overlay = overlay.resize((new_w, new_h))
                if num == 1:
                    px = iw // 2 - overlay.width // 2
                    py = 40
                else:
                    px = iw // 2 - overlay.width // 2
                    py = ih - overlay.height - 40
                img.paste(overlay, (px, py), overlay)
            except Exception as e:
                print(f"Overlay error: {e}")
                continue
    return img

# ==================== SIDEBAR ====================
st.sidebar.header("🛠️ Tool Settings")
greeting_type = st.sidebar.selectbox("Greeting Type", ["Good Morning", "Good Night"])

use_overlay_checkbox = st.sidebar.checkbox("🖼️ Use Overlay Wishes Instead of Text", value=False)

all_themes = get_sorted_themes()
overlay_theme = "Auto"
if use_overlay_checkbox:
    overlay_theme = st.sidebar.selectbox("Overlay Theme", ["Auto", "Random"] + all_themes)

if use_overlay_checkbox:
    with st.sidebar.expander("🎨 Overlay Text Size Settings", expanded=False):
        good_size = st.slider("Good Text Size %", 20, 100, 40)
        wish_size = st.slider("Wish Text Size %", 10, 80, 30)

show_date = st.sidebar.checkbox("Add Today's Date", value=False)

with st.sidebar.expander("✏️ Text Settings", expanded=False):
    show_wish_text = st.checkbox("Show Wishes Text", value=True)
    coverage_percent = st.slider("Main Text Coverage (%)", 1, 100, 20)
    date_size_factor = st.slider("Date Text Size (%)", 30, 120, 70)

with st.sidebar.expander("🖌️ Font", expanded=False):
    available_fonts = list_files("assets/fonts", [".ttf", ".otf"])
    use_own_font = st.checkbox("Use Own Font?")
    if use_own_font:
        uploaded_font = st.file_uploader("Upload Your Font", type=["ttf", "otf"])
    else:
        font_file = st.selectbox("Choose Font", available_fonts)

with st.sidebar.expander("💧 Watermark Logo", expanded=False):
    available_logos = list_files("assets/logos", [".png"])
    use_own_logo = st.checkbox("Use Own Watermark?")
    if use_own_logo:
        uploaded_logo = st.file_uploader("Upload Your Logo", type=["png"])
    else:
        logo_file = st.selectbox("Choose Logo", available_logos)

uploaded_images = st.file_uploader("📁 Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# ==================== MAIN LOGIC ====================
results = []
if st.button("✅ Generate Edited Images"):
    if uploaded_images:
        with st.spinner("🌀 Processing images... Please wait."):
            animation_chars = ["🌀", "✨", "🌟", "🔄", "🔥", "⚡"]
            status_text = st.empty()

            for idx, image_file in enumerate(uploaded_images, start=1):
                status_text.markdown(f"{animation_chars[idx % len(animation_chars)]} Processing **{image_file.name}** ({idx}/{len(uploaded_images)})...")
                time.sleep(0.2)

                image = Image.open(image_file).convert("RGBA")
                image = crop_to_3_4(image)
                w, h = image.size

                if use_overlay_checkbox:
                    image = overlay_theme_overlays(
                        image.copy(),
                        greeting_type,
                        overlay_theme,
                        all_themes
                    )
                else:
                    normalized = (coverage_percent / 100) * 0.2
                    scale_factor = (normalized ** 2.5) * 2.8
                    area = scale_factor * w * h
                    main_font_size = max(30, int(area ** 0.5))
                    sub_font_size = int(main_font_size * 0.5)
                    date_font_size = int(main_font_size * date_size_factor / 100)

                    if use_own_font and uploaded_font is not None:
                        font_bytes = io.BytesIO(uploaded_font.read())
                        font_path = font_bytes
                    else:
                        font_path = os.path.join("assets/fonts", font_file)

                    main_font = ImageFont.truetype(font_path, main_font_size)
                    sub_font = ImageFont.truetype(font_path, sub_font_size)
                    date_font = ImageFont.truetype(font_path, date_font_size)

                    draw = ImageDraw.Draw(image)
                    text_color = random.choice(COLORS)
                    def_wish = random.choice(MORNING_WISHES if greeting_type == "Good Morning" else NIGHT_WISHES)
                    custom_wish = st.sidebar.text_input("Wishes Text (optional)", value="")
                    wish_text = custom_wish if custom_wish.strip() else def_wish

                    x = safe_randint(30, max(30, w - main_font_size * len(greeting_type) // 2 - 30))
                    y = safe_randint(30, max(30, h - main_font_size - 30))
                    overlay_text(draw, (x, y), greeting_type, main_font, text_color, shadow=True, outline=True)

                    if show_wish_text:
                        overlay_text(draw, (x + 10, y + main_font_size + 10), wish_text, sub_font, text_color, shadow=True)

                    if show_date:
                        today = datetime.datetime.now().strftime("%d %B %Y")
                        dx = safe_randint(30, w - 200)
                        dy = safe_randint(30, h - 50)
                        overlay_text(draw, (dx, dy), today, date_font, random.choice(COLORS), shadow=True)

                if use_own_logo and uploaded_logo is not None:
                    logo = Image.open(uploaded_logo).convert("RGBA")
                else:
                    logo_path = os.path.join("assets/logos", logo_file)
                    logo = Image.open(logo_path).convert("RGBA")
                logo.thumbnail((int(w * 0.25), int(h * 0.25)))
                image = place_logo_random(image, logo)

                final = image.convert("RGB")
                results.append((image_file.name, final))

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
