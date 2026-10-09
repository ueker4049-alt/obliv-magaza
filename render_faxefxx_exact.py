import os
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageFilter

# Precise audio transient hit frames (60 fps):
# Each hit corresponds to a snare/clap/beat 'şak' in the audio track
BEAT_CUTS = [
    214, # Hit 1 (Beat drop / 3.562s)
    235, # Hit 2 (3.911s)
    276, # Hit 3 (4.595s)
    296, # Hit 4 (4.929s)
    337, # Hit 5 (5.617s)
    378, # Hit 6 (6.306s)
    398, # Hit 7 (6.640s)
    439, # Hit 8 (7.323s)
    459, # Hit 9 (7.658s)
    501, # Hit 10 (8.346s)
    522, # Hit 11 (8.700s)
    542, # Hit 12 (9.034s)
    563, # Hit 13 (9.384s)
    603, # Hit 14 (10.050s)
    624, # Hit 15 (10.400s)
]

def render_white_frame(shirt_img, logo_img, width, height, shirt_base_w, shirt_base_y, logo_w, logo_y, punch_scale=1.0):
    canvas = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    
    # Top logo
    if logo_img is not None:
        lw = logo_w
        lh = int(logo_img.height * (lw / logo_img.width))
        logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = (width - lw) // 2
        canvas.alpha_composite(logo_res, (lx, logo_y))
        
    # Shirt with punch scale on beat hits
    sw = int(shirt_base_w * punch_scale)
    sh = int(shirt_img.height * (sw / shirt_img.width))
    shirt_res = shirt_img.resize((sw, sh), Image.Resampling.LANCZOS)
    
    s_alpha = shirt_res.split()[-1]
    pad = 80
    shadow = Image.new('RGBA', (sw + pad * 2, sh + pad * 2), (0, 0, 0, 0))
    s_tint = Image.new('RGBA', (sw, sh), (30, 30, 30, 80))
    s_tint.putalpha(s_alpha.point(lambda a: int(a * 0.28)))
    shadow.paste(s_tint, (pad, pad + 15), s_tint)
    shadow_blur = shadow.filter(ImageFilter.GaussianBlur(28))
    
    sx = (width - sw) // 2
    # Adjust sy so it scales from the center of the shirt
    sy = shirt_base_y - (sh - int(shirt_img.height * (shirt_base_w / shirt_img.width))) // 2
    canvas.alpha_composite(shadow_blur, (sx - pad, sy - pad))
    canvas.alpha_composite(shirt_res, (sx, sy))
    
    return canvas.convert('RGB')

def render_concrete_frame(slide_img, logo_img, width, height, logo_w, logo_y, punch_scale=1.0):
    if punch_scale != 1.0:
        # Scale slightly from center for the beat punch
        pw = int(width * punch_scale)
        ph = int(height * punch_scale)
        s_res = slide_img.resize((pw, ph), Image.Resampling.LANCZOS)
        x_crop = (pw - width) // 2
        y_crop = (ph - height) // 2
        canvas = s_res.crop((x_crop, y_crop, x_crop + width, y_crop + height)).convert('RGBA')
    else:
        canvas = slide_img.copy().convert('RGBA')
        
    if logo_img is not None:
        lw = logo_w
        lh = int(logo_img.height * (lw / logo_img.width))
        logo_res = logo_img.resize((lw, lh), Image.Resampling.LANCZOS)
        lx = (width - lw) // 2
        canvas.alpha_composite(logo_res, (lx, logo_y))
        
    return canvas.convert('RGB')

