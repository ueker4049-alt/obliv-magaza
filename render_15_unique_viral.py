import os, subprocess, shutil, random

# --------------------------------------------------------------------
# 15 UNIQUE VIRAL TRACKS (Every single video has a completely unique song)
# No soundless videos, no duplicate songs!
# --------------------------------------------------------------------
track_configs = [
    # 1.mp4: Original TikTok reference sound (Teresa..vsp) with signature Obliv drop timing
    (1, 'tiktok_ref_exact.aac', 11.11, 'signature_tiktok'),
    # 2.mp4: Instagram Click Beat drop
    (2, 'insta_music_with_clicks.wav', 11.07, 'click_beat_drop'),
    # 3.mp4: Carnival Viral Bass Drop
    (3, 'carnival_viral_cut.mp3', 16.00, 'bass_drop_punch'),
    # 4.mp4: OblivWear Viral Rap Flow (13.6s)
    (4, 'audio_oblivwear_viral.mp3', 13.59, 'rap_flow_rhythm'),
    # 5.mp4: Viral Beat Section 1 (13s)
    (5, 'audio_viral_beat_13s.mp3', 13.00, 'smooth_streetwear_cut'),
    # 6.mp4: Viral Beat Section 2 (14s)
    (6, 'audio_viral_beat_14s.mp3', 14.00, 'punch_zoom_bounce'),
    # 7.mp4: Viral Beat Section 3 (15s)
    (7, 'audio_viral_beat_15s.mp3', 15.00, 'tempo_acceleration'),
    # 8.mp4: Viral Beat Section 4 (16s)
    (8, 'audio_viral_beat_16s.mp3', 16.00, 'catalog_parade'),
    # 9.mp4: Viral Beat Section 5 (12s)
    (9, 'audio_viral_beat_12s.mp3', 12.00, 'fast_drop_sync'),
    # 10.mp4: Viral Beat Section 6 (14.5s)
    (10, 'audio_viral_beat_14_5s.mp3', 14.50, 'rhythmic_switch'),
    # 11.mp4: Viral Beat Section 7 (15.5s)
    (11, 'audio_viral_beat_15_5s.mp3', 15.50, 'double_pop_detail'),
    # 12.mp4: Viral Drop Cut A (11.17s)
    (12, 'tiktok_viral_cut_a.mp3', 11.17, 'reverse_drop_flow'),
    # 13.mp4: Viral Drop Cut B (16s)
    (13, 'tiktok_viral_cut_b.mp3', 16.00, 'high_energy_pulse'),
    # 14.mp4: Viral Drop Cut C (12s)
    (14, 'tiktok_viral_cut_c.mp3', 12.00, 'triplet_bounce'),
    # 15.mp4: Viral Drop Cut D (14s)
    (15, 'tiktok_viral_cut_d.mp3', 14.00, 'finale_grand_showcase'),
]

os.makedirs('tiktok', exist_ok=True)

# Solo slides with branded top-right logo
branded_slides = [f"solo_slides_branded/slide_{i:02d}.jpg" for i in range(9)]
zoom_slides = [f"solo_slides_branded/zooms/slide_{i:02d}_zoom.jpg" for i in range(9)]

# Reference signature cut indices for 11s TikTok format
cut_indices_ref = [
    1, 16, 21, 26, 31, 36, 41, 46, 56, 61,
    76, 81, 86, 96, 101, 111, 126, 136, 141, 146,
    151, 161, 166, 176, 181, 186, 196, 201, 206, 211,
    221, 226, 236, 251, 256, 261, 276, 281, 291, 296,
    301, 306, 311, 316, 321, 326, 335
]

