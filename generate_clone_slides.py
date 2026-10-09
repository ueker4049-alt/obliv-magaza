import os, glob
from PIL import Image, ImageDraw, ImageFilter, ImageFont

os.makedirs('tiktok_clone_slides', exist_ok=True)

# 1. Load concrete background (1080x1920)
bg_raw = Image.open('concrete_bg.jpg').convert('RGB')
bg_base = bg_raw.resize((1080, 1920), Image.Resampling.LANCZOS)

# 2. Hook slide (Exact hook from the reference TikTok)
hook = Image.open('ysweartr_cover.jpg').convert('RGB')
w, h = hook.size
target_w, target_h = 1080, 1920
ratio = max(target_w / w, target_h / h)
new_w, new_h = int(w * ratio), int(h * ratio)
hook_resized = hook.resize((new_w, new_h), Image.Resampling.LANCZOS)
left = (new_w - target_w) // 2
top = (new_h - target_h) // 2
hook_slide = hook_resized.crop((left, top, left + target_w, top + target_h))
hook_slide.save('tiktok_clone_slides/slide_00.jpg', quality=95)
print("Slide 00 hook saved.")

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

def paste_tshirt_with_shadow(bg_image, tshirt_img, center_x, center_y, target_width, angle=0):
    tw, th = tshirt_img.size
    ratio = target_width / float(tw)
    new_w, new_h = int(tw * ratio), int(th * ratio)
    ts = tshirt_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    if angle != 0:
        ts = ts.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        
    ts_w, ts_h = ts.size
    
    alpha = ts.split()[-1]
    shadow_pad = 70
    shadow_canvas = Image.new('RGBA', (ts_w + shadow_pad * 2, ts_h + shadow_pad * 2), (0, 0, 0, 0))
    shadow_tint = Image.new('RGBA', (ts_w, ts_h), (25, 28, 32, 130))
    shadow_tint.putalpha(alpha.point(lambda a: int(a * 0.42)))
    
    shadow_canvas.paste(shadow_tint, (shadow_pad + 10, shadow_pad + 20), shadow_tint)
    shadow_blurred = shadow_canvas.filter(ImageFilter.GaussianBlur(26))
    
    bg_rgba = bg_image.convert('RGBA')
    sh_topleft = (int(center_x - ts_w / 2 - shadow_pad), int(center_y - ts_h / 2 - shadow_pad))
    bg_rgba.alpha_composite(shadow_blurred, sh_topleft)
    
    ts_topleft = (int(center_x - ts_w / 2), int(center_y - ts_h / 2))
    bg_rgba.alpha_composite(ts, ts_topleft)
    
    return bg_rgba.convert('RGB')

# Slide 1: Main hero t-shirt centered (Obliv Zé Pequeno), adjacent sleeve peek on right
s1 = bg_base.copy()
s1 = paste_tshirt_with_shadow(s1, tshirts[1], center_x=1200, center_y=880, target_width=920, angle=14)
s1 = paste_tshirt_with_shadow(s1, tshirts[0], center_x=450, center_y=870, target_width=980, angle=-12)
s1.save('tiktok_clone_slides/slide_01.jpg', quality=95)

# Slide 2: Obliv 444 Angel left, Lil Tecca right
s2 = bg_base.copy()
s2 = paste_tshirt_with_shadow(s2, tshirts[1], center_x=150, center_y=870, target_width=960, angle=-14)
s2 = paste_tshirt_with_shadow(s2, tshirts[2], center_x=880, center_y=890, target_width=960, angle=12)
s2.save('tiktok_clone_slides/slide_02.jpg', quality=95)

# Slide 3: Lil Tecca left, Travis Scott Cactus right
s3 = bg_base.copy()
s3 = paste_tshirt_with_shadow(s3, tshirts[2], center_x=150, center_y=870, target_width=960, angle=-14)
s3 = paste_tshirt_with_shadow(s3, tshirts[3], center_x=880, center_y=890, target_width=960, angle=12)
s3.save('tiktok_clone_slides/slide_03.jpg', quality=95)

# Slide 4: Travis Scott left, Trippie Redd 1400 right
s4 = bg_base.copy()
s4 = paste_tshirt_with_shadow(s4, tshirts[3], center_x=150, center_y=870, target_width=960, angle=-14)
s4 = paste_tshirt_with_shadow(s4, tshirts[4], center_x=880, center_y=890, target_width=960, angle=12)
s4.save('tiktok_clone_slides/slide_04.jpg', quality=95)

# Slide 5: Trippie Redd left, Rolling Lips Acid right
s5 = bg_base.copy()
s5 = paste_tshirt_with_shadow(s5, tshirts[4], center_x=150, center_y=870, target_width=960, angle=-14)
s5 = paste_tshirt_with_shadow(s5, tshirts[5], center_x=880, center_y=890, target_width=960, angle=12)
s5.save('tiktok_clone_slides/slide_05.jpg', quality=95)

# Slide 6: Rolling Lips left, Lil Uzi Vert right
s6 = bg_base.copy()
s6 = paste_tshirt_with_shadow(s6, tshirts[5], center_x=150, center_y=870, target_width=960, angle=-14)
s6 = paste_tshirt_with_shadow(s6, tshirts[6], center_x=880, center_y=890, target_width=960, angle=12)
s6.save('tiktok_clone_slides/slide_06.jpg', quality=95)

# Slide 7: Lil Uzi Vert left, I Am Music right
s7 = bg_base.copy()
s7 = paste_tshirt_with_shadow(s7, tshirts[6], center_x=150, center_y=870, target_width=960, angle=-14)
s7 = paste_tshirt_with_shadow(s7, tshirts[7], center_x=880, center_y=890, target_width=960, angle=12)
s7.save('tiktok_clone_slides/slide_07.jpg', quality=95)

# Slide 8: I Am Music left, Frank Ocean Blonde right
s8 = bg_base.copy()
s8 = paste_tshirt_with_shadow(s8, tshirts[7], center_x=150, center_y=870, target_width=960, angle=-14)
s8 = paste_tshirt_with_shadow(s8, tshirts[8], center_x=880, center_y=890, target_width=960, angle=12)
s8.save('tiktok_clone_slides/slide_08.jpg', quality=95)

# Slide 9: Frank Ocean Blonde centered as final hero, previous on far left
s9 = bg_base.copy()
s9 = paste_tshirt_with_shadow(s9, tshirts[7], center_x=-100, center_y=880, target_width=920, angle=-16)
s9 = paste_tshirt_with_shadow(s9, tshirts[8], center_x=540, center_y=870, target_width=980, angle=8)
s9.save('tiktok_clone_slides/slide_09.jpg', quality=95)

print("Regenerated all slides with authentic angled flat-lay styling.")
