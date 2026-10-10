import os
import cv2
import numpy as np
import subprocess
import shutil

def generate_dreampay_exact_video(audio_path, output_path, total_frames=413):
    """
    Recreates the exact @dreampay2 viral TikTok video style:
    Stationary carpet stack base with authentic peeling motion of 10 Obliv t-shirts,
    matching the exact timestamps and movement curves of the reference video.
    """
    temp_dir = f"temp_dp_{os.path.basename(output_path).replace('.mp4','')}"
    os.makedirs(temp_dir, exist_ok=True)
    
    clean_shirt = cv2.imread('master_original_stack_base.jpg')
    if clean_shirt is None:
        raise FileNotFoundError("master_original_stack_base.jpg not found!")
    
    h, w = clean_shirt.shape[:2]
    
    hand = cv2.imread('hand_isolated.png', cv2.IMREAD_UNCHANGED)
    if hand is None:
        raise FileNotFoundError("hand_isolated.png not found!")

    # Helper: overlay isolated hand onto canvas
    def add_hand(canvas, hx, hy):
        res = canvas.copy()
        h_w, h_h = hand.shape[1], hand.shape[0]
        if hx < w and hy < h:
            x_end = min(w, hx + h_w)
            y_end = min(h, hy + h_h)
            sub_w = x_end - hx
            sub_h = y_end - hy
            if sub_w > 0 and sub_h > 0:
                h_a = hand[:sub_h, :sub_w, 3].astype(float) / 255.0
                for c in range(3):
                    res[hy:y_end, hx:x_end, c] = (
                        res[hy:y_end, hx:x_end, c] * (1.0 - h_a) + 
                        hand[:sub_h, :sub_w, c] * h_a
                    ).astype(np.uint8)
        return res

    # Helper: render clean shirt with graphic (without hand)
    def render_shirt(kind):
        canvas = clean_shirt.copy()
        if kind == 'travis':
            face = cv2.imread('pure_face_travis.png')
            if face is None:
                return canvas
            gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            alpha = np.clip((255 - gray).astype(float)/255.0 - 0.05, 0, 1) / 0.95
            tw = 215
            th = int(face.shape[0] * (tw / face.shape[1]))
            f_res = cv2.resize(face, (tw, th))
            a_res = cv2.resize(alpha, (tw, th))
            x1, y1 = 180, 330
            roi_c = canvas[y1:y1+th, x1:x1+tw].astype(float)
            for c in range(3):
                roi_c[:, :, c] = roi_c[:, :, c] * (1.0 - a_res * (1.0 - f_res[:, :, c] / 255.0))
            canvas[y1:y1+th, x1:x1+tw] = np.clip(roi_c, 0, 255).astype(np.uint8)
        elif kind == 'tecca':
            tec = cv2.imread('clean_pure_tecca_chest.png', cv2.IMREAD_UNCHANGED)
            if tec is None:
                return canvas
            tw, th = 195, int(tec.shape[0] * (195 / tec.shape[1]))
            tec_res = cv2.resize(tec, (tw, th))
            rgb = tec_res[:, :, :3]
            a = tec_res[:, :, 3].astype(float)/255.0
            x1, y1 = 190, 330
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'trippie':
            tr = cv2.imread('clean_trippie.png', cv2.IMREAD_UNCHANGED)
            if tr is None:
                return canvas
            tw, th = 200, int(tr.shape[0] * (200 / tr.shape[1]))
            tr_res = cv2.resize(tr, (tw, th))
            rgb = tr_res[:, :, :3]
            a_orig = tr_res[:, :, 3].astype(float)/255.0
            gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            a = np.clip((245 - gray)/50.0, 0, 1) * a_orig
            x1, y1 = 188, 330
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'lips':
            lp = cv2.imread('clean_lips.png', cv2.IMREAD_UNCHANGED)
            if lp is None:
                return canvas
            tw, th = 200, int(lp.shape[0] * (200 / lp.shape[1]))
            lp_res = cv2.resize(lp, (tw, th))
            rgb = lp_res[:, :, :3]
            a_orig = lp_res[:, :, 3].astype(float)/255.0
            gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            a = np.clip((250 - gray)/50.0, 0, 1) * a_orig
            x1, y1 = 188, 340
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'dollar':
            dl = cv2.imread('clean_dollar.png', cv2.IMREAD_UNCHANGED)
            if dl is None:
                return canvas
            tw, th = 210, int(dl.shape[0] * (210 / dl.shape[1]))
            dl_res = cv2.resize(dl, (tw, th))
            rgb = dl_res[:, :, :3]
            a_orig = dl_res[:, :, 3].astype(float)/255.0
            gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            a = np.clip((250 - gray)/50.0, 0, 1) * a_orig
            x1, y1 = 183, 330
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'drpepper':
            dp = cv2.imread('clean_drpepper.png', cv2.IMREAD_UNCHANGED)
            if dp is None:
                return canvas
            tw, th = 190, int(dp.shape[0] * (190 / dp.shape[1]))
            dp_res = cv2.resize(dp, (tw, th))
            rgb = dp_res[:, :, :3]
            a_orig = dp_res[:, :, 3].astype(float)/255.0
            gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
            a = np.clip((250 - gray)/50.0, 0, 1) * a_orig
            x1, y1 = 193, 330
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'frank':
            fo_raw = cv2.imread('clean_frank_ocean_graphic.png', cv2.IMREAD_UNCHANGED)
            if fo_raw is None:
                return canvas
            fo = fo_raw[30:, :]
            tw, th = 175, int(fo.shape[0] * (175 / fo.shape[1]))
            fo_res = cv2.resize(fo, (tw, th))
            rgb = fo_res[:, :, :3]
            a = fo_res[:, :, 3].astype(float)/255.0
            x1, y1 = 200, 330
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'iam':
            iam = cv2.imread('crop_graphic_iam.png', cv2.IMREAD_UNCHANGED)
            if iam is None:
                return canvas
            tw, th = 210, int(iam.shape[0] * (210 / iam.shape[1]))
            iam_res = cv2.resize(iam, (tw, th))
            rgb = iam_res[:, :, :3]
            a = iam_res[:, :, 3].astype(float)/255.0
            x1, y1 = 183, 390
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'uzi':
            uz = cv2.imread('clean_uzi_letters.png', cv2.IMREAD_UNCHANGED)
            if uz is None:
                return canvas
            tw, th = 210, int(uz.shape[0] * (210 / uz.shape[1]))
            uz_res = cv2.resize(uz, (tw, th))
            rgb = uz_res[:, :, :3]
            a = uz_res[:, :, 3].astype(float)/255.0
            x1, y1 = 183, 390
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        elif kind == 'angel':
            ag = cv2.imread('clean_t1_angel_graphic.png', cv2.IMREAD_UNCHANGED)
            if ag is None:
                return canvas
            tw, th = 205, int(ag.shape[0] * (205 / ag.shape[1]))
            ag_res = cv2.resize(ag, (tw, th))
            rgb = ag_res[:, :, :3]
            a = ag_res[:, :, 3].astype(float)/255.0
            x1, y1 = 185, 330
            for c in range(3):
                canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
        return canvas

    # Pre-render clean shirts
    shirt_keys = ['travis', 'tecca', 'trippie', 'lips', 'dollar', 'drpepper', 'frank', 'iam', 'uzi', 'angel']
    clean_shirts = [render_shirt(k) for k in shirt_keys]

    # Top shirt polygon for diagonal peeling
    pts = np.array([
        [200, 190], [270, 185], [360, 200], [420, 230], # collar
        [480, 240], [530, 270], [570, 340], [520, 460], # right sleeve
        [480, 450], [480, 780], [490, 800],             # right torso & hem
        [100, 800], [110, 480],                          # bottom hem & left torso
        [40, 480], [0, 360], [40, 280], [130, 230]       # left sleeve
    ], dtype=np.int32)
    shirt_poly = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(shirt_poly, [pts], 255)
    poly_soft = cv2.GaussianBlur(shirt_poly, (7, 7), 0).astype(float) / 255.0

    # Diagonal coordinates
    Y, X = np.ogrid[:h, :w]
    theta = np.radians(35)
    D = X * np.cos(theta) + Y * np.sin(theta)
    d_min, d_max = D.min(), D.max()

    # Exact pull intervals from dreampay reference video (30 fps)
    pull_intervals = [
        (0, 10),
        (41, 50),
        (76, 85),
        (114, 122),
        (152, 160),
        (190, 197),
        (229, 237),
        (270, 278),
        (308, 316),
        (349, 357)
    ]

    print(f"Rendering {total_frames} frames for {output_path}...")
    for f_i in range(total_frames):
        frame_final = clean_shirts[0]
        in_pull = False
        for p_idx, (p_start, p_end) in enumerate(pull_intervals):
            if p_start <= f_i <= p_end:
                in_pull = True
                progress = (f_i - p_start) / max(1, (p_end - p_start))
                top_s = clean_shirts[p_idx % len(clean_shirts)]
                next_s = clean_shirts[(p_idx + 1) % len(clean_shirts)]
                
                # Diagonal peel equation
                cur_d = d_max - progress * (d_max - d_min)
                mask_peel = np.clip((cur_d - D) / 30.0 + 0.5, 0, 1) * poly_soft
                shadow = np.exp(-((D - cur_d) / 20.0) ** 2) * 0.35 * poly_soft
                shadow[D > cur_d] = 0.0
                
                comp = next_s.astype(float) * (1.0 - shadow[:, :, None])
                comp = comp * (1.0 - mask_peel[:, :, None]) + top_s.astype(float) * mask_peel[:, :, None]
                comp = np.clip(comp, 0, 255).astype(np.uint8)
                
                # Hand pulling bottom corner towards camera right
                hx = int(480 + progress * 150)
                hy = int(720 + progress * 200)
                frame_final = add_hand(comp, hx, hy)
                break
        
        if not in_pull:
            completed = sum(1 for (s, e) in pull_intervals if e < f_i)
            shown_idx = completed % len(clean_shirts)
            # Stationary hand resting on corner
            frame_final = add_hand(clean_shirts[shown_idx], 480, 720)

        # Scale to 1080x1920 for crystal clear TikTok HD
        frame_hd = cv2.resize(frame_final, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
        cv2.imwrite(os.path.join(temp_dir, f"frame_{f_i:05d}.jpg"), frame_hd, [cv2.IMWRITE_JPEG_QUALITY, 93])

    duration = total_frames / 30.0
    print(f"Frames written. Compiling video with audio ({audio_path})...")
    cmd = (
        f'ffmpeg -y -framerate 30 -i "{temp_dir}/frame_%05d.jpg" '
        f'-i "{audio_path}" -t {duration:.2f} '
        f'-c:v libx264 -pix_fmt yuv420p -preset fast -crf 19 '
        f'-c:a aac -b:a 192k -shortest "{output_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Done! Rendered:", output_path)

if __name__ == '__main__':
    # 1. Primary Dreampay with original viral sound
    generate_dreampay_exact_video(
        audio_path='cut_dreampay.mp3',
        output_path='tiktok/birebir_dreampay_viral_stack.mp4'
    )
    # 2. Dreampay with Lil Tecca - 500 lbs
    generate_dreampay_exact_video(
        audio_path='cut_tecca_500lbs.mp3',
        output_path='tiktok/birebir_dreampay_tecca_500lbs.mp4'
    )
