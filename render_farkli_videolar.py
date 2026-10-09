import os, subprocess, shutil, glob

os.makedirs('tiktok', exist_ok=True)

def render_concept_1():
    """
    CONCEPT 1: Sitede Gördüğün vs Gerçekte Üstünde Duran (Travis Scott - FE!N)
    Total duration: ~13s
    Fast rhythmic switch: Flat shirt (0.8s) -> Mirror Fit pic (1.1s)
    """
    out_video = "tiktok/farkli_sitede_vs_uzerinde_fein.mp4"
    audio_path = "cut_travis_fein.mp3"
    temp_dir = "temp_render_c1"
    os.makedirs(temp_dir, exist_ok=True)

    # Frame rate = 30 fps
    # Pairs 0..6 (7 pairs = 14 segments)
    # pair 0: flat (25 frames = 0.83s), fit (35 frames = 1.16s)
    # 7 * 60 frames = 420 frames = 14 seconds
    frame_seq = []
    for i in range(7):
        flat = f"frames_c1/pair_{i}_flat.jpg"
        fit = f"frames_c1/pair_{i}_fit.jpg"
        # Flat: 24 frames (~0.8s)
        for _ in range(24):
            frame_seq.append(flat)
        # Fit: 34 frames (~1.13s)
        for _ in range(34):
            frame_seq.append(fit)

    # Limit to 390 frames (13.0s)
    frame_seq = frame_seq[:390]

    for idx, fpath in enumerate(frame_seq):
        dst = os.path.join(temp_dir, f"frame_{idx:05d}.jpg")
        shutil.copyfile(fpath, dst)

    cmd = (
        f'ffmpeg -y -framerate 30 -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p '
        f'-g 30 -keyint_min 30 -c:a aac -b:a 192k -shortest "{out_video}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Concept 1 finished:", out_video)

def render_concept_2():
    """
    CONCEPT 2: Streetwear Tier List / 10/10 Rating & Bed Lay Showcase (Kanye West - Bound 2)
    Total duration: ~13s
    Syncing 7 products: ~1.85s each (55 frames each)
    """
    out_video = "tiktok/farkli_tier_list_rating_bound2.mp4"
    audio_path = "cut_kanye_bound2.mp3"
    temp_dir = "temp_render_c2"
    os.makedirs(temp_dir, exist_ok=True)

    # 7 items, 55 frames each = 385 frames = 12.83s
    frame_seq = []
    for i in range(7):
        item_frame = f"frames_c2/rating_{i}.jpg"
        for _ in range(55):
            frame_seq.append(item_frame)

    for idx, fpath in enumerate(frame_seq):
        dst = os.path.join(temp_dir, f"frame_{idx:05d}.jpg")
        shutil.copyfile(fpath, dst)

    cmd = (
        f'ffmpeg -y -framerate 30 -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t 12.8 -c:v libx264 -pix_fmt yuv420p '
        f'-g 30 -keyint_min 30 -c:a aac -b:a 192k -shortest "{out_video}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Concept 2 finished:", out_video)

def render_concept_3():
    """
    CONCEPT 3: Cinematic Intro + Model Outfit Check (Frank Ocean - Novacane)
    Starts with clip_00.mp4 (1.5s animated drop teaser) + teaser frames (Travis boy/girl outfit check)
    Total duration: ~13s
    """
    out_video = "tiktok/farkli_outfit_cinematic_novacane.mp4"
    audio_path = "cut_frank_novacane.mp3"
    temp_dir = "temp_render_c3"
    os.makedirs(temp_dir, exist_ok=True)

    # First extract 45 frames from clip_00.mp4 (1.5s at 30fps)
    cmd_extract = f'ffmpeg -y -i "tiktok_clips/clip_00.mp4" -vf "fps=30" -frames:v 45 "{temp_dir}/intro_%03d.jpg"'
    subprocess.run(cmd_extract, shell=True, check=True)

    all_frames = []
    # 1. Intro frames
    for i in range(1, 46):
        all_frames.append(os.path.join(temp_dir, f"intro_{i:03d}.jpg"))

    # 2. Teaser model & drip frames (6 items, ~55 frames each = 330 frames)
    # Total frames = 45 + 330 = 375 frames = 12.5s
    for i in range(6):
        tframe = f"frames_c3/teaser_{i}.jpg"
        for _ in range(55):
            all_frames.append(tframe)

    temp_seq_dir = "temp_render_c3_seq"
    os.makedirs(temp_seq_dir, exist_ok=True)
    for idx, fpath in enumerate(all_frames):
        dst = os.path.join(temp_seq_dir, f"frame_{idx:05d}.jpg")
        shutil.copyfile(fpath, dst)

    cmd = (
        f'ffmpeg -y -framerate 30 -i "{temp_seq_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t 12.5 -c:v libx264 -pix_fmt yuv420p '
        f'-g 30 -keyint_min 30 -c:a aac -b:a 192k -shortest "{out_video}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(temp_seq_dir, ignore_errors=True)
    print("Concept 3 finished:", out_video)

def render_concept_4():
    """
    CONCEPT 4: Fast-paced Lil Tecca 500lbs Edition (Mockup vs Reality)
    """
    out_video = "tiktok/farkli_sitede_vs_uzerinde_tecca.mp4"
    audio_path = "cut_tecca_500lbs.mp3"
    temp_dir = "temp_render_c4"
    os.makedirs(temp_dir, exist_ok=True)

    # 7 pairs, snappy cut: 20 frames flat (0.66s), 30 frames fit (1.0s) -> 50 frames per pair = 350 frames = 11.66s
    frame_seq = []
    for i in range(7):
        flat = f"frames_c1/pair_{i}_flat.jpg"
        fit = f"frames_c1/pair_{i}_fit.jpg"
        for _ in range(20):
            frame_seq.append(flat)
        for _ in range(30):
            frame_seq.append(fit)

    for idx, fpath in enumerate(frame_seq):
        dst = os.path.join(temp_dir, f"frame_{idx:05d}.jpg")
        shutil.copyfile(fpath, dst)

    cmd = (
        f'ffmpeg -y -framerate 30 -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t 11.6 -c:v libx264 -pix_fmt yuv420p '
        f'-g 30 -keyint_min 30 -c:a aac -b:a 192k -shortest "{out_video}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Concept 4 finished:", out_video)

if __name__ == "__main__":
    render_concept_1()
    render_concept_2()
    render_concept_3()
    render_concept_4()
