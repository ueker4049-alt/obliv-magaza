import os, subprocess, shutil
from PIL import Image

# 1. Setup paths
os.makedirs('tiktok', exist_ok=True)
os.makedirs('solo_slides_branded', exist_ok=True)
os.makedirs('solo_slides_branded/zooms', exist_ok=True)

# 2. Prepare OBLIV Logo in top-right for all solo_slides
logo_raw = Image.open('static/images/obliv_logo_black_clean.png').convert('RGBA')
logo_alpha = logo_raw.split()[-1]
bbox = logo_alpha.point(lambda p: 255 if p > 20 else 0).getbbox()
logo_cropped = logo_raw.crop(bbox) if bbox else logo_raw

target_logo_w = 260
logo_ratio = target_logo_w / float(logo_cropped.width)
target_logo_h = int(logo_cropped.height * logo_ratio)
logo_final = logo_cropped.resize((target_logo_w, target_logo_h), Image.Resampling.LANCZOS)
logo_pos = (1080 - target_logo_w - 55, 75)

branded_slides = []
zoom_slides = []

for i in range(9):
    slide_path = f'solo_slides/solo_{i:02d}.jpg'
    img = Image.open(slide_path).convert('RGB')
    
    # Standard branded slide
    branded_path = f'solo_slides_branded/slide_{i:02d}.jpg'
    img.paste(logo_final, logo_pos, logo_final)
    img.save(branded_path, quality=95)
    branded_slides.append(branded_path)
    
    # Dynamic 1.15x punch-in zoom slide
    w, h = img.size
    crop_w, crop_h = int(w / 1.15), int(h / 1.15)
    cx, cy = w // 2, int(h * 0.52)
    left = cx - crop_w // 2
    top = cy - crop_h // 2
    zoomed = img.crop((left, top, left + crop_w, top + crop_h)).resize((1080, 1920), Image.Resampling.LANCZOS)
    zoomed.paste(logo_final, logo_pos, logo_final)
    zoom_path = f'solo_slides_branded/zooms/slide_{i:02d}_zoom.jpg'
    zoomed.save(zoom_path, quality=95)
    zoom_slides.append(zoom_path)

print(f"Branded {len(branded_slides)} solo_slides with top-right OBLIV logo.")

# Common cut markers for 11.17s audio (335 frames at 30 fps)
cut_frame_indices_11s = [
    1, 16, 21, 26, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

# =============================================================
# VIDEO 1: EXACT VIRAL TIKTOK AUDIO (Teresa..vsp original sound)
# =============================================================
print("--- Generating tiktok/1.mp4 ---")
temp_dir_1 = 'temp_render_1'
os.makedirs(temp_dir_1, exist_ok=True)
seg_idx = 0
cur_p = 0
for frame_no in range(1, 336):
    if seg_idx < len(cut_frame_indices_11s) - 1:
        if frame_no >= cut_frame_indices_11s[seg_idx + 1]:
            seg_idx += 1
            cur_p = (cur_p + 1) % len(branded_slides)
    slide_path = branded_slides[cur_p]
    shutil.copyfile(slide_path, f"{temp_dir_1}/frame_{frame_no:04d}.jpg")

subprocess.run([
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', f'{temp_dir_1}/frame_%04d.jpg',
    '-i', 'tiktok_ref_exact.aac',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/1.mp4'
], check=True)
shutil.rmtree(temp_dir_1, ignore_errors=True)
print("1.mp4 rendered.")

# =============================================================
# VIDEO 2: VIRAL CLICK BEAT & SHUFFLED ORDER
# =============================================================
print("--- Generating tiktok/2.mp4 ---")
temp_dir_2 = 'temp_render_2'
os.makedirs(temp_dir_2, exist_ok=True)
# Shuffled sequence of solo slides: [1, 3, 0, 5, 2, 7, 4, 8, 6]
shuffled_order = [1, 3, 0, 5, 2, 7, 4, 8, 6]
shuffled_slides = [branded_slides[i] for i in shuffled_order]
seg_idx = 0
cur_p = 0
for frame_no in range(1, 336):
    if seg_idx < len(cut_frame_indices_11s) - 1:
        if frame_no >= cut_frame_indices_11s[seg_idx + 1]:
            seg_idx += 1
            cur_p = (cur_p + 1) % len(shuffled_slides)
    slide_path = shuffled_slides[cur_p]
    shutil.copyfile(slide_path, f"{temp_dir_2}/frame_{frame_no:04d}.jpg")

subprocess.run([
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', f'{temp_dir_2}/frame_%04d.jpg',
    '-i', 'insta_music_with_clicks.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/2.mp4'
], check=True)
shutil.rmtree(temp_dir_2, ignore_errors=True)
print("2.mp4 rendered.")

# =============================================================
# VIDEO 3: CARNIVAL VIRAL BASS DROP WITH ALTERNATING ZOOM POP
# =============================================================
print("--- Generating tiktok/3.mp4 ---")
temp_dir_3 = 'temp_render_3'
os.makedirs(temp_dir_3, exist_ok=True)
# 16 seconds at 30 fps = 480 frames
total_frames_3 = 480
# Pair standard with zoom for rhythmic camera punch
punch_sequence = []
for i in range(len(branded_slides)):
    punch_sequence.append(branded_slides[i])
    punch_sequence.append(zoom_slides[i])

frames_per_cut_3 = 10 # ~0.33s cut per punch
for frame_no in range(1, total_frames_3 + 1):
    c_idx = ((frame_no - 1) // frames_per_cut_3) % len(punch_sequence)
    shutil.copyfile(punch_sequence[c_idx], f"{temp_dir_3}/frame_{frame_no:04d}.jpg")

subprocess.run([
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', f'{temp_dir_3}/frame_%04d.jpg',
    '-i', 'carnival_viral_cut.mp3',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/3.mp4'
], check=True)
shutil.rmtree(temp_dir_3, ignore_errors=True)
print("3.mp4 rendered.")

# =============================================================
# VIDEO 4: VIRAL SOUND 15s ULTRA FAST DROP (solo_slides only)
# =============================================================
print("--- Generating tiktok/4.mp4 ---")
temp_dir_4 = 'temp_render_4'
os.makedirs(temp_dir_4, exist_ok=True)
total_frames_4 = 450 # 15s at 30fps
frames_per_cut_4 = 7 # ~0.23s rapid beat-sync switch
for frame_no in range(1, total_frames_4 + 1):
    c_idx = ((frame_no - 1) // frames_per_cut_4) % len(branded_slides)
    shutil.copyfile(branded_slides[c_idx], f"{temp_dir_4}/frame_{frame_no:04d}.jpg")

subprocess.run([
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', f'{temp_dir_4}/frame_%04d.jpg',
    '-i', 'tiktok_viral_15s.mp3',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'tiktok/4.mp4'
], check=True)
shutil.rmtree(temp_dir_4, ignore_errors=True)
print("4.mp4 rendered.")

print("SUCCESS: All 4 TikTok videos rendered using strictly solo_slides with top-right OBLIV logo!")