def render_beat_synced_video(
    mode="white_vertical",
    audio_path="ref_vt_audio.mp3",
    output_path="tiktok/birebir_faxefxx_obliv_white_9x16.mp4"
):
    print(f"\n==========================================")
    print(f"Rendering BEAT-PERFECT: {output_path} (Mode: {mode})")
    print(f"==========================================")
    
    fps = 60
    total_frames = 650 # 10.833s
    
    if mode == "white_square":
        width, height = 1080, 1080
        center_cy = 540
        header_cy = 140
        base_logo_w = 380
        header_logo_w = 320
        shirt_base_w = 720
        shirt_base_y = 360
    else: # 1080x1920 vertical
        width, height = 1080, 1920
        center_cy = 960
        header_cy = 280
        base_logo_w = 460
        header_logo_w = 380
        shirt_base_w = 860
        shirt_base_y = 760
        
    temp_dir = f"temp_fx_{os.path.basename(output_path).replace('.mp4','')}"
    os.makedirs(temp_dir, exist_ok=True)
    
    logo_raw = Image.open("user_obliv_logo.png").convert("RGBA")
    header_logo_y = header_cy - int(logo_raw.height * (header_logo_w / logo_raw.width)) // 2
    
    # 11 source t-shirts (including 2 new Black color drops)
    product_keys = [
        'static/uploads/obliv.png',       # 0: Zé Pequeno
        'static/uploads/t-1.png',         # 1: 444 Angel
        'static/uploads/lil_tecca.png',   # 2: Lil Tecca
        'static/uploads/travis_scott.png',# 3: Travis Scott
        'static/uploads/trippie_red.png', # 4: Trippie Redd
        'static/uploads/lips.png',        # 5: Rolling Lips
        'static/uploads/lil_uzi_vert.png',# 6: Lil Uzi Vert
        'static/uploads/i_am_music.png',  # 7: I Am Music
        'static/uploads/frank_ocean.png', # 8: Frank Ocean
        'static/uploads/vamp_fangs.png',  # 9: Deviant Fangs (New Black Tee)
        'static/uploads/star_girl.png',   # 10: Star Girl (New Black Tee)
    ]
    loaded_shirts = [Image.open(p).convert('RGBA') for p in product_keys]
    
    solo_slide_files = [f"solo_slides/solo_{i:02d}.jpg" for i in range(11)]
    loaded_slides = [Image.open(p).convert('RGB') for p in solo_slide_files]

    # Map each of the 15 beat slots to showcase all 11 products:
    # Featuring the 2 new Black drops prominently on the beat drop and climax!
    slot_product_mapping = [
        9,  # Slot 1 (f=214): DEVIANT FANGS (New Black Tee - Beat Drop!)
        10, # Slot 2 (f=235): STAR GIRL (New Black Tee - 2nd Beat Hit!)
        1,  # Slot 3 (f=276): 444 Angel
        0,  # Slot 4 (f=296): Zé Pequeno
        2,  # Slot 5 (f=337): Lil Tecca
        3,  # Slot 6 (f=378): Travis Scott
        4,  # Slot 7 (f=398): Trippie Redd
        5,  # Slot 8 (f=439): Rolling Lips
        6,  # Slot 9 (f=459): Lil Uzi Vert
        7,  # Slot 10 (f=501): I Am Music
        8,  # Slot 11 (f=522): Frank Ocean
        9,  # Slot 12 (f=542): DEVIANT FANGS (Rapid Climax Hit)
        10, # Slot 13 (f=563): STAR GIRL (Rapid Climax Hit)
        1,  # Slot 14 (f=603): 444 Angel (Rapid Climax Hit)
        9,  # Slot 15 (f=624): DEVIANT FANGS (Final Beat Climax)
    ]
    
    # Pre-calculate intervals [start_f, end_f, product_idx]
    intervals = []
    for idx, start_f in enumerate(BEAT_CUTS):
        end_f = BEAT_CUTS[idx+1] - 1 if idx + 1 < len(BEAT_CUTS) else total_frames - 1
        intervals.append((start_f, end_f, slot_product_mapping[idx]))

    print(f"Rendering {total_frames} frames with {len(intervals)} beat-synced intervals...")

    for f_i in range(total_frames):
        if f_i < BEAT_CUTS[0]: # f_i < 214 (INTRO)
            if mode == "concrete_vertical":
                bg = Image.open('concrete_bg.jpg').convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
            else:
                bg = Image.new('RGBA', (width, height), (255, 255, 255, 255))
                
            # Intro beat hits:
            # Hit 1: frame 50 (0.838s)
            # Hit 2: frame 91 (1.517s)
            # Hit 3: frame 132 (2.200s)
            # Slide: frame 154..185
            # Parked: frame 186..213
            if f_i < 50:
                lw = base_logo_w
                cy = center_cy
            elif f_i < 91:
                # Beat 1: Zoom to 1.25x
                lw = int(base_logo_w * 1.25)
                cy = center_cy
            elif f_i < 132:
                # Beat 2: Zoom to 1.45x
                lw = int(base_logo_w * 1.45)
                cy = center_cy
            elif f_i < 154:
                # Beat 3: Peak zoom 1.70x, then settle
                lw = int(base_logo_w * 1.70)
                cy = center_cy
            elif f_i < 185:
                # Smooth slide up to header
                prog = (f_i - 154) / (185 - 154)
                prog_e = 0.5 - 0.5 * np.cos(prog * np.pi)
                lw = int(base_logo_w * (1.0 - prog_e) + header_logo_w * prog_e)
                cy = int(center_cy * (1.0 - prog_e) + header_cy * prog_e)
            else:
                # Parked at top
                lw = header_logo_w
                cy = header_cy
                
            lh = int(logo_raw.height * (lw / logo_raw.width))
            logo_scaled = logo_raw.resize((lw, lh), Image.Resampling.LANCZOS)
            lx = (width - lw) // 2
            ly = cy - lh // 2
            bg.alpha_composite(logo_scaled, (lx, ly))
            frame_img = bg.convert('RGB')
        else:
            # BEAT-SYNCED T-SHIRT SHOWCASE (214..649)
            # Find current interval and relative frame to cut
            cur_prod = 0
            frames_since_cut = 0
            for start_f, end_f, p_idx in intervals:
                if start_f <= f_i <= end_f:
                    cur_prod = p_idx
                    frames_since_cut = f_i - start_f
                    break
                    
            # Punch-in impact curve on each beat hit:
            # 0 frames after cut: 1.05x punch
            # 1 frame after cut: 1.03x punch
            # 2 frames after cut: 1.01x punch
            # >=3 frames: 1.00x normal
            if frames_since_cut == 0:
                punch = 1.05
            elif frames_since_cut == 1:
                punch = 1.03
            elif frames_since_cut == 2:
                punch = 1.01
            else:
                punch = 1.00

            if mode == "concrete_vertical":
                frame_img = render_concrete_frame(
                    slide_img=loaded_slides[cur_prod],
                    logo_img=logo_raw,
                    width=width,
                    height=height,
                    logo_w=header_logo_w,
                    logo_y=140,
                    punch_scale=punch
                )
            else:
                frame_img = render_white_frame(
                    shirt_img=loaded_shirts[cur_prod],
                    logo_img=logo_raw,
                    width=width,
                    height=height,
                    shirt_base_w=shirt_base_w,
                    shirt_base_y=shirt_base_y,
                    logo_w=header_logo_w,
                    logo_y=header_logo_y,
                    punch_scale=punch
                )

            # Çok hafif, tatlı white flash geçiş efekti
            if frames_since_cut == 0:
                flash_alpha = 0.28
            elif frames_since_cut == 1:
                flash_alpha = 0.15
            elif frames_since_cut == 2:
                flash_alpha = 0.05
            else:
                flash_alpha = 0.0

            if flash_alpha > 0:
                f_rgba = frame_img.convert("RGBA")
                flash_layer = Image.new("RGBA", (width, height), (255, 255, 255, int(255 * flash_alpha)))
                f_rgba.alpha_composite(flash_layer)
                frame_img = f_rgba.convert("RGB")

        frame_img.save(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), quality=93)

    duration = total_frames / float(fps)
    print(f"Frames saved. Encoding with ffmpeg ({audio_path})...")
    cmd = (
        f'ffmpeg -y -framerate {fps} -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t {duration:.2f} '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 '
        f'-c:a aac -b:a 192k -shortest "{output_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("FINISHED! Video rendered:", output_path)

if __name__ == '__main__':
    # 1. Solo Slides Concrete 9:16 Vertical (Requested by user)
    render_beat_synced_video(
        mode="concrete_vertical",
        audio_path="ref_vt_audio.mp3",
        output_path="tiktok/birebir_faxefxx_solo_slides_concrete.mp4"
    )
    # 2. Studio White 9:16 Vertical (Ideal for TikTok / Reels)
    render_beat_synced_video(
        mode="white_vertical",
        audio_path="ref_vt_audio.mp3",
        output_path="tiktok/birebir_faxefxx_obliv_white_9x16.mp4"
    )
    # 3. Studio White 1:1 Square (Original ref format)
    render_beat_synced_video(
        mode="white_square",
        audio_path="ref_vt_audio.mp3",
        output_path="tiktok/birebir_faxefxx_obliv_square_1x1.mp4"
    )
