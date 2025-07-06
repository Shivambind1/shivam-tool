import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
import random
import io

# PAGE CONFIG
st.set_page_config(page_title="SHIVAM TOOL ™", layout="wide")

# CUSTOM STYLE
st.markdown("""
    <style>
    body {
        background: linear-gradient(to bottom right, #0f2027, #203a43, #2c5364);
        color: #EEE;
    }
    .block-container {
        padding: 2rem 2rem;
    }
    h1 {
        color: #FFD700;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        background: rgba(0,0,0,0.7);
        font-size: 3rem;
        font-weight: 900;
    }
    h4 {
        text-align: center;
        color: #DDDDDD;
        margin-top: -10px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #FFD700, #FFC300);
        color: black;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 16px;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, #FF8800, #FF6600);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 16px;
    }
    .stRadio, .stCheckbox, .stSelectbox, .stFileUploader {
        background: rgba(255, 255, 255, 0.08);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .css-1v0mbdj, .css-1d391kg {
        background-color: rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("""
<h1>🔆 SHIVAM TOOL ™</h1>
<h4>✨ EDIT PHOTO IN ONE CLICK – Premium Greeting Image Designer</h4>
""", unsafe_allow_html=True)

st.markdown("---")

# FILE UPLOADS
st.subheader("📌 Upload Your Files")
col1, col2, col3 = st.columns(3)
with col1:
    logo_file = st.file_uploader("🔖 Watermark / Logo (PNG)", type=["png"])
with col2:
    font_files = st.file_uploader("🔠 Custom Fonts (Optional)", type=["ttf", "otf"], accept_multiple_files=True)
with col3:
    texture_images = st.file_uploader("🌈 Texture Images (Optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

uploaded_images = st.file_uploader("🖼️ Photos to Edit", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.markdown("---")

# OPTIONS
st.subheader("⚙️ Design Options")
col4, col5 = st.columns(2)
with col4:
    greeting_choice = st.radio("🌅 Choose Greeting Text:", ["Good Morning", "Good Night"])
with col5:
    add_subtext = st.checkbox("✨ Add Subtext")

selected_subtext = None
if add_subtext:
    if greeting_choice == "Good Morning":
        selected_subtext = st.selectbox("Select Subtext", ["Have a Nice Day", "Have a Great Day"])
    else:
        selected_subtext = st.selectbox("Select Subtext", ["Sweet Dream"])

DEFAULT_FONT_PATH = "default.ttf"

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

def get_random_color():
    return tuple(random.randint(80, 255) for _ in range(3))

def draw_text_with_effects(draw, position, text, font, base_color, use_shadow, multi_color, texture_img=None):
    x, y = position
    if use_shadow:
        for dx in [-3, 3]:
            for dy in [-3, 3]:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
    if texture_img:
        mask = Image.new("L", draw.im.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text(position, text, font=font, fill=255)
        texture_resized = texture_img.resize(draw.im.size)
        draw.im.paste(texture_resized, mask=mask)
    elif multi_color:
        offset_x = 0
        for letter in text:
            color = get_random_color()
            draw.text((x + offset_x, y), letter, font=font, fill=color)
            offset_x += font.getlength(letter)
    else:
        draw.text((x, y), text, font=font, fill=base_color)

st.markdown("---")
st.subheader("✅ Ready to Make?")

output_images = []
if st.button("✨ EDIT IMAGES IN ONE CLICK"):
    if uploaded_images and logo_file:
        with st.spinner("🧪 Generating Premium Images..."):
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((300, 300))
            logo.putalpha(60)

            fonts = []
            if font_files:
                for f in font_files:
                    fonts.append(io.BytesIO(f.read()))
            else:
                with open(DEFAULT_FONT_PATH, "rb") as f:
                    fonts.append(io.BytesIO(f.read()))

            textures = []
            if texture_images:
                for t in texture_images:
                    textures.append(Image.open(t).convert("RGB"))

            for img_file in uploaded_images:
                img = Image.open(img_file).convert("RGB")
                img = crop_to_3_4(img)
                draw = ImageDraw.Draw(img)

                font_stream = random.choice(fonts)
                font_stream.seek(0)
                size = random.randint(90, 140)
                font = ImageFont.truetype(font_stream, size=size)

                base_color = get_random_color()
                pos = (30, 30)
                use_shadow = random.random() > 0.3
                multi_color = random.random() > 0.4
                use_texture = (random.random() > 0.6) and textures
                texture_img = random.choice(textures) if use_texture else None

                draw_text_with_effects(draw, pos, greeting_choice, font, base_color, use_shadow, multi_color, texture_img)

                if selected_subtext:
                    sub_font = ImageFont.truetype(font_stream, size=40)
                    sub_pos = (pos[0], pos[1] + size + 10)
                    draw.text(sub_pos, selected_subtext, font=sub_font, fill=(200, 200, 200))

                img_w, img_h = img.size
                logo_w, logo_h = logo.size
                img.paste(logo, (img_w - logo_w - 20, img_h - logo_h - 20), mask=logo)

                sign_font = ImageFont.truetype(font_stream, size=30)
                sign_pos = (10, img_h - 40)
                draw.text(sign_pos, "™ SHIVAM", font=sign_font, fill=(180, 180, 180))

                output_images.append((img_file.name, img))

        st.success("✅ All Images Processed Successfully!")

        st.markdown("---")
        st.subheader("🔎 Preview & Download")
        for idx, (name, image) in enumerate(output_images):
            st.image(image, caption=f"Preview: {name}", use_column_width=True)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="JPEG", quality=95)
            img_bytes.seek(0)
            st.download_button(
                label=f"📥 Download {name}",
                data=img_bytes,
                file_name=name,
                mime="image/jpeg",
                key=f"download_{idx}"
            )

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for name, image in output_images:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                zipf.writestr(name, img_bytes.getvalue())

        st.download_button(
            "📦 Download All Images (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="SHIVAM_TOOL_Images.zip",
            mime="application/zip"
        )

        st.markdown("<p style='text-align: center; color: #888; font-size: 12px;'>© 2025 SHIVAM TOOL™ - All Rights Reserved</p>", unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please upload at least images and logo to start.")

