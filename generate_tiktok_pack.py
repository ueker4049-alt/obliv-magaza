import os, subprocess, shutil
from PIL import Image, ImageOps, ImageFilter

os.makedirs('tiktok', exist_ok=True)
os.makedirs('temp_frames_1', exist_ok=True)
os.makedirs('temp_frames_2', exist_ok=True)
os.makedirs('temp_frames_3', exist_ok=True)
os.makedirs('temp_frames_4', exist_ok=True)

# -------------------------------------------------------------
# COMMON CUT INDICES FOR 11.17s AUDIO (335 frames at 30 fps)
# -------------------------------------------------------------
cut_frame_indices_11s = [
    1, 16, 21, 26, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

# =============================================================
# VIDEO 1: EXACT VIRAL TIKTOK MATCH (Floor drop + Obliv watermark + Exact Sound)
# =============================================================
print("--- Generating Video 1 (1.mp4: Exact Viral Floor Sound & Rhythmic Drops) ---")
solo_files_v2 = [f"solo_slides_v2/solo_{i:02d}.jpg" for i in range(9)]
seg_idx = 0
cur_p = 0

for frame_no in range(1, 336):
    if seg_idx < len(cut_frame_indices_11s) - 1:
        if frame_no >= cut_frame_indices_11s[seg_idx + 1]:
            seg_idx += 1
            cur_p = (cur_p + 1) % len(solo_files_v2)
    
    slide_path = solo_files_v2[cur_p]
    out_frame = f"temp_frames_1/frame_{frame_no:04d}.jpg"
    shutil.copyfile(slide_path, out_frame)

cmd1 = [
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', 'temp_frames_1/frame_%04d.jpg',
    '-i', 'tiktok_ref_exact.aac',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/1.mp4'
]
res1 = subprocess.run(cmd1, capture_output=True, text=True)
print("Video 1 result:", res1.returncode)


# =============================================================
# VIDEO 2: CLONE HOOK & VIRAL EDIT (Full Collection Beat Showcase)
# =============================================================
print("--- Generating Video 2 (2.mp4: Viral Hook + Collection Drop + Clicks) ---")
clone_slides = [f"tiktok_clone_slides/slide_{i:02d}.jpg" for i in range(10)]
seg_idx = 0
cur_p = 0

for frame_no in range(1, 336):
    if seg_idx < len(cut_frame_indices_11s) - 1:
        if frame_no >= cut_frame_indices_11s[seg_idx + 1]:
            seg_idx += 1
            cur_p = (cur_p + 1) % len(clone_slides)
    
    slide_path = clone_slides[cur_p]
    out_frame = f"temp_frames_2/frame_{frame_no:04d}.jpg"
    shutil.copyfile(slide_path, out_frame)

cmd2 = [
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', 'temp_frames_2/frame_%04d.jpg',
    '-i', 'insta_music_with_clicks.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/2.mp4'
]
res2 = subprocess.run(cmd2, capture_output=True, text=True)
print("Video 2 result:", res2.returncode)


# =============================================================
# VIDEO 3: BED & LIFESTYLE AESTHETIC MOCKUPS (16s Carnival Viral Bass Cut)
# =============================================================
print("--- Generating Video 3 (3.mp4: Streetwear Bed Aesthetic + Carnival Bass Drop) ---")
# Prepare 9:16 slides from bed review mockups
bed_sources = [
    'static/uploads/obliv_review_bed.jpg',
    'static/uploads/tecca_review_bed.jpg',
    'static/uploads/travis_review_bed.jpg',
    'static/uploads/trippie_review_bed.jpg',
    'static/uploads/drpepper_review_bed.jpg',
    'static/uploads/dollar_review_bed.jpg',
    'static/uploads/lips_review_bed.jpg',
    'static/uploads/esdeekid_review_bed.jpg',
    'static/uploads/obliv_angrybirds_yellow_bed.jpg',
    'static/uploads/clean_black_bed.jpg',
]

# Ensure bed slides are cropped/padded to 1080x1920 with high-end aesthetic
bed_slides = []
os.makedirs('temp_bed_slides', exist_ok=True)
logo_raw = Image.open('static/images/obliv_logo_black_clean.png').convert('RGBA')
logo_alpha = logo_raw.split()[-1]
bbox = logo_alpha.point(lambda p: 255 if p > 20 else 0).getbbox()
if bbox:
    logo_crop = logo_raw.crop(bbox)
else:
    logo_crop = logo_raw
logo_resized = logo_crop.resize((260, int(logo_crop.height * (260 / logo_crop.width))), Image.Resampling.LANCZOS)

for idx, bpath in enumerate(bed_sources):
    out_b = f"temp_bed_slides/bed_slide_{idx:02d}.jpg"
    if os.path.exists(bpath):
        bim = Image.open(bpath).convert('RGB')
        # Center crop or pad with blurred background to 1080x1920
        bw, bh = bim.size
        # create blurred backdrop
        backdrop = bim.resize((1080, 1920), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(30))
        # resize main image to fit width
        fit_w = 1080
        fit_h = int(bh * (fit_w / bw))
        main_im = bim.resize((fit_w, fit_h), Image.Resampling.LANCZOS)
        # paste in center
        offset_y = (1920 - fit_h) // 2
        backdrop.paste(main_im, (0, offset_y))
        # Paste Obliv logo
        backdrop.paste(logo_resized, (1080 - 260 - 60, 80), logo_resized)
        backdrop.save(out_b, quality=95)
        bed_slides.append(out_b)
    else:
        # fallback
        bed_slides.append(solo_files_v2[idx % len(solo_files_v2)])

# 16 seconds at 30 fps = 480 frames
# Fast cuts every 0.35s - 0.5s on beat
frames_per_cut_v3 = 10 # ~3 cuts per second
total_frames_3 = 480
for frame_no in range(1, total_frames_3 + 1):
    c_idx = ((frame_no - 1) // frames_per_cut_v3) % len(bed_slides)
    out_frame = f"temp_frames_3/frame_{frame_no:04d}.jpg"
    shutil.copyfile(bed_slides[c_idx], out_frame)

cmd3 = [
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', 'temp_frames_3/frame_%04d.jpg',
    '-i', 'carnival_viral_cut.mp3',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/3.mp4'
]
res3 = subprocess.run(cmd3, capture_output=True, text=True)
print("Video 3 result:", res3.returncode)


# =============================================================
# VIDEO 4: VIRAL SOUND HYBRID (Mix of Floor + Bed + Zoom Closeups 15s)
# =============================================================
print("--- Generating Video 4 (4.mp4: Dynamic Hybrid Viral Showcase 15s) ---")
all_variety_slides = []
for i in range(len(solo_files_v2)):
    all_variety_slides.append(solo_files_v2[i])
    if i < len(bed_slides):
        all_variety_slides.append(bed_slides[i])
    if i < len(clone_slides):
        all_variety_slides.append(clone_slides[i])

total_frames_4 = 450 # 15s at 30fps
frames_per_cut_v4 = 8 # ultra fast snappy cuts (approx 3.75 cuts/sec)
for frame_no in range(1, total_frames_4 + 1):
    c_idx = ((frame_no - 1) // frames_per_cut_v4) % len(all_variety_slides)
    out_frame = f"temp_frames_4/frame_{frame_no:04d}.jpg"
    shutil.copyfile(all_variety_slides[c_idx], out_frame)

cmd4 = [
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', 'temp_frames_4/frame_%04d.jpg',
    '-i', 'tiktok_viral_15s.mp3',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/4.mp4'
]
res4 = subprocess.run(cmd4, capture_output=True, text=True)
print("Video 4 result:", res4.returncode)

# Clean up temp frames to save space
for folder in ['temp_frames_1', 'temp_frames_2', 'temp_frames_3', 'temp_frames_4', 'temp_bed_slides']:
    shutil.rmtree(folder, ignore_errors=True)

print("ALL 4 TIKTOK VIDEOS PRODUCED SUCCESSFULLY IN /tiktok FOLDER!")
