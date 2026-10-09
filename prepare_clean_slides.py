import os, glob
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "LEMONMILK-Bold.otf"
LOGO_PATH = "static/images/obliv_logo_black_clean.png"

# Text styles for different videos
TEXT_THEMES = {
    'pov': "POV: GİYİNMEYİ BİLİYORSUN",
    'rotation': "WEEKLY STREETWEAR ROTATION",
    'clean': "OBLIV 240 GSM DROP",
    'drip': "STREETWEAR GRAILS 2026",
    'swipe': "KAYDIR VE FAVORİNİ SEÇ",
    'notext': None
}

def prepare_base_slides(theme_key='pov'):
    r"""
    Takes 9 images from C:\Users\Umut\Desktop\obliv\tek_tek_tisortler\solo_00..08.jpg
    Adds LEMONMILK-Bold text (if any) and OBLIV watermark.
    Returns list of 9 PIL Images (1080x1920).
    """
    input_files = sorted(glob.glob(r'C:\Users\Umut\Desktop\obliv\tek_tek_tisortler\solo_*.jpg'))
    text = TEXT_THEMES.get(theme_key)
    
    font = ImageFont.truetype(FONT_PATH, 44) if text else None
    logo = Image.open(LOGO_PATH).convert("RGBA") if os.path.exists(LOGO_PATH) else None
    if logo:
        lw = 140
        lh = int(logo.height * (lw / logo.width))
        logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)

    slides = []
    for f in input_files:
        img = Image.open(f).convert("RGB")
        if img.size != (1080, 1920):
            img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        
        # Add logo
        if logo:
            img.paste(logo, (1080 - logo.width - 50, 60), logo)
            
        # Add centered text
        if text:
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            tx = (1080 - tw) // 2
            ty = 230
            draw.text((tx, ty), text, font=font, fill=(20, 20, 20))
            
        slides.append(img)
    return slides

if __name__ == '__main__':
    slides = prepare_base_slides('pov')
    print(f"Prepared {len(slides)} base slides.")
