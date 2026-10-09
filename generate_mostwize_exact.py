import os, subprocess, shutil
from PIL import Image

def generate_mostwize_style_video(
    front_img_path,
    back_img_path,
    audio_path,
    output_path,
    total_duration=14.0
):
    r"""
    Recreates the exact @mostwize.society TikTok video style:
    1. Angle 1 (0.0s - 3.2s): Back neck / label view on bed
    2. Angle 2 (3.2s - 7.0s): Full front boxy flat-lay view on bed
    3. Angle 3 (7.0s - 10.5s): Close-up / medium angled crop of front graphic & heavy cotton texture
    4. Angle 4 (10.5s - 14.0s): Second dynamic front angle
    """
    temp_dir = f"temp_mw_{os.path.basename(output_path).replace('.mp4','')}"
    os.makedirs(temp_dir, exist_ok=True)
    fps = 30
    w, h = 1080, 1920

    # Load front and back images
    front_img = Image.open(front_img_path).convert("RGB")
    back_img = Image.open(back_img_path).convert("RGB") if back_img_path else front_img

    # Build Angle 1: Back view or Collar label close-up
    # Take back image and fit/crop to 1080x1920
    im_b_ratio = back_img.width / back_img.height
    canvas_ratio = w / h
    # Scale to fill canvas with crop
    scale1 = max(w / back_img.width, h / back_img.height)
    bw1, bh1 = int(back_img.width * scale1), int(back_img.height * scale1)
    b_resized1 = back_img.resize((bw1, bh1), Image.Resampling.LANCZOS)
    angle1 = b_resized1.crop(((bw1 - w) // 2, (bh1 - h) // 2, (bw1 - w) // 2 + w, (bh1 - h) // 2 + h))

    # Build Angle 2: Full front flat lay
    scale2 = max(w / front_img.width, h / front_img.height)
    fw2, fh2 = int(front_img.width * scale2), int(front_img.height * scale2)
    f_resized2 = front_img.resize((fw2, fh2), Image.Resampling.LANCZOS)
    angle2 = f_resized2.crop(((fw2 - w) // 2, (fh2 - h) // 2, (fw2 - w) // 2 + w, (fh2 - h) // 2 + h))

    # Build Angle 3: Close-up of graphic / chest print & texture
    scale3 = scale2 * 1.35
    fw3, fh3 = int(front_img.width * scale3), int(front_img.height * scale3)
    f_resized3 = front_img.resize((fw3, fh3), Image.Resampling.LANCZOS)
    # Center slightly on the chest graphic
    crop_x3 = (fw3 - w) // 2
    crop_y3 = int((fh3 - h) * 0.40)
    crop_y3 = max(0, min(fh3 - h, crop_y3))
    angle3 = f_resized3.crop((crop_x3, crop_y3, crop_x3 + w, crop_y3 + h))

    # Build Angle 4: Medium dynamic front angle
    scale4 = scale2 * 1.15
    fw4, fh4 = int(front_img.width * scale4), int(front_img.height * scale4)
    f_resized4 = front_img.resize((fw4, fh4), Image.Resampling.LANCZOS)
    crop_x4 = (fw4 - w) // 2
    crop_y4 = int((fh4 - h) * 0.48)
    crop_y4 = max(0, min(fh4 - h, crop_y4))
    angle4 = f_resized4.crop((crop_x4, crop_y4, crop_x4 + w, crop_y4 + h))

    # Timing:
    # 0 - 3.2s: Angle 1 (96 frames)
    # 3.2s - 7.0s: Angle 2 (114 frames)
    # 7.0s - 10.5s: Angle 3 (105 frames)
    # 10.5s - 14.0s: Angle 4 (105 frames)
    # Total = 420 frames = 14.0s
    frame_seq = []
    for _ in range(96):
        frame_seq.append(angle1)
    for _ in range(114):
        frame_seq.append(angle2)
    for _ in range(105):
        frame_seq.append(angle3)
    for _ in range(105):
        frame_seq.append(angle4)

    for idx, frame in enumerate(frame_seq):
        frame.save(os.path.join(temp_dir, f"frame_{idx:05d}.jpg"), quality=93)

    cmd = (
        f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t {total_duration:.2f} '
        f'-c:v libx264 -pix_fmt yuv420p -g {fps} -keyint_min {fps} '
        f'-c:a aac -b:a 192k -shortest "{output_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Mostwize video rendered:", output_path)

if __name__ == '__main__':
    # 1. Travis Scott Bed Lay + Travis Scott FE!N
    generate_mostwize_style_video(
        front_img_path='static/uploads/travis_review_bed.jpg',
        back_img_path='static/uploads/clean_white_bed.jpg',
        audio_path='cut_travis_fein.mp3',
        output_path='tiktok/birebir_mostwize_travis_fein.mp4',
        total_duration=13.0
    )
    # 2. Lil Tecca Bed Lay + Kanye West Bound 2
    if os.path.exists('static/uploads/tecca_review_bed.jpg') and os.path.exists('cut_kanye_bound2.mp3'):
        generate_mostwize_style_video(
            front_img_path='static/uploads/tecca_review_bed.jpg',
            back_img_path='static/uploads/clean_white_bed.jpg',
            audio_path='cut_kanye_bound2.mp3',
            output_path='tiktok/birebir_mostwize_tecca_bound2.mp4',
            total_duration=13.0
        )
    # 3. Trippie Redd Bed Lay + Frank Ocean Novacane
    if os.path.exists('static/uploads/trippie_review_bed.jpg') and os.path.exists('cut_frank_novacane.mp3'):
        generate_mostwize_style_video(
            front_img_path='static/uploads/trippie_review_bed.jpg',
            back_img_path='static/uploads/clean_white_bed.jpg',
            audio_path='cut_frank_novacane.mp3',
            output_path='tiktok/birebir_mostwize_frank_novacane.mp4',
            total_duration=13.0
        )
