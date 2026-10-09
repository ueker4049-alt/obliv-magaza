import os, subprocess, shutil

os.makedirs('tiktok', exist_ok=True)

# 14 brand new, highly targeted TikTok video drops
batch_configs = [
    # 1. Kanye - Heartless
    {
        'out': 'tiktok/obliv_kanye_heartless.mp4',
        'song': 'cut_kanye_heartless.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_streetwear',
        'lead_idx': 1, # Obliv 444 Angel
        'cut_len': 7
    },
    # 2. Lil Uzi - Just Wanna Rock
    {
        'out': 'tiktok/obliv_uzi_wannarock.mp4',
        'song': 'cut_uzi_wannarock.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_drip',
        'lead_idx': 6, # Lil Uzi Vert
        'cut_len': 6
    },
    # 3. Frank Ocean - Lost
    {
        'out': 'tiktok/obliv_frank_lost.mp4',
        'song': 'cut_frank_lost.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_minimal',
        'lead_idx': 8, # Frank Ocean Blonde
        'cut_len': 7
    },
    # 4. Travis Scott - FE!N (Fast pace fit check)
    {
        'out': 'tiktok/obliv_travis_fein_drop2.mp4',
        'song': 'cut_travis_fein.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_favorite',
        'lead_idx': 3, # Travis Scott
        'cut_len': 5
    },
    # 5. Lil Tecca - 500lbs (Weekly rotation)
    {
        'out': 'tiktok/obliv_tecca_500lbs_rotation.mp4',
        'song': 'cut_tecca_500lbs.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_rotation',
        'lead_idx': 2, # Lil Tecca
        'cut_len': 6
    },
    # 6. Kanye West - Bound 2 (Which one would you take?)
    {
        'out': 'tiktok/obliv_kanye_bound2_choice.mp4',
        'song': 'cut_kanye_bound2.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_strikethrough',
        'lead_idx': 0, # Obliv Zé Pequeno
        'cut_len': 7
    },
    # 7. Kendrick Lamar - Not Like Us (Summer streetwear drop)
    {
        'out': 'tiktok/obliv_kendrick_notlikeus_drop2.mp4',
        'song': 'cut_kendrick_notlikeus.mp3',
        'dur': 13.5,
        'hook_dir': 'slides_streetwear',
        'lead_idx': 5, # Rolling Lips
        'cut_len': 6
    },
    # 8. Don Toliver - No Idea (Vibe check)
    {
        'out': 'tiktok/obliv_don_toliver_vibe.mp4',
        'song': 'cut_don_noidea.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_minimal',
        'lead_idx': 7, # I Am Music
        'cut_len': 7
    },
    # 9. Trippie Redd - Miss The Rage (Ultra fast hype cut)
    {
        'out': 'tiktok/obliv_trippie_hype.mp4',
        'song': 'cut_trippie_misstherage.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_favorite',
        'lead_idx': 4, # Trippie Redd 1400
        'cut_len': 5
    },
    # 10. Lil Tecca - Ransom (Viral streetwear fit check)
    {
        'out': 'tiktok/obliv_tecca_ransom_fit.mp4',
        'song': 'cut_tecca_ransom.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_strikethrough',
        'lead_idx': 2, # Lil Tecca
        'cut_len': 6
    },
    # 11. Travis Scott - Goosebumps (Which one is your style?)
    {
        'out': 'tiktok/obliv_travis_goosebumps_style.mp4',
        'song': 'cut_travis_goosebumps.mp3',
        'dur': 13.0,
        'hook_dir': 'slides_wear',
        'lead_idx': 3, # Travis Scott Cactus
        'cut_len': 6
    },
    # 12. Kanye West - Carnival (Best Oversize T-Shirts)
    {
        'out': 'tiktok/obliv_kanye_carnival_best.mp4',
        'song': 'cut_kanye_carnival.mp3',
        'dur': 14.0,
        'hook_dir': 'slides_rotation',
        'lead_idx': 1, # Obliv 444 Angel
        'cut_len': 6
    },
    # 13. Frank Ocean - Novacane (Aesthetic street style)
    {
        'out': 'tiktok/obliv_frank_novacane_aesthetic.mp4',
        'song': 'cut_frank_novacane.mp3',
        'dur': 13.5,
        'hook_dir': 'slides_minimal',
        'lead_idx': 8, # Frank Ocean Blonde
        'cut_len': 7
    },
    # 14. Lil Uzi Vert - 20 Min (Top Sellers Edition)
    {
        'out': 'tiktok/obliv_uzi_20min_bestseller.mp4',
        'song': 'cut_uzi_20min.mp3',
        'dur': 13.5,
        'hook_dir': 'slides_favorite',
        'lead_idx': 6, # Lil Uzi Vert
        'cut_len': 6
    },
]

def render_drop(conf):
    out_video = conf['out']
    temp_dir = 'temp_massive_render'
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

print("Starting mass production of 14 new viral drops...")
for conf in batch_configs:
    render_drop(conf)

print("MASS PRODUCTION COMPLETE: 14 NEW VIRAL VIDEOS CREATED!")
