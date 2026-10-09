import os, glob, subprocess
from PIL import Image

# 1. Total frames needed: 335 frames at 30 fps (~11.17s)
cut_frame_indices = [
    1, 16, 21, 26, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

# Total segments = 46
print(f"Total cut segments: {len(cut_frame_indices)-1}")

# 2. Solo slides available: solo_00 to solo_08 (9 products)
solo_files = [f"solo_slides/solo_{i:02d}.jpg" for i in range(9)]

# Cycle through products cleanly across segments
# Each cut will switch to the next solo product
os.makedirs('rendered_video_frames', exist_ok=True)

seg_idx = 0
current_product_idx = 0

for frame_no in range(1, 336):
    # Check if we passed into a new segment
    if seg_idx < len(cut_frame_indices) - 1:
        if frame_no >= cut_frame_indices[seg_idx + 1]:
            seg_idx += 1
            current_product_idx = (current_product_idx + 1) % len(solo_files)
    
    # Selected slide
    slide_path = solo_files[current_product_idx]
    
    # Save frame (symlink or copy or Pillow open/save)
    # Using Image.open / save or os.system copy
    out_frame = f"rendered_video_frames/frame_{frame_no:04d}.jpg"
    # Fast copy
    if not os.path.exists(out_frame):
        with open(slide_path, 'rb') as src, open(out_frame, 'wb') as dst:
            dst.write(src.read())

print("All 335 video frames populated!")

# 3. Assemble video with FFmpeg + Mixed Audio
cmd = [
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', 'rendered_video_frames/frame_%04d.jpg',
    '-i', 'insta_music_with_clicks.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '256k',
    '-shortest',
    'obliv_instagram_click_viral.mp4'
]

print("Rendering video via FFmpeg...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg returncode:", res.returncode)
if res.returncode != 0:
    print(res.stderr[:500])
else:
    print("SUCCESS: obliv_instagram_click_viral.mp4 rendered!")
