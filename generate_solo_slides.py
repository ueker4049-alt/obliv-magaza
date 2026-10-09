import os
from PIL import Image, ImageFilter

os.makedirs('solo_slides', exist_ok=True)

# 1. Load concrete background (1080x1920)
bg_raw = Image.open('concrete_bg.jpg').convert('RGB')
bg_base = bg_raw.resize((1080, 1920), Image.Resampling.LANCZOS)

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

def render_solo_slide(tshirt_img, angle=0, target_width=920, center_x=540, center_y=960):
    tw, th = tshirt_img.size
    ratio = target_width / float(tw)
    new_w, new_h = int(tw * ratio), int(th * ratio)
    ts = tshirt_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    if angle != 0:
        ts = ts.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        
    ts_w, ts_h = ts.size
    
    alpha = ts.split()[-1]
    shadow_pad = 80
    shadow_canvas = Image.new('RGBA', (ts_w + shadow_pad * 2, ts_h + shadow_pad * 2), (0, 0, 0, 0))
    shadow_tint = Image.new('RGBA', (ts_w, ts_h), (20, 24, 28, 140))
    shadow_tint.putalpha(alpha.point(lambda a: int(a * 0.45)))
    
    shadow_canvas.paste(shadow_tint, (shadow_pad + 12, shadow_pad + 24), shadow_tint)
    shadow_blurred = shadow_canvas.filter(ImageFilter.GaussianBlur(30))
    
    bg_rgba = bg_base.copy().convert('RGBA')
    sh_topleft = (int(center_x - ts_w / 2 - shadow_pad), int(center_y - ts_h / 2 - shadow_pad))
    bg_rgba.alpha_composite(shadow_blurred, sh_topleft)
    
    ts_topleft = (int(center_x - ts_w / 2), int(center_y - ts_h / 2))
    bg_rgba.alpha_composite(ts, ts_topleft)
    
    return bg_rgba.convert('RGB')

# Angles for each product to look natural yet punchy
angles = [-3, 2.5, -2, 3, -2.5, 2, -3, 2.5, -1]

for i, (ts, ang) in enumerate(zip(tshirts, angles)):
    slide = render_solo_slide(ts, angle=ang, target_width=940, center_x=540, center_y=960)
    slide.save(f'solo_slides/solo_{i:02d}.jpg', quality=95)
    print(f"Saved solo_{i:02d}.jpg")

print("All solo slides generated successfully!")
