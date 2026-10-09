import os, subprocess, shutil, random

# Audio palette
# We will create 15 additional videos: 5.mp4 to 19.mp4
# Total videos will be 1 to 19 (19 videos total, or user asked 15 more)
os.makedirs('tiktok', exist_ok=True)

branded_slides = [f"solo_slides_branded/slide_{i:02d}.jpg" for i in range(9)]
zoom_slides = [f"solo_slides_branded/zooms/slide_{i:02d}_zoom.jpg" for i in range(9)]

# Common cut markers for 11.17s audio (335 frames at 30 fps)
cut_frame_indices_11s = [
    1, 16, 21, 26, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

# Variations definition: (video_num, audio_file, style_mode, total_seconds)
# style_modes:
# 'rhythmic_cycle': uses cut_frame_indices_11s with different slide permutations
# 'rapid_cut': fast cuts every N frames
# 'punch_zoom': alternating between standard slide and zoom slide
# 'reverse_cycle': reverse order rhythmic cuts

variations = [
    # 5.mp4: Exact TikTok sound with reverse order
    (5, 'tiktok_ref_exact.aac', 'rhythmic_reverse', 11.17),
    # 6.mp4: Exact TikTok sound with punch zoom
    (6, 'tiktok_ref_exact.aac', 'rhythmic_zoom_alt', 11.17),
    # 7.mp4: Click beat with random permutation
    (7, 'insta_music_with_clicks.wav', 'shuffled_rapid', 11.07),
    # 8.mp4: Click beat with punch zoom
    (8, 'insta_music_with_clicks.wav', 'punch_zoom', 11.07),
    # 9.mp4: Only clicks (ASMR streetwear drops)
    (9, 'only_clicks.wav', 'rhythmic_cycle_b', 11.17),
    # 10.mp4: Carnival bass drop with reverse order
    (10, 'carnival_viral_cut.mp3', 'rapid_cut_6', 16.0),
    # 11.mp4: Carnival bass drop with alternating punch zoom
    (11, 'carnival_viral_cut.mp3', 'punch_zoom_fast', 16.0),
    # 12.mp4: Trend beat 18s smooth rhythm
    (12, 'tiktok_trend_beat.wav', 'rhythmic_18s', 18.0),
    # 13.mp4: Trend beat 18s rapid beat-drop
    (13, 'tiktok_trend_beat.wav', 'punch_zoom_18s', 18.0),
    # 14.mp4: Viral cut A (11.17s) snappy rhythmic
    (14, 'tiktok_viral_cut_a.mp3', 'rhythmic_cycle_c', 11.17),
    # 15.mp4: Viral cut B (16s) fast streetwear showcase
    (15, 'tiktok_viral_cut_b.mp3', 'rapid_cut_8', 16.0),
    # 16.mp4: Viral cut C (12s) high-energy drop
    (16, 'tiktok_viral_cut_c.mp3', 'punch_zoom_12s', 12.0),
    # 17.mp4: Viral cut D (14s) punchy transition
    (17, 'tiktok_viral_cut_d.mp3', 'rapid_cut_7', 14.0),
    # 18.mp4: Exact TikTok sound with double-cut bounce
    (18, 'tiktok_ref_exact.aac', 'double_cut', 11.17),
    # 19.mp4: Click beat ultra rapid finale
    (19, 'insta_music_with_clicks.wav', 'ultra_rapid', 11.07),
]

def render_variation(vid_num, audio_path, mode, duration_sec):
    out_video = f"tiktok/{vid_num}.mp4"
    temp_dir = f"temp_var_{vid_num}"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = int(duration_sec * fps)
    
    frames_sequence = []
    
    if mode == 'rhythmic_reverse':
        # reverse order of branded_slides
        rev_slides = branded_slides[::-1]
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_frame_indices_11s) - 1:
                if f >= cut_frame_indices_11s[seg_idx + 1]:
                    seg_idx += 1
                    cur_p = (cur_p + 1) % len(rev_slides)
            frames_sequence.append(rev_slides[cur_p])
            
    elif mode == 'rhythmic_zoom_alt':
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_frame_indices_11s) - 1:
                if f >= cut_frame_indices_11s[seg_idx + 1]:
                    seg_idx += 1
                    cur_p = (cur_p + 1) % (len(branded_slides) * 2)
            # Alternates between standard and zoom
            p_idx = (cur_p // 2) % len(branded_slides)
            if cur_p % 2 == 0:
                frames_sequence.append(branded_slides[p_idx])
            else:
                frames_sequence.append(zoom_slides[p_idx])
                
    elif mode == 'shuffled_rapid':
        # Curated streetwear shuffle: [2, 5, 8, 1, 4, 7, 0, 3, 6]
        shuff = [branded_slides[i] for i in [2, 5, 8, 1, 4, 7, 0, 3, 6]]
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_frame_indices_11s) - 1:
                if f >= cut_frame_indices_11s[seg_idx + 1]:
                    seg_idx += 1
                    cur_p = (cur_p + 1) % len(shuff)
            frames_sequence.append(shuff[cur_p])
            
    elif mode == 'punch_zoom':
        # Alternating 8 frames normal, 8 frames zoom
        cut_len = 8
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            p_idx = (chunk // 2) % len(branded_slides)
            if chunk % 2 == 0:
                frames_sequence.append(branded_slides[p_idx])
            else:
                frames_sequence.append(zoom_slides[p_idx])
                
    elif mode == 'rhythmic_cycle_b':
        # Offset start by 4 products
        offset_slides = branded_slides[4:] + branded_slides[:4]
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_frame_indices_11s) - 1:
                if f >= cut_frame_indices_11s[seg_idx + 1]:
                    seg_idx += 1
                    cur_p = (cur_p + 1) % len(offset_slides)
            frames_sequence.append(offset_slides[cur_p])
            
    elif mode == 'rapid_cut_6':
        # Cut every 6 frames (5 cuts per second)
        cut_len = 6
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            frames_sequence.append(branded_slides[idx])
            
    elif mode == 'punch_zoom_fast':
        # Cut every 6 frames alternating standard and zoom
        cut_len = 6
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            if chunk % 2 == 0:
                frames_sequence.append(branded_slides[idx])
            else:
                frames_sequence.append(zoom_slides[idx])
                
    elif mode == 'rhythmic_18s':
        # 18 seconds rhythm: cut every 10 frames
        cut_len = 10
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            frames_sequence.append(branded_slides[idx])
            
    elif mode == 'punch_zoom_18s':
        # 18 seconds punch zoom: cut every 9 frames
        cut_len = 9
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            if chunk % 2 == 0:
                frames_sequence.append(branded_slides[idx])
            else:
                frames_sequence.append(zoom_slides[idx])
                
    elif mode == 'rhythmic_cycle_c':
        order = [branded_slides[i] for i in [0, 8, 1, 7, 2, 6, 3, 5, 4]]
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_frame_indices_11s) - 1:
                if f >= cut_frame_indices_11s[seg_idx + 1]:
                    seg_idx += 1
                    cur_p = (cur_p + 1) % len(order)
            frames_sequence.append(order[cur_p])
            
    elif mode == 'rapid_cut_8':
        cut_len = 8
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            frames_sequence.append(branded_slides[idx])
            
    elif mode == 'punch_zoom_12s':
        cut_len = 7
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            if chunk % 2 == 0:
                frames_sequence.append(branded_slides[idx])
            else:
                frames_sequence.append(zoom_slides[idx])
                
    elif mode == 'rapid_cut_7':
        cut_len = 7
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            frames_sequence.append(branded_slides[idx])
            
    elif mode == 'double_cut':
        # Quick double pop then steady: 3 frames zoom, 12 frames normal
        pattern_len = 15
        for f in range(1, total_frames + 1):
            rem = (f - 1) % pattern_len
            idx = ((f - 1) // pattern_len) % len(branded_slides)
            if rem < 4:
                frames_sequence.append(zoom_slides[idx])
            else:
                frames_sequence.append(branded_slides[idx])
                
    elif mode == 'ultra_rapid':
        cut_len = 5 # 6 cuts per second!
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            frames_sequence.append(branded_slides[idx])
    else:
        for f in range(1, total_frames + 1):
            frames_sequence.append(branded_slides[0])

    # Copy frame files
    for frame_no, slide_f in enumerate(frames_sequence, 1):
        shutil.copyfile(slide_f, f"{temp_dir}/frame_{frame_no:04d}.jpg")

    cmd = [
        'ffmpeg', '-y',
        '-framerate', '30',
        '-i', f'{temp_dir}/frame_%04d.jpg',
        '-i', audio_path,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        out_video
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Rendered {out_video} ({duration_sec}s, mode: {mode})")

for vid_num, audio_p, mode, dur in variations:
    print(f"Processing {vid_num}.mp4...")
    render_variation(vid_num, audio_p, mode, dur)

print("ALL 15 NEW TIKTOK VIDEOS (5.mp4 to 19.mp4) COMPLETED!")
