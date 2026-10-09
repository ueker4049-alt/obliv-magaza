import os, subprocess, shutil

os.makedirs('tiktok', exist_ok=True)

# 12 Flagship TikTok Drops with Viral Hip-Hop Songs & No Zoom Pure Clean Cuts:
drop_configs = [
    # 1. Tecca 500lbs
    {
        'out': 'tiktok/obliv_tecca_500lbs.mp4',
        'song': 'cut_tecca_500lbs.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_pov',
        'lead_idx': 2, # Lil Tecca
        'cut_len': 6 # 140 BPM
    },
    # 2. Travis Scott FE!N
    {
        'out': 'tiktok/obliv_travis_fein.mp4',
        'song': 'cut_travis_fein.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_pov',
        'lead_idx': 3, # Travis Scott Cactus
        'cut_len': 6 # 150 BPM
    },
    # 3. Travis Scott Goosebumps
    {
        'out': 'tiktok/obliv_travis_goosebumps.mp4',
        'song': 'cut_travis_goosebumps.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_drip',
        'lead_idx': 3, # Travis Scott Cactus
        'cut_len': 7 # 130 BPM
    },
    # 4. Kanye West Bound 2
    {
        'out': 'tiktok/obliv_kanye_bound2.mp4',
        'song': 'cut_kanye_bound2.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_fitcheck',
        'lead_idx': 0, # Obliv Zé Pequeno
        'cut_len': 8 # 149 BPM
    },
    # 5. Kanye West Carnival
    {
        'out': 'tiktok/obliv_kanye_carnival.mp4',
        'song': 'cut_kanye_carnival.mp3',
        'dur': 14.0,
        'hook_dir': 'slides_best',
        'lead_idx': 7, # I Am Music
        'cut_len': 6 # 148 BPM
    },
    # 6. Kanye West Flashing Lights
    {
        'out': 'tiktok/obliv_kanye_flashing_lights.mp4',
        'song': 'cut_kanye_flashing.mp3',
        'dur': 14.0,
        'hook_dir': 'slides_pov',
        'lead_idx': 1, # Obliv 444 Angel
        'cut_len': 10 # 90 BPM
    },
    # 7. Frank Ocean Novacane
    {
        'out': 'tiktok/obliv_frank_novacane.mp4',
        'song': 'cut_frank_novacane.mp3',
        'dur': 13.5,
        'hook_dir': 'slides_wear',
        'lead_idx': 8, # Frank Ocean Blonde
        'cut_len': 7 # 120 BPM
    },
    # 8. Lil Uzi Vert 20 Min
    {
        'out': 'tiktok/obliv_uzi_20min.mp4',
        'song': 'cut_uzi_20min.mp3',
        'dur': 13.5,
        'hook_dir': 'slides_pov',
        'lead_idx': 6, # Lil Uzi Vert
        'cut_len': 7 # 131 BPM
    },
    # 9. Trippie Redd Miss The Rage
    {
        'out': 'tiktok/obliv_trippie_miss_the_rage.mp4',
        'song': 'cut_trippie_misstherage.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_drip',
        'lead_idx': 4, # Trippie Redd 1400
        'cut_len': 6 # 160 BPM
    },
    # 10. Kendrick Lamar Not Like Us
    {
        'out': 'tiktok/obliv_kendrick_not_like_us.mp4',
        'song': 'cut_kendrick_notlikeus.mp3',
        'dur': 13.5,
        'hook_dir': 'slides_best',
        'lead_idx': 5, # Rolling Lips Acid
        'cut_len': 7 # 101 BPM
    },
    # 11. Lil Tecca Ransom
    {
        'out': 'tiktok/obliv_tecca_ransom.mp4',
        'song': 'cut_tecca_ransom.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_fitcheck',
        'lead_idx': 2, # Lil Tecca
        'cut_len': 5 # 180 BPM
    },
    # 12. Don Toliver No Idea
    {
        'out': 'tiktok/obliv_don_toliver_no_idea.mp4',
        'song': 'cut_don_noidea.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_obliv',
        'lead_idx': 1, # Obliv 444 Angel
        'cut_len': 7 # 128 BPM
    },
]

def render_drop(conf):
    out_video = conf['out']
    temp_dir = 'temp_drop_render'
    os.makedirs(temp_dir, exist_ok=True)
    
    fps = 30
    total_frames = int(conf['dur'] * fps)
    
    hook_dir = conf['hook_dir']
    slides = [f"{hook_dir}/slide_{i:02d}.jpg" for i in range(9)]
    
    lead = conf['lead_idx']
    cut_len = conf['cut_len']
    order = [lead] + [i for i in range(9) if i != lead]
    
    # Pure clean cut, zero zoom
    frames = []
    for f in range(1, total_frames + 1):
        chunk = (f - 1) // cut_len
        idx = order[chunk % len(order)]
        frames.append(slides[idx])
        
    for i, slide_p in enumerate(frames, 1):
        shutil.copyfile(slide_p, f"{temp_dir}/frame_{i:04d}.jpg")
        
    cmd = [
        'ffmpeg', '-y',
        '-framerate', '30',
        '-i', f'{temp_dir}/frame_%04d.jpg',
        '-i', conf['song'],
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-g', '30',
        '-keyint_min', '15',
        '-sc_threshold', '0',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        out_video
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"Rendered -> {out_video}")

print("Starting production of 12 new viral streetwear TikTok drops...")
for conf in drop_configs:
    render_drop(conf)

print("ALL 12 NEW TIKTOK VIDEOS PRODUCED WITH FULL PRODUCTION QUALITY!")
