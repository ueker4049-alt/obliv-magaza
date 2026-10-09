import os
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Load font helpers
FONT_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
FONT_BLACK = r'C:\Windows\Fonts\ariblk.ttf'

def get_font(size, bold=True):
    try:
        path = FONT_BLACK if bold else FONT_BOLD
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# 9 product model names
PRODUCT_NAMES = [
    "ZE PEQUENO",
    "444 ANGEL",
    "LIL TECCA",
    "TRAVIS SCOTT",
    "TRIPPIE REDD",
    "ROLLING LIPS",
    "LIL UZI VERT",
    "I AM MUSIC",
    "FRANK OCEAN",
]

DAYS_OF_WEEK = [
    "PAZARTESİ",
    "SALI",
    "ÇARŞAMBA",
    "PERŞEMBE",
    "CUMA",
    "CUMARTESİ",
    "PAZAR",
]

def draw_pill_badge(draw, text, cx, cy, font, bg_color=(15, 15, 18, 225), text_color=(255, 255, 255, 245), pad_x=26, pad_y=12, radius=18):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    bx = cx - tw // 2
    by = cy - th // 2
    draw.rounded_rectangle([bx - pad_x, by - pad_y, bx + tw + pad_x, by + th + pad_y], radius=radius, fill=bg_color, outline=(255, 255, 255, 45), width=1)
    draw.text((bx, by - 2), text, fill=text_color, font=font)

def load_resources():
    logo_raw = Image.open("user_obliv_logo.png").convert("RGBA")
    solo_slides = [Image.open(f"solo_slides/solo_{i:02d}.jpg").convert("RGB") for i in range(9)]
    concrete_bg = Image.open("concrete_bg.jpg").convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    return logo_raw, solo_slides, concrete_bg