def build_frame_sequence(style, total_frames):
    sequence = []
    
    if style == 'signature_tiktok':
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_indices_ref) - 1 and f >= cut_indices_ref[seg_idx + 1]:
                seg_idx += 1
                cur_p = (cur_p + 1) % len(branded_slides)
            sequence.append(branded_slides[cur_p])
            
    elif style == 'click_beat_drop':
        # Curated streetwear order [1, 3, 0, 5, 2, 7, 4, 8, 6]
        order = [branded_slides[i] for i in [1, 3, 0, 5, 2, 7, 4, 8, 6]]
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_indices_ref) - 1 and f >= cut_indices_ref[seg_idx + 1]:
                seg_idx += 1
                cur_p = (cur_p + 1) % len(order)
            sequence.append(order[cur_p])
            
    elif style == 'bass_drop_punch':
        # Alternating standard and punch zoom on bass hit every 9 frames
        cut_len = 9
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            if chunk % 2 == 0:
                sequence.append(branded_slides[idx])
            else:
                sequence.append(zoom_slides[idx])
                
    elif style == 'rap_flow_rhythm':
        # Rapid rhythmic 8-frame cuts (approx 3.7 cuts/sec)
        cut_len = 8
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            sequence.append(branded_slides[idx])
            
    elif style == 'smooth_streetwear_cut':
        # 10-frame cuts with alternating order
        cut_len = 10
        order = [branded_slides[i] for i in [0, 2, 4, 6, 8, 1, 3, 5, 7]]
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(order)
            sequence.append(order[idx])
            
    elif style == 'punch_zoom_bounce':
        # 7-frame cut alternating zoom and wide
        cut_len = 7
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(branded_slides)
            sequence.append(zoom_slides[idx] if chunk % 2 else branded_slides[idx])
            
    elif style == 'tempo_acceleration':
        # Pacing gets faster and faster across 15s!
        cuts = [14, 14, 12, 12, 10, 10, 8, 8, 6, 6, 5, 5, 5, 5, 5]
        cur_f = 0
        p_idx = 0
        for c in cuts:
            for _ in range(c):
                if len(sequence) < total_frames:
                    sequence.append(branded_slides[p_idx % len(branded_slides)])
            p_idx += 1
        # Fill rest with fast 5 frames
        while len(sequence) < total_frames:
            sequence.append(branded_slides[p_idx % len(branded_slides)])
            p_idx += 1
            
    elif style == 'catalog_parade':
        # 11 frames per product
        cut_len = 11
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            sequence.append(branded_slides[idx])
            
    elif style == 'fast_drop_sync':
        # Snappy 6-frame cuts (5 cuts/sec)
        cut_len = 6
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            sequence.append(branded_slides[idx])
            
    elif style == 'rhythmic_switch':
        # Order reverse with punch zooms
        rev = branded_slides[::-1]
        rev_zoom = zoom_slides[::-1]
        cut_len = 8
        for f in range(1, total_frames + 1):
            chunk = (f - 1) // cut_len
            idx = (chunk // 2) % len(rev)
            sequence.append(rev_zoom[idx] if chunk % 2 else rev[idx])
            
    elif style == 'double_pop_detail':
        # 4 frames zoom pop then 10 frames wide
        pattern_len = 14
        for f in range(1, total_frames + 1):
            rem = (f - 1) % pattern_len
            idx = ((f - 1) // pattern_len) % len(branded_slides)
            if rem < 4:
                sequence.append(zoom_slides[idx])
            else:
                sequence.append(branded_slides[idx])
                
    elif style == 'reverse_drop_flow':
        rev_order = [branded_slides[i] for i in [8, 7, 6, 5, 4, 3, 2, 1, 0]]
        seg_idx = 0
        cur_p = 0
        for f in range(1, total_frames + 1):
            if seg_idx < len(cut_indices_ref) - 1 and f >= cut_indices_ref[seg_idx + 1]:
                seg_idx += 1
                cur_p = (cur_p + 1) % len(rev_order)
            sequence.append(rev_order[cur_p])
            
    elif style == 'high_energy_pulse':
        # High energy 7-frame cuts
        cut_len = 7
        order = [branded_slides[i] for i in [2, 0, 7, 3, 8, 1, 6, 4, 5]]
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(order)
            sequence.append(order[idx])
            
    elif style == 'triplet_bounce':
        # Triplet cuts: 5-5-10 pattern
        triplet = [5, 5, 10]
        cur_idx = 0
        t_ptr = 0
        while len(sequence) < total_frames:
            dur = triplet[t_ptr % len(triplet)]
            slide = zoom_slides[cur_idx % len(zoom_slides)] if (t_ptr % 3 == 0) else branded_slides[cur_idx % len(branded_slides)]
            for _ in range(dur):
                if len(sequence) < total_frames:
                    sequence.append(slide)
            cur_idx += 1
            t_ptr += 1
            
    elif style == 'finale_grand_showcase':
        # 8-frame cuts rotating all 9 shirts smoothly
        cut_len = 8
        for f in range(1, total_frames + 1):
            idx = ((f - 1) // cut_len) % len(branded_slides)
            sequence.append(branded_slides[idx])
            
    # Guarantee exact frame count
    if len(sequence) < total_frames:
        sequence += [branded_slides[0]] * (total_frames - len(sequence))
    return sequence[:total_frames]

def render_one(vid_num, audio_p, dur, style):
    out_video = f"tiktok/{vid_num}.mp4"
    temp_dir = f"temp_render_{vid_num}"
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = int(dur * fps)
    frames = build_frame_sequence(style, total_frames)
    
    for i, slide_path in enumerate(frames, 1):
        shutil.copyfile(slide_path, f"{temp_dir}/frame_{i:04d}.jpg")
        
    cmd = [
        'ffmpeg', '-y',
        '-framerate', '30',
        '-i', f'{temp_dir}/frame_%04d.jpg',
        '-i', audio_p,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        out_video
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"SUCCESS: Rendered {out_video} ({dur}s | {audio_p} | {style})")

print("Rendering 15 unique viral videos...")
for vid_num, audio_p, dur, style in track_configs:
    print(f"--> Building {vid_num}.mp4...")
    render_one(vid_num, audio_p, dur, style)

print("ALL 15 DISTINCT VIRAL TIKTOK VIDEOS PRODUCED SUCCESSFULLY!")
