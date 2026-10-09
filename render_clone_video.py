import os, subprocess

# 10 slides: slide_00 to slide_09
# Slide 00 (hook): 2.5 seconds
# Slides 01 to 09 (t-shirts): 1.4 seconds each
# Total = 2.5 + 9 * 1.4 = 15.1 seconds (matches the 15.9s TikTok audio perfectly)

durations = [2.5] + [1.4] * 9

# Create concat demuxer file
with open('slides_concat.txt', 'w', encoding='utf-8') as f:
    for i in range(10):
        img_path = f"tiktok_clone_slides/slide_{i:02d}.jpg".replace('\\', '/')
        f.write(f"file '{img_path}'\n")
        f.write(f"duration {durations[i]}\n")
    # Repeat last image as per concat demuxer spec
    f.write(f"file 'tiktok_clone_slides/slide_09.jpg'\n")

print("Created slides_concat.txt")

# Run FFmpeg to encode video with the original audio
cmd = [
    'ffmpeg', '-y',
    '-f', 'concat', '-safe', '0', '-i', 'slides_concat.txt',
    '-i', 'tiktok_ref.mp3',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
    '-c:a', 'aac', '-b:a', '192k',
    '-shortest',
    'obliv_tiktok_photo_video.mp4'
]

print("Running FFmpeg...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFmpeg returncode:", res.returncode)
if res.returncode != 0:
    print(res.stderr[:500])
else:
    print("Video rendered successfully: obliv_tiktok_photo_video.mp4")
