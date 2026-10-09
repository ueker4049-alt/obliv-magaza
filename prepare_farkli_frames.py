import os, sys, subprocess, shutil, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

FONT_PATH = "LEMONMILK-Bold.otf"
LOGO_PATH = "static/images/obliv_logo_black_clean.png"

def fit_to_1080x1920(img, bg_color=(245, 245, 245)):
    """Fit an image centered into a 1080x1920 canvas with subtle blurred background or solid tone."""
    canvas = Image.new("RGB", (1080, 1920), bg_color)
    img_ratio = img.width / img.height
    target_ratio = 1080 / 1920

    # Let's create an aesthetically pleasing presentation:
    # Scale img to fit within (1080, 1550) so there's plenty of breathing room for text and top/bottom margins
    max_w, max_h = 1080, 1550
    scale = min(max_w / img.width, max_h / img.height)
    new_w, new_h = int(img.width * scale), int(img.height * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    pos_x = (1080 - new_w) // 2
    pos_y = 220 + (1450 - new_h) // 2
    canvas.paste(resized, (pos_x, pos_y))
    return canvas

def add_clean_watermark(canvas):
    """Add small Obliv logo in top-right corner"""
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            lw = 140
            lh = int(logo.height * (lw / logo.width))
            logo = logo.resize((lw, lh), Image.Resampling.LANCZOS)
            canvas.paste(logo, (1080 - lw - 50, 60), logo)
        except Exception as e:
            pass
    return canvas

def draw_centered_text(draw, lines, y_start, font, fill=(20, 20, 20), stroke_fill=None, stroke_width=0, line_spacing=18):
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font, stroke_width=stroke_width)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (1080 - w) // 2
        if stroke_fill and stroke_width > 0:
            draw.text((x, y), line, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        else:
            draw.text((x, y), line, font=font, fill=fill)
        y += h + line_spacing

def make_concept_1_frames():
    """
    CONCEPT 1: Sitede Gördüğün VS Gerçekte Üstünde Duran (Mockup vs Reality / Fit Check)
    Pairs flat t-shirts with customer mirror selfies wearing Obliv!
    """
    os.makedirs("frames_c1", exist_ok=True)
    font_title = ImageFont.truetype(FONT_PATH, 52)
    font_badge = ImageFont.truetype(FONT_PATH, 44)
    font_sub = ImageFont.truetype(FONT_PATH, 34)

    pairs = [
        # (flat_shirt, mirror_fit, shirt_name)
        ("solo_slides/solo_03.jpg", "static/uploads/prod_com_1.jpg", "TRAVIS SCOTT OVERSIZE"),
        ("solo_slides/solo_02.jpg", "static/uploads/prod_com_2.jpg", "LIL TECCA 500LBS"),
        ("solo_slides/solo_08.jpg", "static/uploads/prod_com_3.jpg", "FRANK OCEAN BLONDE"),
        ("solo_slides/solo_06.jpg", "static/uploads/prod_com_4.jpg", "LIL UZI VERT DRIP"),
        ("solo_slides/solo_01.jpg", "static/uploads/prod_com_5.jpg", "OBLIV 444 ANGEL"),
        ("solo_slides/solo_05.jpg", "static/uploads/prod_com_6.jpg", "ROLLING LIPS VINTAGE"),
        ("solo_slides/solo_00.jpg", "static/uploads/prod_com_8.jpg", "ZE PEQUENO GRAIL")
    ]

    flat_frames = []
    fit_frames = []

    for idx, (flat_p, fit_p, name) in enumerate(pairs):
        # 1. Flat frame: "SİTEDE GÖRDÜĞÜN"
        flat_img = Image.open(flat_p).convert("RGB")
        flat_canvas = fit_to_1080x1920(flat_img, bg_color=(240, 240, 240))
        add_clean_watermark(flat_canvas)
        draw = ImageDraw.Draw(flat_canvas)
        draw_centered_text(draw, ["SİTEDE GÖRDÜĞÜN", f"[{name}]"], 90, font_badge, fill=(20, 20, 20))
        draw_centered_text(draw, ["OBLIVWEAR.COM", "240 GSM HEAVYWEIGHT DROP"], 1750, font_sub, fill=(120, 120, 120))
        out_flat = f"frames_c1/pair_{idx}_flat.jpg"
        flat_canvas.save(out_flat, quality=95)
        flat_frames.append(out_flat)

        # 2. Fit frame: "GERÇEKTE ÜSTÜNDE DURUŞU 🔥"
        fit_img = Image.open(fit_p).convert("RGB")
        fit_canvas = fit_to_1080x1920(fit_img, bg_color=(18, 18, 18))
        add_clean_watermark(fit_canvas)
        draw = ImageDraw.Draw(fit_canvas)
        draw_centered_text(draw, ["GERÇEKTE ÜSTÜNDE DURAN", "MÜKEMMEL OVERSIZE KALIP"], 90, font_badge, fill=(255, 255, 255))
        draw_centered_text(draw, ["BOYUN KAPANMAZ - ASLA SOLMAZ", "LINK PROFILDE"], 1750, font_sub, fill=(200, 200, 200))
        out_fit = f"frames_c1/pair_{idx}_fit.jpg"
        fit_canvas.save(out_fit, quality=95)
        fit_frames.append(out_fit)

    print("Concept 1 frames generated successfully!")
    return pairs, flat_frames, fit_frames

def make_concept_2_frames():
    """
    CONCEPT 2: 10/10 Streetwear Rating / Tier List & Bed Lay Showcase
    Combines bed-laid aesthetic photos with clear 10/10 streetwear rating graphics!
    """
    os.makedirs("frames_c2", exist_ok=True)
    font_rating = ImageFont.truetype(FONT_PATH, 56)
    font_name = ImageFont.truetype(FONT_PATH, 42)
    font_sub = ImageFont.truetype(FONT_PATH, 34)

    items = [
        ("static/uploads/travis_review_bed.jpg", "TRAVIS SCOTT UTOPIA", "PUAN: 10/10", "ASLA ESKİMEYEN KLASİK"),
        ("static/uploads/dollar_review_bed.jpg", "ONE DOLLAR BILL TEE", "PUAN: 10/10", "STREETWEAR GRAIL"),
        ("static/uploads/drpepper_review_bed.jpg", "DR PEPPER RETRO TEE", "PUAN: 10/10", "YAZ İÇİN EN İYİ RENK"),
        ("static/uploads/lips_review_bed.jpg", "ROLLING LIPS RED TEE", "PUAN: 10/10", "DETAYLAR ÇOK İYİ"),
        ("static/uploads/tecca_review_bed.jpg", "LIL TECCA PLANET TEE", "PUAN: 10/10", "240 GSM KALIN KUMAŞ"),
        ("static/uploads/trippie_review_bed.jpg", "TRIPPIE REDD RAGE TEE", "PUAN: 10/10", "OVERSIZE DROP KALIP"),
        ("static/uploads/esdeekid_review_bed.jpg", "ESDEEKID GRAPHIC TEE", "PUAN: 10/10", "STİLİNİ YÜKSELTEN PARÇA")
    ]

    out_frames = []
    for idx, (img_p, title, score, desc) in enumerate(items):
        raw_img = Image.open(img_p).convert("RGB")
        canvas = fit_to_1080x1920(raw_img, bg_color=(25, 25, 25))
        add_clean_watermark(canvas)
        draw = ImageDraw.Draw(canvas)
        draw_centered_text(draw, [score, title], 85, font_rating, fill=(255, 255, 255))
        draw_centered_text(draw, [desc, "SINIRLI STOK | OBLIVWEAR.COM"], 1750, font_sub, fill=(200, 200, 200))
        out_p = f"frames_c2/rating_{idx}.jpg"
        canvas.save(out_p, quality=95)
        out_frames.append(out_p)

    print("Concept 2 frames generated successfully!")
    return out_frames

def make_concept_3_frames():
    """
    CONCEPT 3: Cinematic Drop Teaser & Outfit Combo
    Uses models (Travis boy & girl) + concrete t-shirts for couple/outfit drip!
    """
    os.makedirs("frames_c3", exist_ok=True)
    font_main = ImageFont.truetype(FONT_PATH, 50)
    font_sub = ImageFont.truetype(FONT_PATH, 34)

    items = [
        ("static/uploads/travis_boy.jpg", "MAN FIT CHECK", "TRAVIS SCOTT OVERSIZE"),
        ("static/uploads/travis_girl.jpg", "GIRL FIT CHECK", "UNISEX OVERSIZE VIBE"),
        ("solo_slides/solo_03.jpg", "OFFICIAL OBLIV DROP", "240 GSM SAF PAMUK"),
        ("static/uploads/prod_com_7.jpg", "OUTFIT GOALS", "SOKAK MODASI BURADA"),
        ("solo_slides/solo_08.jpg", "FRANK OCEAN BLONDE", "DETAYLARDAKİ KALİTE"),
        ("static/uploads/prod_com_2.jpg", "DAILY ROTATION", "TEK TİŞÖRTLE TÜM KOMBİN")
    ]

    out_frames = []
    for idx, (img_p, header, sub) in enumerate(items):
        raw_img = Image.open(img_p).convert("RGB")
        canvas = fit_to_1080x1920(raw_img, bg_color=(20, 20, 20))
        add_clean_watermark(canvas)
        draw = ImageDraw.Draw(canvas)
        draw_centered_text(draw, [header], 90, font_main, fill=(255, 255, 255))
        draw_centered_text(draw, [sub, "OBLIVWEAR.COM"], 1750, font_sub, fill=(200, 200, 200))
        out_p = f"frames_c3/teaser_{idx}.jpg"
        canvas.save(out_p, quality=95)
        out_frames.append(out_p)

    print("Concept 3 frames generated successfully!")
    return out_frames

if __name__ == "__main__":
    make_concept_1_frames()
    make_concept_2_frames()
    make_concept_3_frames()
