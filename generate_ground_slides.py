import os
from PIL import Image, ImageFilter, ImageOps

os.makedirs('solo_slides_v2', exist_ok=True)

# 1. Base floor background (1080x1920)
bg_raw = Image.open('real_floor.jpg').convert('RGB')
bg_base = bg_raw.resize((1080, 1920), Image.Resampling.LANCZOS)

# 2. OBLIV Logo for top-right
logo_raw = Image.open('static/images/obliv_logo_black_clean.png').convert('RGBA')
# Crop transparent padding around logo
logo_alpha = logo_raw.split()[-1]
logo_bbox = logo_alpha.point(lambda p: 255 if p > 20 else 0).getbbox()
if logo_bbox:
    logo_cropped = logo_raw.crop(logo_bbox)
else:
    logo_cropped = logo_raw

# Resize logo for top-right corner (width ~ 240px)
target_logo_w = 250
logo_ratio = target_logo_w / float(logo_cropped.width)
target_logo_h = int(logo_cropped.height * logo_ratio)
logo_final = logo_cropped.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)

# Position: Top-right corner (x=1080 - 250 - 60 = 770, y=80)
logo_pos = (1080 - target_logo_w - 65, 85)

# 3. Clean t-shirt loader
def load_and_clean_tshirt(path):
    im = Image.open(path).convert('RGBA')
    alpha = im.split()[-1]
    mask = alpha.point(lambda p: 255 if p > 25 else 0)
    bbox = mask.getbbox()
    if bbox:
        x1, y1, x2, y2 = bbox
        x1 = max(0, x1 - 4)
        y1 = max(0, y1 - 4)
        x2 = min(im.width, x2 + 4)
        y2 = min(im.height, y2 + 4)
        im = im.crop((x1, y1, x2, y2))
    return im

product_files = [
    'static/uploads/obliv.png',       # 0: Obliv Zé Pequeno
    'static/uploads/t-1.png',         # 1: Obliv 444 Angel
    'static/uploads/lil_tecca.png',   # 2: Lil Tecca
    'static/uploads/travis_scott.png',# 3: Travis Scott Cactus
    'static/uploads/trippie_red.png', # 4: Trippie Redd 1400
    'static/uploads/lips.png',        # 5: Rolling Lips Acid
    'static/uploads/lil_uzi_vert.png',# 6: Lil Uzi Vert
    'static/uploads/i_am_music.png',  # 7: I Am Music
    'static/uploads/frank_ocean.png', # 8: Frank Ocean Blonde
]

tshirts = [load_and_clean_tshirt(pf) for pf in product_files]

def render_ground_laid_slide(tshirt_img, angle=0, target_width=930, center_x=540, center_y=990):
    # Resize tshirt
    tw, th = tshirt_img.size
    ratio = target_width / float(tw)
    new_w, new_h = int(tw * ratio), int(th * ratio)
    ts = tshirt_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Slight casual streetwear floor tilt
    if angle != 0:
        ts = ts.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        
    ts_w, ts_h = ts.size
    alpha = ts.split()[-1]
    
    # Multi-layer authentic floor contact shadow:
    # 1) Direct tight contact crease shadow (dark, close)
    pad = 80
    c_shadow = Image.new('RGBA', (ts_w + pad * 2, ts_h + pad * 2), (0, 0, 0, 0))
    c_tint = Image.new('RGBA', (ts_w, ts_h), (25, 25, 28, 160))
    c_tint.putalpha(alpha.point(lambda a: int(a * 0.55)))
    c_shadow.paste(c_tint, (pad + 6, pad + 14), c_tint)
    c_blurred = c_shadow.filter(ImageFilter.GaussianBlur(12))
    
    # 2) Diffused ambient floor occlusion shadow (soft, wider)
    a_shadow = Image.new('RGBA', (ts_w + pad * 2, ts_h + pad * 2), (0, 0, 0, 0))
    a_tint = Image.new('RGBA', (ts_w, ts_h), (35, 38, 42, 90))
    a_tint.putalpha(alpha.point(lambda a: int(a * 0.35)))
    a_shadow.paste(a_tint, (pad + 12, pad + 28), a_tint)
    a_blurred = a_shadow.filter(ImageFilter.GaussianBlur(32))
    
    # Composite onto floor
    canvas = bg_base.copy().convert('RGBA')
    topleft_pad = (int(center_x - ts_w / 2 - pad), int(center_y - ts_h / 2 - pad))
    canvas.alpha_composite(a_blurred, topleft_pad)
    canvas.alpha_composite(c_blurred, topleft_pad)
    
    # Paste t-shirt
    topleft_ts = (int(center_x - ts_w / 2), int(center_y - ts_h / 2))
    canvas.alpha_composite(ts, topleft_ts)
    
    # Place OBLIV Logo in Top-Right
    canvas.alpha_composite(logo_final, logo_pos)
    
    return canvas.convert('RGB')

# Angles for authentic laid-out streetwear floor photography
angles = [-12, 10, -9, 11, -10, 8, -11, 9, -5]

for i, (ts, ang) in enumerate(zip(tshirts, angles)):
    slide = render_ground_laid_slide(ts, angle=ang, target_width=940, center_x=540, center_y=1010)
    slide.save(f'solo_slides_v2/solo_{i:02d}.jpg', quality=95)
    print(f"Saved solo_slides_v2/solo_{i:02d}.jpg")

print("All floor-laid slides with logo generated successfully!")
