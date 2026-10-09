py -c "
import cv2
import numpy as np

# Load original frame 35
f = cv2.imread('test_dp_frames/trans1_f035.jpg')
h, w = f.shape[:2]

# Hand mask in stationary frame:
hand_patch = f[720:860, 480:576].copy()
diff = hand_patch[:, :, 2].astype(int) - hand_patch[:, :, 0].astype(int)
skin = (diff > 35) & (hand_patch[:, :, 2] > 120)

full_clean_mask = np.zeros((h, w), dtype=np.uint8)
roi_b = f[310:610, 150:390]
gray_b = cv2.cvtColor(roi_b, cv2.COLOR_BGR2GRAY)
full_clean_mask[310:610, 150:390][gray_b < 210] = 255
full_clean_mask[720:860, 480:576][skin] = 255
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
full_clean_mask = cv2.dilate(full_clean_mask, kernel, iterations=2)

clean_base = cv2.inpaint(f, full_clean_mask, 5, cv2.INPAINT_NS)
soft_mask = cv2.GaussianBlur(full_clean_mask, (25, 25), 0).astype(float) / 255.0
denoised = cv2.bilateralFilter(clean_base, 15, 40, 40)
blended_clean = clean_base.astype(float) * (1.0 - soft_mask[:, :, None]) + denoised.astype(float) * soft_mask[:, :, None]
clean_shirt = np.clip(blended_clean, 0, 255).astype(np.uint8)

# Top shirt polygon
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

# Diagonal peel line
Y, X = np.ogrid[:h, :w]
theta = np.radians(35)
D = X * np.cos(theta) + Y * np.sin(theta)
d_min, d_max = D.min(), D.max()

hand = cv2.imread('hand_isolated.png', cv2.IMREAD_UNCHANGED)

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

def render_shirt(kind):
    canvas = clean_shirt.copy()
    if kind == 'travis':
        face = cv2.imread('pure_face_travis.png')
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
        tw, th = 195, int(tec.shape[0] * (195 / tec.shape[1]))
        rgb = cv2.resize(tec[:, :, :3], (tw, th))
        a = cv2.resize(tec[:, :, 3].astype(float)/255.0, (tw, th))
        x1, y1 = 190, 330
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'trippie':
        tr = cv2.imread('clean_trippie.png', cv2.IMREAD_UNCHANGED)
        tw, th = 200, int(tr.shape[0] * (200 / tr.shape[1]))
        rgb = cv2.resize(tr[:, :, :3], (tw, th))
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        a = cv2.resize(np.clip((245 - gray)/50.0, 0, 1) * (tr[:, :, 3].astype(float)/255.0), (tw, th))
        x1, y1 = 188, 330
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'lips':
        lp = cv2.imread('clean_lips.png', cv2.IMREAD_UNCHANGED)
        tw, th = 200, int(lp.shape[0] * (200 / lp.shape[1]))
        rgb = cv2.resize(lp[:, :, :3], (tw, th))
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        a = cv2.resize(np.clip((250 - gray)/50.0, 0, 1) * (lp[:, :, 3].astype(float)/255.0), (tw, th))
        x1, y1 = 188, 340
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'dollar':
        dl = cv2.imread('clean_dollar.png', cv2.IMREAD_UNCHANGED)
        tw, th = 210, int(dl.shape[0] * (210 / dl.shape[1]))
        rgb = cv2.resize(dl[:, :, :3], (tw, th))
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        a = cv2.resize(np.clip((250 - gray)/50.0, 0, 1) * (dl[:, :, 3].astype(float)/255.0), (tw, th))
        x1, y1 = 183, 330
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'drpepper':
        dp = cv2.imread('clean_drpepper.png', cv2.IMREAD_UNCHANGED)
        tw, th = 190, int(dp.shape[0] * (190 / dp.shape[1]))
        rgb = cv2.resize(dp[:, :, :3], (tw, th))
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        a = cv2.resize(np.clip((250 - gray)/50.0, 0, 1) * (dp[:, :, 3].astype(float)/255.0), (tw, th))
        x1, y1 = 193, 330
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'frank':
        fo = cv2.imread('clean_frank_ocean_graphic.png', cv2.IMREAD_UNCHANGED)[30:, :]
        tw, th = 175, int(fo.shape[0] * (175 / fo.shape[1]))
        rgb = cv2.resize(fo[:, :, :3], (tw, th))
        a = cv2.resize(fo[:, :, 3].astype(float)/255.0, (tw, th))
        x1, y1 = 200, 330
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'iam':
        iam = cv2.imread('crop_graphic_iam.png', cv2.IMREAD_UNCHANGED)
        tw, th = 210, int(iam.shape[0] * (210 / iam.shape[1]))
        rgb = cv2.resize(iam[:, :, :3], (tw, th))
        a = cv2.resize(iam[:, :, 3].astype(float)/255.0, (tw, th))
        x1, y1 = 183, 390
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'uzi':
        uz = cv2.imread('clean_uzi_letters.png', cv2.IMREAD_UNCHANGED)
        tw, th = 210, int(uz.shape[0] * (210 / uz.shape[1]))
        rgb = cv2.resize(uz[:, :, :3], (tw, th))
        a = cv2.resize(uz[:, :, 3].astype(float)/255.0, (tw, th))
        x1, y1 = 183, 390
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    elif kind == 'angel':
        ag = cv2.imread('clean_t1_angel_graphic.png', cv2.IMREAD_UNCHANGED)
        tw, th = 205, int(ag.shape[0] * (205 / ag.shape[1]))
        rgb = cv2.resize(ag[:, :, :3], (tw, th))
        a = cv2.resize(ag[:, :, 3].astype(float)/255.0, (tw, th))
        x1, y1 = 185, 330
        for c in range(3):
            canvas[y1:y1+th, x1:x1+tw, c] = (canvas[y1:y1+th, x1:x1+tw, c] * (1.0 - a) + rgb[:, :, c] * a).astype(np.uint8)
    return canvas

