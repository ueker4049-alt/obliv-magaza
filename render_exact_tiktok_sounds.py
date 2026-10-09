import os, subprocess, shutil, math
import numpy as np
from PIL import Image
from build_slide_sets import make_clean_slides, make_transparent_tshirt_slides

os.makedirs('tiktok', exist_ok=True)

def ease_in_out_cubic(x):
    if x < 0.5:
        return 4 * x * x * x
    else:
        return 1 - math.pow(-2 * x + 2, 3) / 2

def render_swipe_video(slides, audio_path, output_path, hold_sec=1.1, trans_sec=0.35, max_duration=13.5, fps=30):
    r"""
    Pure mobile swipe video between t-shirts.
    Matches the exact viral TikTok formats.
    """
    base_name = os.path.basename(output_path).replace('.mp4', '')
    temp_dir = f"temp_{base_name}"
    os.makedirs(temp_dir, exist_ok=True)
    
    hold_frames = round(hold_sec * fps)
    trans_frames = round(trans_sec * fps)
    
    w, h = 1080, 1920
    np_slides = [np.array(s) for s in slides]
    total_slides = len(np_slides)
    
    frame_idx = 0
    max_frames = round(max_duration * fps) if max_duration else None
    
    for s_idx in range(total_slides):
        if max_frames and frame_idx >= max_frames:
            break
            
        curr_slide = np_slides[s_idx]
        next_slide = np_slides[(s_idx + 1) % total_slides]
        
        # 1. Hold slide
        for _ in range(hold_frames):
            if max_frames and frame_idx >= max_frames:
                break
            img = Image.fromarray(curr_slide)
            img.save(os.path.join(temp_dir, f"frame_{frame_idx:05d}.jpg"), quality=93)
            frame_idx += 1
            
        # 2. Swipe transition (right to left)
        for t in range(trans_frames):
            if max_frames and frame_idx >= max_frames:
                break
            progress = (t + 1) / trans_frames
            eased = ease_in_out_cubic(progress)
            
            offset = round(eased * w)
            offset = max(0, min(w, offset))
            
            frame_canvas = np.empty((h, w, 3), dtype=np.uint8)
            if offset < w:
                frame_canvas[:, :w - offset] = curr_slide[:, offset:]
            if offset > 0:
                frame_canvas[:, w - offset:] = next_slide[:, :offset]
                
            img = Image.fromarray(frame_canvas)
            img.save(os.path.join(temp_dir, f"frame_{frame_idx:05d}.jpg"), quality=93)
            frame_idx += 1
            
    total_sec = frame_idx / fps
    print(f"Rendering: {output_path} | Frames: {frame_idx} ({total_sec:.2f}s)...")
    
    cmd = (
        f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t {total_sec:.2f} '
        f'-c:v libx264 -pix_fmt yuv420p -g {fps} -keyint_min {fps} '
        f'-c:a aac -b:a 192k -shortest "{output_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Finished: {output_path}")

def main():
    # 1. Viral Mostwize Society Exact Sound - POV Giyinmeyi Biliyorsun (Concrete slides)
    slides_pov = make_clean_slides(text="POV: GİYİNMEYİ BİLİYORSUN")
    render_swipe_video(
        slides=slides_pov,
        audio_path='cut_mostwize.mp3',
        output_path='tiktok/viral_tiktok_mostwize_pov.mp4',
        hold_sec=1.1,
        trans_sec=0.35,
        max_duration=13.5
    )

    # 2. Viral Dreampay/Bape Exact Sound - Pure Minimalist (No text, pure product aesthetic)
    slides_pure = make_clean_slides(text=None)
    render_swipe_video(
        slides=slides_pure,
        audio_path='cut_dreampay.mp3',
        output_path='tiktok/viral_tiktok_dreampay_minimal.mp4',
        hold_sec=1.1,
        trans_sec=0.35,
        max_duration=13.5
    )

    # 3. Viral Dreampay Exact Sound - Studio Look (t shirt/*.png on clean streetwear backdrop)
    slides_studio = make_transparent_tshirt_slides(text="POV: GİYİNMEYİ BİLİYORSUN")
    render_swipe_video(
        slides=slides_studio,
        audio_path='cut_dreampay.mp3',
        output_path='tiktok/viral_tiktok_dreampay_studio.mp4',
        hold_sec=1.1,
        trans_sec=0.35,
        max_duration=13.5
    )

    # 4. Viral Mostwize Sound - Studio Look
    slides_studio_rot = make_transparent_tshirt_slides(text="WEEKLY STREETWEAR ROTATION")
    render_swipe_video(
        slides=slides_studio_rot,
        audio_path='cut_mostwize.mp3',
        output_path='tiktok/viral_tiktok_mostwize_studio.mp4',
        hold_sec=1.1,
        trans_sec=0.35,
        max_duration=13.5
    )

if __name__ == '__main__':
    main()
