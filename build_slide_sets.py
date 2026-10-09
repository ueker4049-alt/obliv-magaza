import os, glob
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "LEMONMILK-Bold.otf"
LOGO_PATH = "static/images/obliv_logo_black_clean.png"

def make_clean_slides(text=None):
    r"""
    Takes 9 images from C:\Users\Umut\Desktop\obliv\tek_tek_tisortler\solo_*.jpg
    Applies Lemon Milk Bold text (if provided) and Obliv logo watermark.
    """
    input_files = sorted(glob.glob(r'C:\Users\Umut\Desktop\obliv\tek_tek_tisortler\solo_*.jpg'))
    font = ImageFont.truetype(FONT_PATH, 44) if text else None
    
    logo = None
    if os.path.exists(LOGO_PATH):
        try:
            raw_logo = Image.open(LOGO_PATH).convert("RGBA")
            lw = 140
            lh = int(raw_logo.height * (lw / raw_logo.width))
            logo = raw_logo.resize((lw, lh), Image.Resampling.LANCZOS)
        except Exception:
            pass

    slides = []
    for f in input_files:
        img = Image.open(f).convert("RGB")
        if img.size != (1080, 1920):
            img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
        
        if logo:
            img.paste(logo, (1080 - logo.width - 50, 60), logo)
            
        if text:
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            tx = (1080 - tw) // 2
            ty = 230
            draw.text((tx, ty), text, font=font, fill=(20, 20, 20))
            
        slides.append(img)
    return slides

def make_transparent_tshirt_slides(text=None, bg_color=(242, 242, 244)):
    r"""
    Takes 9 transparent PNGs from C:\Users\Umut\Desktop\obliv\t shirt\*.png
    Places them cleanly centered on a modern minimalist studio streetwear canvas (1080x1920).
    Adds Lemon Milk Bold text and logo watermark.
    """
    input_files = sorted(glob.glob(r'C:\Users\Umut\Desktop\obliv\t shirt\*.png'))
    font = ImageFont.truetype(FONT_PATH, 44) if text else None
    
    logo = None
    if os.path.exists(LOGO_PATH):
        try:
            raw_logo = Image.open(LOGO_PATH).convert("RGBA")
            lw = 140
            lh = int(raw_logo.height * (lw / raw_logo.width))
            logo = raw_logo.resize((lw, lh), Image.Resampling.LANCZOS)
        except Exception:
            pass

    slides = []
    for f in input_files:
        png_img = Image.open(f).convert("RGBA")
        
        # Create solid canvas
        canvas = Image.new("RGBA", (1080, 1920), bg_color + (255,))
        
        # Scale t-shirt nicely (width ~ 960)
        target_w = 980
        target_h = int(png_img.height * (target_w / png_img.width))
        resized = png_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Center in canvas, leaving breathing room for text at top
        pos_x = (1080 - target_w) // 2
        pos_y = 350 + (1450 - target_h) // 2
        
        canvas.paste(resized, (pos_x, pos_y), resized)
        
        if logo:
            canvas.paste(logo, (1080 - logo.width - 50, 60), logo)
            
        if text:
            draw = ImageDraw.Draw(canvas)
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            tx = (1080 - tw) // 2
            ty = 230
            draw.text((tx, ty), text, font=font, fill=(20, 20, 20))
            
        slides.append(canvas.convert("RGB"))
    return slides