# Pre-render all 10 shirts with hand resting:
shirt_keys = ['travis', 'tecca', 'trippie', 'lips', 'dollar', 'drpepper', 'frank', 'iam', 'uzi', 'angel']
pre_rendered = [add_hand(render_shirt(k), 480, 720) for k in shirt_keys]

# Timing: 10 shirts, total duration = 13.77s (413 frames)
# Exact pull starts from dreampay video:
# Pulls happen at:
# 1: 0..8
# 2: 42..49
# 3: 76..84
# 4: 114..120
# 5: 152..158
# 6: 190..195
# 7: 229..235
# 8: 270..276
# 9: 308..314
# 10: 349..355
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

print('Pre-rendering all 413 video frames...')
out_frames = []
cur_shirt_idx = 0

for f_i in range(413):
    # Check if in a pull interval
    in_pull = False
    for p_idx, (p_start, p_end) in enumerate(pull_intervals):
        if p_start <= f_i <= p_end:
            in_pull = True
            progress = (f_i - p_start) / max(1, (p_end - p_start))
            top_s = pre_rendered[p_idx % len(pre_rendered)]
            next_s = pre_rendered[(p_idx + 1) % len(pre_rendered)]
            
            # Diagonal peel
            cur_d = d_max - progress * (d_max - d_min)
            mask_peel = np.clip((cur_d - D) / 30.0 + 0.5, 0, 1) * poly_soft
            shadow = np.exp(-((D - cur_d) / 20.0) ** 2) * 0.35 * poly_soft
            shadow[D > cur_d] = 0.0
            
            comp = next_s.astype(float) * (1.0 - shadow[:, :, None])
            comp = comp * (1.0 - mask_peel[:, :, None]) + top_s.astype(float) * mask_peel[:, :, None]
            comp = np.clip(comp, 0, 255).astype(np.uint8)
            
            # Moving hand pulling corner
            hx = int(480 + progress * 150)
            hy = int(720 + progress * 200)
            frame_final = add_hand(comp, hx, hy)
            out_frames.append(frame_final)
            break
    if not in_pull:
        # Determine which shirt is currently shown:
        # count how many pulls have completed before f_i
        completed = sum(1 for (s, e) in pull_intervals if e < f_i)
        shown_idx = completed % len(pre_rendered)
        out_frames.append(pre_rendered[shown_idx])

# Write out video using cv2.VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
vw = cv2.VideoWriter('temp_dreampay_raw.mp4', fourcc, 30.0, (w, h))
for f_out in out_frames:
    vw.write(f_out)
vw.release()

print('temp_dreampay_raw.mp4 written, frames:', len(out_frames))
"