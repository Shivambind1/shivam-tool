
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io
import random

st.set_page_config(page_title="✨ GOOD VIBES TOOL", layout="centered")

# --- Header ---
st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #f9d423, #ff4e50);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            color: white;
            margin-bottom: 20px;
        }
        .main-header h1 {
            font-size: 50px;
            margin: 0;
            font-weight: bold;
        }
        .main-header p {
            font-size: 20px;
            margin-top: 8px;
        }
        .section-title {
            color: #e67e22;
            font-weight: bold;
            font-size: 20px;
            margin-top: 20px;
        }
    </style>
    <div class='main-header'>
        <h1>✨ GOOD VIBES ✨</h1>
        <p>Focus on Stunning Good Morning / Good Night Edits</p>
    </div>
""", unsafe_allow_html=True)

# --- Upload Section ---
st.markdown("<div class='section-title'>📌 Upload Section</div>", unsafe_allow_html=True)
logo_file = st.file_uploader("Watermark logo (PNG transparent recommended)", type=["png"])
font_files = st.file_uploader("Custom fonts (.ttf/.otf)", type=["ttf", "otf"], accept_multiple_files=True)
uploaded_images = st.file_uploader("Photos to Edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# --- Text Settings ---
st.markdown("<div class='section-title'>📝 Text Settings</div>", unsafe_allow_html=True)
mode = st.selectbox("Main Greeting", ["Good Morning", "Good Night"])
extra_line_opt = st.checkbox("Add Sub-line (e.g. Have a Nice Day / Sweet Dreams)")
text_size = st.slider("Main Text Size", 100, 250, 150, step=10)
subtext_size = int(text_size * 0.35)

# --- Crop Helper ---
def crop_to_3_4(img):
    w, h = img.size
    target_ratio = 3 / 4
    current_ratio = w / h
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    return img

# --- Load Fonts ---
available_fonts = []
if font_files:
    for f in font_files:
        available_fonts.append(io.BytesIO(f.read()))
else:
    try:
        with open("default/default.ttf", "rb") as f:
            available_fonts.append(io.BytesIO(f.read()))
    except FileNotFoundError:
        available_fonts.append(None)

# --- Processing Button ---
output_images = []

if st.button("✅ Generate Edited Images"):
    if uploaded_images and logo_file:
        with st.spinner("Processing images..."):

            # Watermark logo
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((50, 50))
            logo = logo.copy()
            alpha = logo.split()[-1].point(lambda p: p * 0.3)
            logo.putalpha(alpha)

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                # Load font
                font_stream = random.choice(available_fonts)
                if font_stream:
                    font_stream.seek(0)
                    try:
                        main_font = ImageFont.truetype(font_stream, size=text_size)
                        sub_font = ImageFont.truetype(font_stream, size=subtext_size)
                    except:
                        main_font = ImageFont.load_default()
                        sub_font = ImageFont.load_default()
                else:
                    main_font = ImageFont.load_default()
                    sub_font = ImageFont.load_default()

                # Main & Sub Text
                main_text = mode
                sub_text = None
                if extra_line_opt:
                    if mode == "Good Morning":
                        sub_text = random.choice(["Have a Nice Day", "Have a Great Day"])
                    else:
                        sub_text = random.choice(["Sweet Dreams", "Sleep Well"])

                # Fancy color
                text_color = tuple(random.randint(140, 255) for _ in range(3))
                outline_color = "black"

                # Random position (top, center, bottom)
                x = 30
                y_choices = [40, img.height//2 - text_size//2, img.height - text_size - 120]
                y = random.choice(y_choices)

                # Outline+shadow to make BOLD
                for dx in [-4, -2, 0, 2, 4]:
                    for dy in [-4, -2, 0, 2, 4]:
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), main_text, font=main_font, fill=outline_color)

                # Main text
                draw.text((x, y), main_text, font=main_font, fill=text_color)

                # Subtext
                if sub_text:
                    draw.text((x + 10, y + text_size + 10), sub_text, font=sub_font, fill=(200, 200, 200))

                # Logo bottom-right
                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 15, img_h - logo_h - 15), mask=logo)

                output_images.append((img_file.name, img))

        # Zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.success("✅ All photos are ready!")

        # Preview
        st.markdown("<div class='section-title'>📸 Preview</div>", unsafe_allow_html=True)
        for name, image in output_images:
            st.image(image.resize((300, 400)), caption=name)

        # Download
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📦 Download All (ZIP)", data=zip_buffer.getvalue(), file_name="GoodVibes.zip", mime="application/zip")
        with col2:
            for name, img in output_images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="JPEG")
                st.download_button(f"⬇️ {name}", data=img_bytes.getvalue(), file_name=name, mime="image/jpeg")
    else:
        st.warning("⚠️ Please upload a logo and at least one photo!")
