import os, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

# 1. Prepare Base Branded Slides with LEMON MILK font and top-right logo
os.makedirs('solo_slides_branded_lemon', exist_ok=True)
os.makedirs('solo_slides_branded_lemon/zooms', exist_ok=True)

logo_raw = Image.open('static/images/obliv_logo_black_clean.png').convert('RGBA')
logo_alpha = logo_raw.split()[-1]
bbox = logo_alpha.point(lambda p: 255 if p > 20 else 0).getbbox()
logo_cropped = logo_raw.crop(bbox) if bbox else logo_raw
target_logo_w = 260
logo_ratio = target_logo_w / float(logo_cropped.width)
target_logo_h = int(logo_cropped.height * logo_ratio)
logo_final = logo_cropped.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)
logo_pos = (1080 - target_logo_w - 55, 75)

text = 'POV: GIYINMEYI BILIYORSUN'
font = ImageFont.truetype('LEMONMILK-Bold.otf', 46)

def apply_text_and_logo(img):
    img.paste(logo_final, logo_pos, logo_final)
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (1080 - tw) // 2
    y = 230
    draw.text((x + 2, y + 2), text, font=font, fill=(185, 185, 185))
    draw.text((x, y), text, font=font, fill=(15, 15, 15))
    return img

branded_slides = []
zoom_slides = []

for i in range(9):
    slide_path = f'solo_slides/solo_{i:02d}.jpg'
    img = Image.open(slide_path).convert('RGB')
    img = apply_text_and_logo(img)
    out_b = f'solo_slides_branded_lemon/slide_{i:02d}.jpg'
    img.save(out_b, quality=95)
    branded_slides.append(out_b)
    
    # Zoom variation
    w, h = img.size
    crop_w, crop_h = int(w / 1.15), int(h / 1.15)
    cx, cy = w // 2, int(h * 0.52)
    left = cx - crop_w // 2
    top = cy - crop_h // 2
    raw_img = Image.open(slide_path).convert('RGB')
    zoomed = raw_img.crop((left, top, left + crop_w, top + crop_h)).resize((1080, 1920), Image.Resampling.LANCZOS)
    zoomed = apply_text_and_logo(zoomed)
    out_z = f'solo_slides_branded_lemon/zooms/slide_{i:02d}_zoom.jpg'
    zoomed.save(out_z, quality=95)
    zoom_slides.append(out_z)

print("Base Lemon Milk slides prepared!")

# 2. Rhythmic cut templates (Immediate action from frame 1 - NO FREEZE at start!)
cut_indices_instant_11s = [
    1, 7, 13, 19, 25, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

def generate_frames_sequence(style, total_frames):
    seq = []
    if style == 'signature_fast_start':
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_indices_instant_11s) - 1 and f >= cut_indices_instant_11s[seg_idx + 1]:
                seg_idx += 1
                cur_p = (cur_p + 1) % len(branded_slides)
            seq.append(branded_slides[cur_p])
            
    elif style == 'punch_zoom_bounce':
        cut_len = 7
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            seq.append(zoom_slides[idx] if chunk % 2 else branded_slides[idx])
            
    elif style == 'bass_drop_punch':
        cut_len = 8
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            seq.append(zoom_slides[idx] if chunk % 2 else branded_slides[idx])
            
    elif style == 'smooth_streetwear_cut':
        cut_len = 8
        order = [branded_slides[i] for i in [0, 2, 4, 6, 8, 1, 3, 5, 7]]
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(order)
            seq.append(order[idx])
            
    elif style == 'fast_drop_sync':
        cut_len = 6 # snappy 5 cuts per second
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            seq.append(branded_slides[idx])
            
    elif style == 'tempo_acceleration':
        cuts = [10, 10, 9, 9, 8, 8, 7, 7, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5]
        cur_f = 0
        p_idx = 0
        for c in cuts:
            for _ in range(c):
                if len(seq) < total_frames:
                    seq.append(branded_slides[p_idx % len(branded_slides)])
            p_idx += 1
        while len(seq) < total_frames:
            seq.append(branded_slides[p_idx % len(branded_slides)])
            p_idx += 1
            
    elif style == 'high_energy_pulse':
        cut_len = 7
        order = [branded_slides[i] for i in [2, 0, 7, 3, 8, 1, 6, 4, 5]]
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(order)
            seq.append(order[idx])
            
    if len(seq) < total_frames:
        seq += [branded_slides[0]] * (total_frames - len(seq))
    return seq[:total_frames]

# 3. Master Build: 7 distinct atılacak videos with 7 completely unique songs
final_tasks = [
    ('atılacak2.mp4', 'tiktok_ref_exact.aac', 11.11, 'signature_fast_start'),
    ('atılacak3.mp4', 'song_brazilian_drop_12s.mp3', 12.00, 'punch_zoom_bounce'),
    ('atılacak5.mp4', 'carnival_viral_cut.mp3', 16.00, 'bass_drop_punch'),
    ('atılacak6.mp4', 'song_no_fear_drop_13s.mp3', 13.00, 'smooth_streetwear_cut'),
    ('atılacak8.mp4', 'song_moonshine_drop_12s.mp3', 12.00, 'fast_drop_sync'),
    ('atılacak9.mp4', 'song_one_chance_drop_14s.mp3', 14.00, 'tempo_acceleration'),
    ('atılacak14.mp4', 'song_violento_drop_13s.mp3', 13.00, 'high_energy_pulse'),
]

os.makedirs('tiktok', exist_ok=True)

for fname, song, dur, style in final_tasks:
    out_video = os.path.join('tiktok', fname)
    temp_dir = 'temp_render_final'
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = int(dur * fps)
    frames = generate_frames_sequence(style, total_frames)
    
    for i, slide_path in enumerate(frames, 1):
        shutil.copyfile(slide_path, f"{temp_dir}/frame_{i:04d}.jpg")
        
    cmd = [
        'ffmpeg', '-y',
        '-framerate', '30',
        '-i', f'{temp_dir}/frame_%04d.jpg',
        '-i', song,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-g', '30',
        '-keyint_min', '15',
        '-sc_threshold', '0',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        out_video
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"SUCCESS: Rendered {fname} ({dur}s | Song: {song} | Style: {style})")

print("ALL 7 ATILACAK VIDEOS PERFECTLY RE-RENDERED WITH UNIQUE SONGS AND INSTANT SMOOTH TRANSITIONS!")
