import os
import shutil
import subprocess
import numpy as np
from PIL import Image

def load_assets():
    logo_raw = Image.open("user_obliv_logo.png").convert("RGBA")
    slides = [Image.open(f"solo_slides/solo_{i:02d}.jpg").convert("RGB") for i in range(9)]
    concrete_bg = Image.open("concrete_bg.jpg").convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    return logo_raw, slides, concrete_bg

def overlay_logo_header(canvas, logo_img, lw=420, ly=130):
    lh = int(logo_img.height * (lw / logo_img.width))
    logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
    lx = (canvas.width - lw) // 2
    canvas.alpha_composite(logo_res, (lx, ly))

# =========================================================================
# 1. CARNIVAL - 3D MACRO CHEST PRINT PUNCH (Playboi Carti & Kanye West)
# =========================================================================
def render_carnival_macro(logo_raw, slides, concrete_bg):
    output_path = "tiktok/trend1_carnival_macro_punch.mp4"
    audio_path = "cut_kanye_carnival.mp3"
    print(f"\n==========================================")
    print(f"Rendering: {output_path} (Carnival Macro Texture Punch)")
    print(f"==========================================")
    
    fps = 30
    total_frames = 420 # 14.0s
    drop_frame = 105   # 3.50s: Choir chants build-up into 808 drop
    
    temp_dir = "temp_trend1_carnival"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Pre-render slides with logo header
    branded_slides = []
    for s in slides:
        b = s.copy().convert("RGBA")
        overlay_logo_header(b, logo_raw)
        branded_slides.append(b.convert("RGB"))
        
    # After drop at 3.5s (f=105):
    # Beat pattern hits every 13 frames (~0.43s)
    # Beat cycle: Frame 0..7 = Full view, Frame 8..12 = 1.35x Macro zoom on chest print!
    beat_step = 13
    
    for f_i in range(total_frames):
        if f_i < drop_frame:
            # Intro choir chant: logo pulses in center to choir beats
            bg = concrete_bg.copy()
            # 4 choir chant pulses at ~0.8s intervals
            pulse = 1.0 + 0.12 * np.abs(np.sin((f_i / 30.0) * np.pi * 2.5))
            c_lw = int(480 * pulse)
            c_lh = int(logo_raw.height * (c_lw / logo_raw.width))
            logo_c = logo_raw.resize((c_lw, c_lh), Image.Resampling.LANCZOS)
            bg.alpha_composite(logo_c, ((1080 - c_lw) // 2, (1920 - c_lh) // 2))
            frame_img = bg.convert("RGB")
        else:
            frames_since = f_i - drop_frame
            shirt_idx = (frames_since // beat_step) % len(branded_slides)
            frame_in_step = frames_since % beat_step
            
            base = branded_slides[shirt_idx]
            
            # 2-step rhythm: Full shot -> Instant Macro Snap
            if frame_in_step < 7:
                # Full shot with slight impact kick settle
                punch = 1.05 if frame_in_step == 0 else (1.02 if frame_in_step == 1 else 1.00)
                if punch != 1.0:
                    pw, ph = int(1080 * punch), int(1920 * punch)
                    res = base.resize((pw, ph), Image.Resampling.LANCZOS)
                    frame_img = res.crop(((pw - 1080)//2, (ph - 1920)//2, (pw - 1080)//2 + 1080, (ph - 1920)//2 + 1920))
                else:
                    frame_img = base
            else:
                # Macro zoom directly into chest graphic & cotton texture!
                zoom = 1.35
                pw, ph = int(1080 * zoom), int(1920 * zoom)
                res = base.resize((pw, ph), Image.Resampling.LANCZOS)
                # Crop focused slightly above center (chest print area)
                cx = (pw - 1080) // 2
                cy = int((ph - 1920) * 0.45)
                frame_img = res.crop((cx, cy, cx + 1080, cy + 1920))
                
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 14.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("SUCCESS:", output_path)

# =========================================================================
# 2. 20 MIN - KINETIC DIRECTIONAL HORIZONTAL SWIPE (Lil Uzi Vert)
# =========================================================================
def render_20min_kinetic_swipe(logo_raw, slides, concrete_bg):
    output_path = "tiktok/trend2_20min_kinetic_swipe.mp4"
    audio_path = "cut_uzi_20min.mp3"
    print(f"\n==========================================")
    print(f"Rendering: {output_path} (20 Min Kinetic Directional Push-Swipe)")
    print(f"==========================================")
    
    fps = 30
    total_frames = 405 # 13.5s
    
    temp_dir = "temp_trend2_swipe"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Base slides (without logo, logo drawn continuously on top during transitions)
    base_slides = [s.convert("RGB") for s in slides]
    
    # Faster rhythmic cut matching 20 Min synth tempo:
    # Transition happens every 24 frames (~0.80s)
    # The swipe transition itself takes 4 frames (ultra snappy whip)
    step = 24
    swipe_frames = 4
    
    for f_i in range(total_frames):
        slide_idx = (f_i // step) % len(base_slides)
        next_idx = (slide_idx + 1) % len(base_slides)
        frame_in_step = f_i % step
        
        cur_img = base_slides[slide_idx]
        next_img = base_slides[next_idx]
        
        if frame_in_step < step - swipe_frames:
            # Steady display
            frame_composite = cur_img.copy().convert("RGBA")
        else:
            # Kinetic whip swipe from right to left with ease-out cubic
            sw_prog = (frame_in_step - (step - swipe_frames) + 1) / float(swipe_frames)
            ease = 1.0 - (1.0 - sw_prog) ** 3
            offset_x = int(1080 * ease)
            
            canvas = Image.new("RGBA", (1080, 1920))
            canvas.paste(cur_img, (-offset_x, 0))
            canvas.paste(next_img, (1080 - offset_x, 0))
            frame_composite = canvas
            
        # Overlay stationary crisp logo on header
        overlay_logo_header(frame_composite, logo_raw)
        frame_composite.convert("RGB").save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.5 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("SUCCESS:", output_path)

# =========================================================================
# 3. FE!N - STROBOSCOPIC EXPOSURE FLASH (Travis Scott)
# =========================================================================
def render_fein_strobe(logo_raw, slides, concrete_bg):
    output_path = "tiktok/trend3_fein_strobe_flash.mp4"
    audio_path = "cut_travis_fein.mp3"
    print(f"\n==========================================")
    print(f"Rendering: {output_path} (FE!N Stroboscopic Flash & 808 Impact)")
    print(f"==========================================")
    
    fps = 30
    total_frames = 390 # 13.0s
    drop_frame = 84    # 2.8s
    
    temp_dir = "temp_trend3_strobe"
    os.makedirs(temp_dir, exist_ok=True)
    
    branded_slides = []
    for s in slides:
        b = s.copy().convert("RGBA")
        overlay_logo_header(b, logo_raw)
        branded_slides.append(b.convert("RGB"))
        
    beat_step = 13 # ~0.43s per beat
    
    for f_i in range(total_frames):
        if f_i < drop_frame:
            # Synth tension build: concrete background with logo pulsing and vibrating
            prog = f_i / float(drop_frame)
            bg = concrete_bg.copy()
            overlay = Image.new("RGBA", (1080, 1920), (12, 12, 16, 160))
            bg.alpha_composite(overlay)
            
            pulse = 1.0 + 0.15 * (f_i % 12) / 12.0
            lw = int(480 * pulse)
            lh = int(logo_raw.height * (lw / logo_raw.width))
            logo_res = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
            bg.alpha_composite(logo_res, ((1080 - lw)//2, (1920 - lh)//2))
            frame_img = bg.convert("RGB")
        else:
            frames_since = f_i - drop_frame
            shirt_idx = (frames_since // beat_step) % len(branded_slides)
            frame_in_step = frames_since % beat_step
            
            base = branded_slides[shirt_idx].copy().convert("RGBA")
            
            # Flash + punch on beat 0
            if frame_in_step == 0:
                # White exposure pop (alpha composite 20% white)
                white_flash = Image.new("RGBA", (1080, 1920), (255, 255, 255, 60))
                base.alpha_composite(white_flash)
                # 1.05x punch
                pw, ph = int(1080 * 1.05), int(1920 * 1.05)
                res = base.resize((pw, ph), Image.Resampling.LANCZOS)
                frame_img = res.crop(((pw-1080)//2, (ph-1920)//2, (pw-1080)//2+1080, (ph-1920)//2+1920)).convert("RGB")
            elif frame_in_step == 1:
                pw, ph = int(1080 * 1.02), int(1920 * 1.02)
                res = base.resize((pw, ph), Image.Resampling.LANCZOS)
                frame_img = res.crop(((pw-1080)//2, (ph-1920)//2, (pw-1080)//2+1080, (ph-1920)//2+1920)).convert("RGB")
            else:
                frame_img = base.convert("RGB")
                
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("SUCCESS:", output_path)

# =========================================================================
# 4. 500 LBS - VERTICAL DROP CASCADE (Lil Tecca)
# =========================================================================
def render_500lbs_vertical_cascade(logo_raw, slides, concrete_bg):
    output_path = "tiktok/trend4_500lbs_vertical_cascade.mp4"
    audio_path = "cut_tecca_500lbs.mp3"
    print(f"\n==========================================")
    print(f"Rendering: {output_path} (500 LBS Vertical Drop Cascade)")
    print(f"==========================================")
    
    fps = 30
    total_frames = 390 # 13.0s
    
    temp_dir = "temp_trend4_cascade"
    os.makedirs(temp_dir, exist_ok=True)
    
    base_slides = [s.convert("RGB") for s in slides]
    
    # Bouncy vertical cascade every 22 frames (~0.73s)
    step = 22
    drop_anim_frames = 4
    
    for f_i in range(total_frames):
        slide_idx = (f_i // step) % len(base_slides)
        next_idx = (slide_idx + 1) % len(base_slides)
        frame_in_step = f_i % step
        
        cur_img = base_slides[slide_idx]
        next_img = base_slides[next_idx]
        
        if frame_in_step < step - drop_anim_frames:
            frame_composite = cur_img.copy().convert("RGBA")
        else:
            # Drop down from top
            dr_prog = (frame_in_step - (step - drop_anim_frames) + 1) / float(drop_anim_frames)
            ease = 1.0 - (1.0 - dr_prog) ** 3
            offset_y = int(1920 * ease)
            
            canvas = Image.new("RGBA", (1080, 1920))
            canvas.paste(cur_img, (0, offset_y))
            canvas.paste(next_img, (0, -1920 + offset_y))
            frame_composite = canvas
            
        overlay_logo_header(frame_composite, logo_raw)
        frame_composite.convert("RGB").save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("SUCCESS:", output_path)

# =========================================================================
# 5. BOUND 2 - ANALOG SLOW DRIFT & DRUM SNAP (Kanye West)
# =========================================================================
def render_bound2_analog_slide(logo_raw, slides, concrete_bg):
    output_path = "tiktok/trend5_bound2_analog_slide.mp4"
    audio_path = "cut_kanye_bound2.mp3"
    print(f"\n==========================================")
    print(f"Rendering: {output_path} (Bound 2 Analog Drift & Drum Snap)")
    print(f"==========================================")
    
    fps = 30
    total_frames = 390 # 13.0s
    
    temp_dir = "temp_trend5_bound2"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Snap cuts on Kanye's heavy kick & snare claps (~1.44s per shirt)
    step = 43
    
    for f_i in range(total_frames):
        slide_idx = (f_i // step) % len(slides)
        frame_in_step = f_i % step
        
        base = slides[slide_idx].copy().convert("RGBA")
        overlay_logo_header(base, logo_raw)
        
        # Subtle slow continuous zoom drift (1.00x -> 1.05x)
        drift = 1.0 + 0.05 * (frame_in_step / float(step))
        pw, ph = int(1080 * drift), int(1920 * drift)
        res = base.resize((pw, ph), Image.Resampling.LANCZOS)
        frame_img = res.crop(((pw-1080)//2, (ph-1920)//2, (pw-1080)//2+1080, (ph-1920)//2+1920)).convert("RGB")
        
        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)
        
    cmd = f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" -i "{audio_path}" -t 13.0 -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 -c:a aac -b:a 192k -shortest "{output_path}"'
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("SUCCESS:", output_path)

if __name__ == '__main__':
    os.makedirs('tiktok', exist_ok=True)
    logo_raw, slides, concrete_bg = load_assets()
    
    render_carnival_macro(logo_raw, slides, concrete_bg)
    render_20min_kinetic_swipe(logo_raw, slides, concrete_bg)
    render_fein_strobe(logo_raw, slides, concrete_bg)
    render_500lbs_vertical_cascade(logo_raw, slides, concrete_bg)
    render_bound2_analog_slide(logo_raw, slides, concrete_bg)
    
    print("\nALL 5 STREETWEAR TREND VIDEOS SUCCESSFULLY GENERATED!")