# -------------------------------------------------------------------------
# IDEA 1: TRAVIS SCOTT FE!N - HEAVYWEIGHT BOXY DROP
# -------------------------------------------------------------------------
def render_idea1_fein(logo_raw, solo_slides, concrete_bg):
    output_path = "tiktok/viral_fikir1_fein_heavyweight_drop.mp4"
    audio_path = "cut_travis_fein.mp3"
    print(f"\n>>> RENDERING FIKIR 1: {output_path} (Travis Scott - FE!N)")
    
    temp_dir = "temp_idea1_fein"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = 390 # 13.0s
    drop_frame = 84    # 2.8s: "FE!N!" scream & 808 drop
    
    font_main = get_font(36, bold=True)
    font_sub = get_font(24, bold=False)
    font_badge = get_font(30, bold=True)
    
    # Pre-render slide bases with top logo and bottom badges
    slide_bases = []
    lw = 440
    lh = int(logo_raw.height * (lw / logo_raw.width))
    logo_top = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
    
    for idx, slide in enumerate(solo_slides):
        s = slide.copy().convert("RGBA")
        # Place logo at top
        s.alpha_composite(logo_top, ((1080 - lw) // 2, 130))
        # Draw bottom badge
        draw = ImageDraw.Draw(s)
        badge_txt = f"{idx+1:02d} / {PRODUCT_NAMES[idx]} • 240 GSM HEAVY COTTON"
        draw_pill_badge(draw, badge_txt, 540, 1730, font_badge)
        slide_bases.append(s.convert("RGB"))

    # Beat schedule after drop: cuts every 13 frames (~0.43s)
    beat_step = 13
    
    for f_i in range(total_frames):
        if f_i < drop_frame:
            # INTRO: Dark concrete vignette with pulsing logo & teaser text
            prog = f_i / float(drop_frame)
            bg = concrete_bg.copy()
            # Dark overlay
            overlay = Image.new("RGBA", (1080, 1920), (10, 10, 14, 180))
            bg.alpha_composite(overlay)
            
            # Pulsing logo in center
            pulse = 1.0 + 0.08 * np.sin(prog * np.pi * 4)
            c_lw = int(480 * pulse)
            c_lh = int(logo_raw.height * (c_lw / logo_raw.width))
            logo_c = logo_raw.resize((c_lw, c_lh), Image.Resampling.LANCZOS)
            bg.alpha_composite(logo_c, ((1080 - c_lw) // 2, 780))
            
            # Teaser text
            draw = ImageDraw.Draw(bg)
            draw_pill_badge(draw, "POV: EN İYİ HEAVYWEIGHT BOXY TEE MARKASINI BULDUN", 540, 1140, font_main, pad_x=32, pad_y=16)
            draw_pill_badge(draw, "240 GSM SAF PAMUK • OVERSIZE KALIP • OBLIVWEAR.COM.TR", 540, 1220, font_sub, pad_x=24, pad_y=10)
            frame_img = bg.convert("RGB")
        else:
            # BEAT DROP: Rapid rhythm cut + 808 bass punch
            frames_since_drop = f_i - drop_frame
            prod_idx = (frames_since_drop // beat_step) % len(slide_bases)
            frame_in_beat = frames_since_drop % beat_step
            
            # 808 Kick punch curve: 1.05x on kick, settles in 2 frames
            if frame_in_beat == 0:
                scale = 1.05
            elif frame_in_beat == 1:
                scale = 1.025
            else:
                scale = 1.00
                
            base = slide_bases[prod_idx]
            if scale != 1.0:
                pw, ph = int(1080 * scale), int(1920 * scale)
                b_res = base.resize((pw, ph), Image.Resampling.LANCZOS)
                crop_x = (pw - 1080) // 2
                crop_y = (ph - 1920) // 2
                frame_img = b_res.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1920))
            else:
                frame_img = base
                
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("FINISHED:", output_path)

# -------------------------------------------------------------------------
# IDEA 2: KANYE WEST BOUND 2 - RATE 1-10 LOOKBOOK
# -------------------------------------------------------------------------
def render_idea2_bound2(logo_raw, solo_slides, concrete_bg):
    output_path = "tiktok/viral_fikir2_bound2_rate_collection.mp4"
    audio_path = "cut_kanye_bound2.mp3"
    print(f"\n>>> RENDERING FIKIR 2: {output_path} (Kanye West - Bound 2)")
    
    temp_dir = "temp_idea2_bound2"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = 390 # 13.0s
    
    font_header = get_font(32, bold=True)
    font_stars = get_font(30, bold=True)
    
    lw = 400
    lh = int(logo_raw.height * (lw / logo_raw.width))
    logo_top = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
    
    # 9 slides shown in 11.5s -> ~1.28s per slide (~38 frames each), last 1.5s is CTA outro
    slide_duration = 38
    
    for f_i in range(total_frames):
        if f_i < slide_duration * 9:
            s_idx = f_i // slide_duration
            frame_in_slide = f_i % slide_duration
            
            s = solo_slides[s_idx].copy().convert("RGBA")
            s.alpha_composite(logo_top, ((1080 - lw) // 2, 120))
            
            draw = ImageDraw.Draw(s)
            # Top poll header
            draw_pill_badge(draw, "RATE 1-10 • HANGİ TİŞÖRT SENİN GRAIL'İN?", 540, 240, font_header, pad_x=28, pad_y=12)
            # Bottom rating card
            badge_txt = f"★ ★ ★ ★ ★ | {PRODUCT_NAMES[s_idx]} • 240 GSM"
            draw_pill_badge(draw, badge_txt, 540, 1730, font_stars, bg_color=(12, 12, 16, 230), text_color=(255, 230, 140, 255))
            
            # Subtle smooth glide zoom
            zoom = 1.0 + 0.03 * (frame_in_slide / float(slide_duration))
            pw, ph = int(1080 * zoom), int(1920 * zoom)
            res = s.resize((pw, ph), Image.Resampling.LANCZOS)
            crop_x = (pw - 1080) // 2
            crop_y = (ph - 1920) // 2
            frame_img = res.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1920)).convert("RGB")
        else:
            # OUTRO CARD: Call to action
            bg = concrete_bg.copy()
            overlay = Image.new("RGBA", (1080, 1920), (10, 10, 14, 200))
            bg.alpha_composite(overlay)
            bg.alpha_composite(logo_top, ((1080 - lw) // 2, 650))
            draw = ImageDraw.Draw(bg)
            draw_pill_badge(draw, "EN SEVDİĞİNİ YORUMLARDA BELİRT", 540, 1000, font_header, pad_x=32, pad_y=18)
            draw_pill_badge(draw, "STOKLAR SINIRLI • OBLIVWEAR.COM.TR", 540, 1100, font_header, pad_x=28, pad_y=14)
            frame_img = bg.convert("RGB")
            
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("FINISHED:", output_path)

# -------------------------------------------------------------------------
# IDEA 3: TRIPPIE REDD MISS THE RAGE - UNDERGROUND SYNTH RAGE
# -------------------------------------------------------------------------
def render_idea3_misstherage(logo_raw, solo_slides, concrete_bg):
    output_path = "tiktok/viral_fikir3_misstherage_fast_shuffle.mp4"
    audio_path = "cut_trippie_misstherage.mp3"
    print(f"\n>>> RENDERING FIKIR 3: {output_path} (Trippie Redd - Miss The Rage)")
    
    temp_dir = "temp_idea3_rage"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = 390 # 13.0s
    drop_frame = 96    # 3.2s: Synth arp into huge bass drop
    
    font_badge = get_font(30, bold=True)
    font_intro = get_font(38, bold=True)
    
    lw = 440
    lh = int(logo_raw.height * (lw / logo_raw.width))
    logo_top = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
    
    # 9 slide bases
    slide_bases = []
    for idx, slide in enumerate(solo_slides):
        s = slide.copy().convert("RGBA")
        s.alpha_composite(logo_top, ((1080 - lw) // 2, 130))
        draw = ImageDraw.Draw(s)
        badge_txt = f"OBLIV RAGE DROP • {PRODUCT_NAMES[idx]}"
        draw_pill_badge(draw, badge_txt, 540, 1730, font_badge, bg_color=(20, 10, 30, 230), text_color=(240, 180, 255, 255))
        slide_bases.append(s.convert("RGB"))

    # Rapid high tempo cut: 10 frames per shirt (~0.33s)
    beat_step = 10
    
    for f_i in range(total_frames):
        if f_i < drop_frame:
            # INTRO: Glitchy synth build-up
            prog = f_i / float(drop_frame)
            bg = concrete_bg.copy()
            overlay = Image.new("RGBA", (1080, 1920), (15, 8, 25, 170))
            bg.alpha_composite(overlay)
            
            # Fast vibrating logo
            shake_x = int(np.random.uniform(-4, 4) * prog)
            c_lw = int(480 + 30 * np.sin(prog * np.pi * 8))
            c_lh = int(logo_raw.height * (c_lw / logo_raw.width))
            logo_c = logo_raw.resize((c_lw, c_lh), Image.Resampling.LANCZOS)
            bg.alpha_composite(logo_c, ((1080 - c_lw) // 2 + shake_x, 800))
            
            draw = ImageDraw.Draw(bg)
            draw_pill_badge(draw, "OBLIV UNDERGROUND GRAIL DROP", 540, 1150, font_intro, bg_color=(30, 10, 45, 230), text_color=(255, 160, 255, 255))
            frame_img = bg.convert("RGB")
        else:
            # RAGE DROP: Hyper-fast cuts + flash impact
            frames_since = f_i - drop_frame
            prod_idx = (frames_since // beat_step) % len(slide_bases)
            frame_in_beat = frames_since % beat_step
            
            base = slide_bases[prod_idx].copy()
            # Flash impact on first frame of each cut
            if frame_in_beat == 0:
                base_rgba = base.convert("RGBA")
                flash = Image.new("RGBA", (1080, 1920), (255, 255, 255, 75))
                base_rgba.alpha_composite(flash)
                frame_img = base_rgba.convert("RGB")
            else:
                frame_img = base
                
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("FINISHED:", output_path)

# -------------------------------------------------------------------------
# IDEA 4: LIL TECCA 500 LBS - 7 DAYS 7 FITS ROTATION
# -------------------------------------------------------------------------
def render_idea4_tecca_rotation(logo_raw, solo_slides, concrete_bg):
    output_path = "tiktok/viral_fikir4_tecca_weekly_rotation.mp4"
    audio_path = "cut_tecca_500lbs.mp3"
    print(f"\n>>> RENDERING FIKIR 4: {output_path} (Lil Tecca - 7 Days 7 Fits)")
    
    temp_dir = "temp_idea4_tecca"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = 390 # 13.0s
    intro_frames = 54  # 1.8s
    
    font_day = get_font(34, bold=True)
    font_intro = get_font(34, bold=True)
    
    lw = 400
    lh = int(logo_raw.height * (lw / logo_raw.width))
    logo_top = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
    
    # 7 Days mapped to 7 distinct products:
    # Pazartesi: 444 Angel (1)
    # Salı: Zé Pequeno (0)
    # Çarşamba: Lil Tecca (2)
    # Perşembe: Travis Scott (3)
    # Cuma: Trippie Redd (4)
    # Cumartesi: Rolling Lips (5)
    # Pazar: Frank Ocean (8)
    day_products = [1, 0, 2, 3, 4, 5, 8]
    
    day_duration = (total_frames - intro_frames) // 7 # 48 frames (~1.6s each)
    
    for f_i in range(total_frames):
        if f_i < intro_frames:
            bg = concrete_bg.copy()
            overlay = Image.new("RGBA", (1080, 1920), (12, 14, 18, 175))
            bg.alpha_composite(overlay)
            bg.alpha_composite(logo_top, ((1080 - lw) // 2, 750))
            draw = ImageDraw.Draw(bg)
            draw_pill_badge(draw, "POV: DOLABINDA SADECE BU 7 TİŞÖRT VAR", 540, 1080, font_intro, pad_x=28, pad_y=14)
            draw_pill_badge(draw, "1 HAFTALIK OUTFIT ROTASYONU", 540, 1160, font_day, bg_color=(20, 25, 30, 220), pad_x=24, pad_y=10)
            frame_img = bg.convert("RGB")
        else:
            day_idx = min(6, (f_i - intro_frames) // day_duration)
            p_idx = day_products[day_idx]
            
            s = solo_slides[p_idx].copy().convert("RGBA")
            s.alpha_composite(logo_top, ((1080 - lw) // 2, 130))
            
            draw = ImageDraw.Draw(s)
            day_name = DAYS_OF_WEEK[day_idx]
            prod_name = PRODUCT_NAMES[p_idx]
            badge_txt = f"{day_name} • {prod_name}"
            draw_pill_badge(draw, badge_txt, 540, 1730, font_day, bg_color=(15, 18, 22, 230), text_color=(255, 255, 255, 255), pad_x=32, pad_y=14)
            frame_img = s.convert("RGB")
            
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("FINISHED:", output_path)

# -------------------------------------------------------------------------
# IDEA 5: VIRAL TIKTOK AUDIO - LOOKBOOK BADGE EDITION (10.83s, 60 FPS)
# -------------------------------------------------------------------------
def render_idea5_lookbook_edition(logo_raw, solo_slides, concrete_bg):
    output_path = "tiktok/viral_fikir5_faxefxx_lookbook_edition.mp4"
    audio_path = "ref_vt_audio.mp3"
    print(f"\n>>> RENDERING FIKIR 5: {output_path} (Ref TikTok Sound - Lookbook Edition)")
    
    temp_dir = "temp_idea5_lookbook"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 60
    total_frames = 650
    
    font_badge = get_font(30, bold=True)
    
    lw = 380
    lh = int(logo_raw.height * (lw / logo_raw.width))
    logo_top = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
    
    # Pre-render slides with top logo and luxury streetwear badge
    slide_bases = []
    for idx, slide in enumerate(solo_slides):
        s = slide.copy().convert("RGBA")
        s.alpha_composite(logo_top, ((1080 - lw) // 2, 130))
        draw = ImageDraw.Draw(s)
        badge_txt = f"0{idx+1} / {PRODUCT_NAMES[idx]} • 240 GSM HEAVYWEIGHT"
        draw_pill_badge(draw, badge_txt, 540, 1730, font_badge, bg_color=(15, 15, 18, 230), text_color=(255, 255, 255, 250))
        slide_bases.append(s.convert("RGB"))

    # Exact 15 transients
    BEAT_CUTS = [214, 235, 276, 296, 337, 378, 398, 439, 459, 501, 522, 542, 563, 603, 624]
    slot_mapping = [0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 3, 1, 2, 4, 5]
    
    intervals = []
    for idx, start_f in enumerate(BEAT_CUTS):
        end_f = BEAT_CUTS[idx+1] - 1 if idx + 1 < len(BEAT_CUTS) else total_frames - 1
        intervals.append((start_f, end_f, slot_mapping[idx]))
        
    for f_i in range(total_frames):
        if f_i < BEAT_CUTS[0]:
            # Intro animation matching ref
            bg = concrete_bg.copy()
            if f_i < 50:
                c_lw, cy = 460, 960
            elif f_i < 91:
                c_lw, cy = 575, 960
            elif f_i < 132:
                c_lw, cy = 660, 960
            elif f_i < 154:
                c_lw, cy = 780, 960
            elif f_i < 185:
                prog = (f_i - 154) / (185 - 154)
                prog_e = 0.5 - 0.5 * np.cos(prog * np.pi)
                c_lw = int(460 * (1.0 - prog_e) + 380 * prog_e)
                cy = int(960 * (1.0 - prog_e) + 240 * prog_e)
            else:
                c_lw, cy = 380, 240
                
            c_lh = int(logo_raw.height * (c_lw / logo_raw.width))
            logo_scaled = logo_raw.resize((c_lw, c_lh), Image.Resampling.LANCZOS)
            bg.alpha_composite(logo_scaled, ((1080 - c_lw) // 2, cy - c_lh // 2))
            frame_img = bg.convert("RGB")
        else:
            cur_p = 0
            frames_since = 0
            for start_f, end_f, p_idx in intervals:
                if start_f <= f_i <= end_f:
                    cur_p = p_idx
                    frames_since = f_i - start_f
                    break
                    
            punch = 1.05 if frames_since == 0 else (1.025 if frames_since == 1 else 1.00)
            base = slide_bases[cur_p]
            if punch != 1.0:
                pw, ph = int(1080 * punch), int(1920 * punch)
                res = base.resize((pw, ph), Image.Resampling.LANCZOS)
                crop_x = (pw - 1080) // 2
                crop_y = (ph - 1920) // 2
                frame_img = res.crop((crop_x, crop_y, crop_x + 1080, crop_y + 1920))
            else:
                frame_img = base
                
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 10.83 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("FINISHED:", output_path)

if __name__ == '__main__':
    os.makedirs('tiktok', exist_ok=True)
    logo_raw, solo_slides, concrete_bg = load_resources()
    
    # Batch render all 5 viral concepts
    render_idea1_fein(logo_raw, solo_slides, concrete_bg)
    render_idea2_bound2(logo_raw, solo_slides, concrete_bg)
    render_idea3_misstherage(logo_raw, solo_slides, concrete_bg)
    render_idea4_tecca_rotation(logo_raw, solo_slides, concrete_bg)
    render_idea5_lookbook_edition(logo_raw, solo_slides, concrete_bg)
    print("\nALL 5 VIRAL TIKTOK CONCEPTS RENDERED SUCCESSFULLY!")
