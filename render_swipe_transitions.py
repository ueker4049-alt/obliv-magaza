import os, subprocess, shutil, math
import numpy as np
from PIL import Image
from prepare_clean_slides import prepare_base_slides

def ease_in_out_cubic(x):
    if x < 0.5:
        return 4 * x * x * x
    else:
        return 1 - math.pow(-2 * x + 2, 3) / 2

def ease_out_cubic(x):
    return 1 - math.pow(1 - x, 3)

def generate_swipe_video(slides, audio_path, output_path, hold_sec=1.1, trans_sec=0.35, fps=30):
    r"""
    Generates a phone swipe transition video.
    Each slide is held for hold_sec, then smoothly swiped to the next slide over trans_sec.
    Zero zoom, zero intro/outro, pure natural smartphone swipe motion.
    """
    temp_dir = f"temp_swipe_{os.path.basename(output_path).replace('.mp4','')}"
    os.makedirs(temp_dir, exist_ok=True)
    
    hold_frames = round(hold_sec * fps)
    trans_frames = round(trans_sec * fps)
    
    w, h = 1080, 1920
    
    # Pre-convert slides to numpy arrays
    np_slides = [np.array(s) for s in slides]
    
    total_slides = len(np_slides)
    frame_idx = 0
    
    print(f"Rendering swipe video: {output_path} | {total_slides} slides...")
    
    for s_idx in range(total_slides):
        curr_slide = np_slides[s_idx]
        next_slide = np_slides[(s_idx + 1) % total_slides]
        
        # 1. Hold frames
        for _ in range(hold_frames):
            img = Image.fromarray(curr_slide)
            img.save(os.path.join(temp_dir, f"frame_{frame_idx:05d}.jpg"), quality=92)
            frame_idx += 1
            
        # 2. Transition frames (swipe from right to left, like finger swiping left on TikTok)
        for t in range(trans_frames):
            # progress 0.0 to 1.0 with smooth cubic easing
            progress = (t + 1) / trans_frames
            eased = ease_in_out_cubic(progress)
            
            # Offset in pixels
            offset = round(eased * w)
            offset = max(0, min(w, offset))
            
            # Canvas composed of right part of current slide + left part of next slide
            frame_canvas = np.empty((h, w, 3), dtype=np.uint8)
            
            # Current slide moves to the left: its right (w - offset) columns appear at [0 : w - offset]
            if offset < w:
                frame_canvas[:, :w - offset] = curr_slide[:, offset:]
            
            # Next slide comes in from the right: its first 'offset' columns appear at [w - offset : w]
            if offset > 0:
                frame_canvas[:, w - offset:] = next_slide[:, :offset]
                
            img = Image.fromarray(frame_canvas)
            img.save(os.path.join(temp_dir, f"frame_{frame_idx:05d}.jpg"), quality=92)
            frame_idx += 1
            
    total_duration = frame_idx / fps
    print(f"Total frames: {frame_idx} ({total_duration:.2f}s)")
    
    cmd = (
        f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t {total_duration:.2f} '
        f'-c:v libx264 -pix_fmt yuv420p -g {fps} -keyint_min {fps} '
        f'-c:a aac -b:a 192k -shortest "{output_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    slides = prepare_base_slides('pov')
    generate_swipe_video(slides, 'cut_travis_fein.mp3', 'tiktok/test_swipe_fein.mp4', hold_sec=1.0, trans_sec=0.35)
