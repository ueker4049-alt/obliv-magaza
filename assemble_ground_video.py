import os, subprocess

cut_frame_indices = [
    1, 16, 21, 26, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

solo_files = [f"solo_slides_v2/solo_{i:02d}.jpg" for i in range(9)]
os.makedirs('rendered_ground_frames', exist_ok=True)

seg_idx = 0
current_product_idx = 0

for frame_no in range(1, 336):
    if seg_idx < len(cut_frame_indices) - 1:
        if frame_no >= cut_frame_indices[seg_idx + 1]:
            seg_idx += 1
            current_product_idx = (current_product_idx + 1) % len(solo_files)
    
    slide_path = solo_files[current_product_idx]
    out_frame = f"rendered_ground_frames/frame_{frame_no:04d}.jpg"
    
    with open(slide_path, 'rb') as src, open(out_frame, 'wb') as dst:
        dst.write(src.read())

print("All 335 frames populated with ground-laid t-shirts and OBLIV logo.")

# Assemble video with only clicks (zero background song)
cmd = [
    'ffmpeg', '-y',
    '-framerate', '30',
    '-i', 'rendered_ground_frames/frame_%04d.jpg',
    '-i', 'only_clicks.wav',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'obliv_ground_clicks_only.mp4'
]

print("Rendering video...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg returncode:", res.returncode)
if res.returncode != 0:
    print(res.stderr[:500])
else:
    print("SUCCESS: obliv_ground_clicks_only.mp4 rendered!")
