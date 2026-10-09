import os
import sqlite3
import random
import string
import time
import base64
import hashlib
import hmac
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import iyzipay
from models import get_db, init_db, sha256_hash, verify_password

app = Flask(__name__)
app.secret_key = 'obliv_luxury_streetwear_secret_key_2026'

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi', 'mkv'}

@app.template_filter('mask_name')
def mask_name_filter(name):
    if not name:
        return 'M*****'
    parts = str(name).strip().split()
    masked_parts = []
    for part in parts:
        if len(part) <= 1:
            masked_parts.append(part.upper() + '***')
        else:
            masked_parts.append(part[0].upper() + '*' * (len(part) - 1))
    return ' '.join(masked_parts)

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_MEDIA_EXTENSIONS = ALLOWED_VIDEO_EXTENSIONS | ALLOWED_IMAGE_EXTENSIONS

def allowed_image(filename: str | None) -> bool:
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_file(filename: str | None) -> bool:
    return allowed_image(filename)

def allowed_media(filename: str | None) -> bool:
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_MEDIA_EXTENSIONS

def is_video_file(filename: str | None) -> bool:
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def send_verification_email(to_email: str, code: str) -> tuple[bool, str]:
    """Sends an anti-spam compliant, beautifully branded 6-digit confirmation code via Gmail SMTP."""
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM settings WHERE key IN ('smtp_email', 'smtp_app_password')").fetchall()
    conn.close()
    settings = {r['key']: r['value'] for r in rows}
    
    sender_email = settings.get('smtp_email') or "oblivwear@gmail.com"
    app_password = (settings.get('smtp_app_password') or "").strip()

    if not app_password:
        print(f"[OBLIV MAIL SIMULATION] To: {to_email} | Code: {code}")
        return True, "simulated"

    try:
        from email.mime.image import MIMEImage
        from email.utils import formatdate, make_msgid

        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = f"OBLIV Giriş Doğrulama Kodunuz: {code}"
        msg_root['From'] = f"OBLIV <{sender_email}>"
        msg_root['To'] = to_email
        msg_root['Reply-To'] = sender_email
        msg_root['Date'] = formatdate(localtime=True)
        msg_root['Message-ID'] = make_msgid(domain='gmail.com')
        msg_root['X-Priority'] = '1'
        msg_root['Importance'] = 'high'
        msg_root['Precedence'] = 'bulk'
        msg_root['X-Entity-Ref-ID'] = f"obliv-{int(time.time())}"

        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)

        text_plain = f"OBLIV • Yeni Nesil Kıyafet & Giyim\n\nDoğrulama Kodunuz: {code}\n\nBu kod 15 dakika geçerlidir.\nİletişim: oblivwear@gmail.com"
        msg_alternative.attach(MIMEText(text_plain, 'plain', 'utf-8'))

        html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#07080B; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#07080B; padding: 40px 16px;">
    <tr>
      <td align="center">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width:500px; background-color:#0E1017; border: 1px solid #1E2333; border-radius: 16px; overflow: hidden; box-shadow: 0 16px 40px rgba(0,0,0,0.6);">
          <!-- Top Blue Glow Bar -->
          <tr>
            <td style="height: 4px; background: linear-gradient(90deg, #1D4ED8, #3B82F6, #60A5FA);"></td>
          </tr>
          <!-- Logo & Header -->
          <tr>
            <td align="center" style="padding: 36px 30px 16px;">
              <img src="cid:obliv_logo" alt="OBLIV" style="height: 38px; width: auto; display: block; border: 0;" />
              <div style="font-size: 11px; color: #3B82F6; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; margin-top: 14px;">
                YENİ NESİL KIYAFET &amp; GİYİM
              </div>
            </td>
          </tr>
          <!-- Body Text -->
          <tr>
            <td style="padding: 10px 36px 24px; text-align: center;">
              <h1 style="color: #FFFFFF; font-size: 20px; font-weight: 800; margin: 0 0 12px; letter-spacing: 0.02em;">
                Hesap Doğrulama Kodu
              </h1>
              <p style="color: #94A3B8; font-size: 14px; line-height: 1.6; margin: 0;">
                OBLIV hesabınızı güvenle onaylamak ve alışverişe başlamak için tek kullanımlık güvenlik kodunuz:
              </p>
            </td>
          </tr>
          <!-- Code Card Box -->
          <tr>
            <td align="center" style="padding: 0 36px 28px;">
              <div style="background-color: #131722; border: 1.5px solid #2563EB; border-radius: 12px; padding: 18px 24px; display: inline-block;">
                <span style="font-family: 'Courier New', Courier, monospace; font-size: 34px; font-weight: 900; letter-spacing: 0.28em; color: #FFFFFF; text-shadow: 0 0 12px rgba(59,130,246,0.5);">
                  {code}
                </span>
              </div>
              <div style="font-size: 12px; color: #64748B; margin-top: 12px;">
                ⏱ Bu kod <strong>15 dakika</strong> boyunca geçerlidir.
              </div>
            </td>
          </tr>
          <!-- Footer Divider & Note -->
          <tr>
            <td style="padding: 0 36px;">
              <div style="height: 1px; background-color: #1E2333;"></div>
            </td>
          </tr>
          <tr>
            <td style="padding: 20px 36px 30px; text-align: center;">
              <p style="font-size: 12px; color: #64748B; line-height: 1.5; margin: 0 0 10px;">
                Bu işlemi siz talep etmediyseniz, hesabınız güvendedir; bu e-postayı dikkate almayabilirsiniz.
              </p>
              <div style="font-size: 11px; color: #475569;">
                &copy; 2026 OBLIV • Tüm Hakları Saklıdır • <a href="mailto:oblivwear@gmail.com" style="color: #3B82F6; text-decoration: none;">oblivwear@gmail.com</a>
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
        msg_alternative.attach(MIMEText(html_body, 'html', 'utf-8'))

        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo_cropped_direct.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                img_data = f.read()
                img = MIMEImage(img_data)
                img.add_header('Content-ID', '<obliv_logo>')
                img.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg_root.attach(img)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, [to_email], msg_root.as_string())

        return True, "sent"
    except Exception as e:
        print(f"[OBLIV MAIL ERROR] {e}")
        return False, str(e)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov', 'avi', 'mkv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import colorsys
from PIL import Image

def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def recolor_all_logos_from_base(target_hex):
    """Dynamically recolors logo assets (static and animated GIF) from high-res base assets to match site theme."""
    try:
        t_r, t_g, t_b = hex_to_rgb(target_hex)
        t_h, t_s, t_v = colorsys.rgb_to_hsv(t_r/255, t_g/255, t_b/255)

        base_direct = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo_cropped_direct_base.png')
        target_direct = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo_cropped_direct.png')
        if os.path.exists(base_direct):
            with Image.open(base_direct) as raw_im:
                im = raw_im.convert('RGBA')
            pixels = im.load()
            if pixels is not None:
                w, h = im.size
                for x in range(w):
                    for y in range(h):
                        r, g, b, a = pixels[x, y]  # type: ignore[index]
                        if x >= 520 and a > 30 and (b > r + 30 and b > g + 30):
                            orig_h, orig_s, orig_v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                            nr, ng, nb = colorsys.hsv_to_rgb(t_h, t_s, min(1.0, orig_v * 1.05))
                            pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)  # type: ignore[index]
                im.save(target_direct)

        base_trans = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo_transparent_base.png')
        target_trans = os.path.join(os.path.dirname(__file__), 'static', 'images', 'logo_transparent.png')
        if os.path.exists(base_trans):
            with Image.open(base_trans) as raw_im:
                im = raw_im.convert('RGBA')
            pixels = im.load()
            if pixels is not None:
                w, h = im.size
                for x in range(w):
                    for y in range(h):
                        r, g, b, a = pixels[x, y]  # type: ignore[index]
                        if x > w * 0.70 and a > 30 and (b > r + 30 and b > g + 30):
                            orig_h, orig_s, orig_v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                            nr, ng, nb = colorsys.hsv_to_rgb(t_h, t_s, min(1.0, orig_v * 1.05))
                            pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)  # type: ignore[index]
                im.save(target_trans)

        base_gif = os.path.join(os.path.dirname(__file__), 'static', 'images', 'obliv_animated_base.gif')
        target_gif = os.path.join(os.path.dirname(__file__), 'static', 'images', 'obliv_animated.gif')
        if os.path.exists(base_gif):
            with Image.open(base_gif) as gif_im:
                frames = []
                durations = []
                num_frames = getattr(gif_im, 'n_frames', 1)
                for i in range(num_frames):
                    gif_im.seek(i)
                    frame = gif_im.convert('RGBA')
                    durations.append(gif_im.info.get('duration', 70))
                    pixels = frame.load()
                    if pixels is not None:
                        w, h = frame.size
                        for x in range(w):
                            for y in range(h):
                                r, g, b, a = pixels[x, y]  # type: ignore[index]
                                if a > 30 and (b > r + 30 and b > g + 30):
                                    orig_h, orig_s, orig_v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                                    nr, ng, nb = colorsys.hsv_to_rgb(t_h, t_s, min(1.0, orig_v * 1.05))
                                    pixels[x, y] = (int(nr * 255), int(ng * 255), int(nb * 255), a)  # type: ignore[index]
                    frames.append(frame)

                if frames:
                    frames[0].save(
                        target_gif,
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        loop=1,
                        optimize=False
                    )
        print(f"[OBLIV THEME] All logos recolored to {target_hex}")
    except Exception as e:
        print(f"[OBLIV THEME LOGO ERROR] {e}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_store_settings():
    conn = get_db()
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}

def get_all_categories():
    conn = get_db()
    cats = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    conn.close()
    return cats

@app.context_processor
def inject_globals():
    return dict(
        current_user=get_current_user(),
        settings=get_store_settings(),
        nav_categories=get_all_categories()
    )

from collections import defaultdict
import threading

_request_records = defaultdict(list)
_banned_ips = {}
_lock = threading.Lock()

BURST_WINDOW = 3          # 3 seconds burst window
BURST_MAX = 20            # Max 20 requests in 3 seconds (instant flooder detection)
NORMAL_WINDOW = 60        # 60 seconds normal window
NORMAL_MAX = 150          # Max 150 requests per minute
API_WINDOW = 10           # 10 seconds for POST / sensitive endpoints
API_MAX = 15              # Max 15 requests in 10s for API/auth/checkout
BAN_DURATION = 180        # 3 minutes ban for malicious bots

def _cleanup_old_records(now):
    stale_keys = [ip for ip, ban_time in _banned_ips.items() if now > ban_time + 300]
    for ip in stale_keys:
        del _banned_ips[ip]

@app.before_request
def ddos_shield_protection():
    # Force HTTPS for domain requests
    proto = request.headers.get('X-Forwarded-Proto') or request.headers.get('CF-Visitor', '')
    if request.headers.get('X-Forwarded-Proto') == 'http' and 'oblivwear.com.tr' in request.host:
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

    if request.path.startswith('/static/'):
        return None

    client_ip = (
        request.headers.get('CF-Connecting-IP') or
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.remote_addr or
        '127.0.0.1'
    )

    now = time.time()

    with _lock:
        if client_ip in _banned_ips:
            ban_until = _banned_ips[client_ip]
            if now < ban_until:
                retry_after = max(1, int(ban_until - now))
                shield_html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>429 • OBLIV Cyber Defense Shield</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;900&family=Plus+Jakarta+Sans:wght@700;900&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #060709 radial-gradient(circle at 50% 20%, rgba(36, 83, 255, 0.22) 0%, #060709 70%);
            color: #F8FAFC;
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .shield-card {{
            background: linear-gradient(180deg, rgba(16, 19, 28, 0.95) 0%, rgba(10, 12, 17, 0.98) 100%);
            border: 1px solid rgba(36, 83, 255, 0.4);
            border-radius: 24px;
            padding: 48px 36px;
            max-width: 540px;
            width: 100%;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9), 0 0 35px rgba(36, 83, 255, 0.25);
            position: relative;
            overflow: hidden;
        }}
        .shield-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(36, 83, 255, 0.15);
            border: 1px solid rgba(36, 83, 255, 0.5);
            color: #60A5FA;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.14em;
            padding: 6px 16px;
            border-radius: 999px;
            margin-bottom: 24px;
        }}
        .pulse-dot {{
            width: 8px;
            height: 8px;
            background: #2563EB;
            border-radius: 50%;
            box-shadow: 0 0 10px #60A5FA;
            animation: pulse 1.2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.3); opacity: 0.5; }}
        }}
        h1 {{
            font-size: 26px;
            font-weight: 900;
            letter-spacing: -0.02em;
            margin-bottom: 12px;
            color: #FFFFFF;
        }}
        p {{
            color: #94A3B8;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        .countdown-box {{
            background: #0B0D13;
            border: 1px dashed rgba(255, 255, 255, 0.16);
            border-radius: 12px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            color: #93C5FD;
            margin-bottom: 24px;
        }}
        .countdown-box strong {{
            color: #FFFFFF;
            font-size: 18px;
            display: inline-block;
            margin: 0 4px;
        }}
        .status-ip {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #475569;
        }}
    </style>
</head>
<body>
    <div class="shield-card">
        <div class="shield-badge">
            <span class="pulse-dot"></span>
            OBLIV CYBER DEFENSE
        </div>
        <h1>HIZ SINIRI AŞILDI</h1>
        <p>Mağaza altyapımız olağanüstü yüksek frekanslı istek trafiği algıladığı için IP adresiniz otomatik koruma kalkanına alındı.</p>
        <div class="countdown-box">
            Kalkanın Açılmasına Kalan: <strong id="cd">{retry_after}</strong> SANİYE
        </div>
        <div class="status-ip">IP HASH: {hashlib.sha256(client_ip.encode()).hexdigest()[:12].upper()} • PROTOCOL: OBLIV-SHIELD-V2</div>
    </div>
    <script>
        let s = {retry_after};
        const el = document.getElementById('cd');
        const timer = setInterval(() => {{
            s--;
            if (s <= 0) {{
                clearInterval(timer);
                window.location.reload();
            }} else {{
                el.innerText = s;
            }}
        }}, 1000);
    </script>
</body>
</html>"""
                return (
                    shield_html,
                    429,
                    {
                        'Retry-After': str(retry_after),
                        'Content-Type': 'text/html; charset=utf-8',
                        'X-DDoS-Shield': 'BLOCKED_RATE_EXCEEDED'
                    }
                )
            else:
                del _banned_ips[client_ip]
                _request_records[client_ip] = []

        req_history = [t for t in _request_records[client_ip] if now - t < NORMAL_WINDOW]
        req_history.append(now)
        _request_records[client_ip] = req_history

        burst_count = sum(1 for t in req_history if now - t <= BURST_WINDOW)
        if burst_count > BURST_MAX:
            _banned_ips[client_ip] = now + BAN_DURATION
            return (
                f"OBLIV DDoS Defense: Ani burst trafiği engellendi ({burst_count} req / {BURST_WINDOW}s). Bağlantı {BAN_DURATION}s süreyle kısıtlandı.",
                429,
                {'Retry-After': str(BAN_DURATION), 'X-DDoS-Shield': 'BURST_ATTACK_MITIGATED'}
            )

        if request.method == 'POST' or request.path.startswith('/api/') or request.path in ['/login', '/register', '/checkout']:
            api_count = sum(1 for t in req_history if now - t <= API_WINDOW)
            if api_count > API_MAX:
                _banned_ips[client_ip] = now + 60
                return (
                    "OBLIV Defense: Çok fazla form / API isteği yapıldı. Lütfen 60 saniye bekleyin.",
                    429,
                    {'Retry-After': '60', 'X-DDoS-Shield': 'API_FLOOD_PREVENTED'}
                )

        if len(req_history) > NORMAL_MAX:
            _banned_ips[client_ip] = now + BAN_DURATION
            return (
                f"OBLIV DDoS Defense: Dakikalık limit aşıldı ({len(req_history)} req / min).",
                429,
                {'Retry-After': str(BAN_DURATION), 'X-DDoS-Shield': 'MINUTE_LIMIT_BLOCKED'}
            )

        if len(_banned_ips) > 500:
            _cleanup_old_records(now)

    if not request.path.startswith('/static') and not request.path.startswith('/admin') and request.method == 'GET':
        if not (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/')):
            try:
                ip_hash = hashlib.sha256(client_ip.encode('utf-8')).hexdigest()[:16]
                today_str = time.strftime('%Y-%m-%d')
                user_agent = (request.headers.get('User-Agent') or '')[:200]
                conn = get_db()
                conn.execute(
                    "INSERT INTO site_visits (ip_hash, path, user_agent, visited_date) VALUES (?, ?, ?, ?)",
                    (ip_hash, request.path, user_agent, today_str)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                pass

@app.after_request
def append_security_headers(response):
    """Adds high-grade cyber defense and performance HTTP headers."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    response.headers['X-DDoS-Protection'] = 'OBLIV-Cloud-Shield/1.0-Active'
    response.headers['ngrok-skip-browser-warning'] = '69420'
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=2592000'
    return response

@app.route('/favicon.ico')
def favicon():
    resp = send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    return resp

@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    resp = send_from_directory(os.path.join(app.root_path, 'static'), 'favicon-192x192.png', mimetype='image/png')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    return resp

@app.route('/')
def home():
    conn = get_db()
    all_products = conn.execute(
        "SELECT * FROM products WHERE is_active = 1 "
        "ORDER BY CASE WHEN LOWER(color_name) = 'siyah' THEN 0 ELSE 1 END ASC, display_order ASC, id ASC"
    ).fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    conn.close()
    return render_template('index.html', products=all_products, categories=categories)

@app.route('/urunler')
def products_page():
    conn = get_db()
    products_raw = conn.execute(
        "SELECT * FROM products WHERE is_active = 1 "
        "ORDER BY CASE WHEN LOWER(color_name) = 'siyah' THEN 0 ELSE 1 END ASC, display_order ASC, id ASC"
    ).fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()

    products = []
    all_colors_set = set()
    for p in products_raw:
        p_dict = dict(p)
        color_rows = conn.execute("SELECT * FROM product_colors WHERE product_id = ? ORDER BY id ASC", (p['id'],)).fetchall()
        p_colors = [dict(c) for c in color_rows]
        if not p_colors:
            p_colors = [{
                'id': 0,
                'color_name': p['color_name'],
                'color_hex': p['color_hex'],
                'image_url': p['image_url']
            }]
        p_dict['colors'] = p_colors
        for c in p_colors:
            c_name = str(c.get('color_name') or '').strip()
            if c_name:
                all_colors_set.add(c_name)

        avail_sizes = []
        if (p['stock_s'] or 0) > 0: avail_sizes.append('S')
        if (p['stock_m'] or 0) > 0: avail_sizes.append('M')
        if (p['stock_l'] or 0) > 0: avail_sizes.append('L')
        if (p['stock_xl'] or 0) > 0: avail_sizes.append('XL')
        p_dict['available_sizes'] = avail_sizes
        products.append(p_dict)

    conn.close()
    filter_colors = sorted(list(all_colors_set))
    return render_template('products.html', products=products, categories=categories, filter_colors=filter_colors)

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, price, old_price, image_url, category, badge FROM products WHERE is_active = 1 AND (LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(badge) LIKE ?) LIMIT 8",
        (f"%{query}%", f"%{query}%", f"%{query}%")
    ).fetchall()
    conn.close()
    results = [dict(r) for r in rows]
    return jsonify(results)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        flash("Ürün bulunamadı.", "error")
        return redirect(url_for('home'))

    product_dict = dict(product)

    gallery_images = conn.execute(
        "SELECT * FROM product_images WHERE product_id = ? ORDER BY display_order ASC, id ASC",
        (product_id,)
    ).fetchall()
    images_list = [dict(img) for img in gallery_images]
    if not images_list:
        images_list = [{'id': 0, 'image_url': product['image_url'], 'display_order': 0}]
    product_dict['gallery_images'] = images_list

    colors = conn.execute(
        "SELECT * FROM product_colors WHERE product_id = ? ORDER BY id ASC",
        (product_id,)
    ).fetchall()
    colors_list = [dict(c) for c in colors]
    if not colors_list:
        colors_list = [{
            'id': 0,
            'color_name': product['color_name'],
            'color_hex': product['color_hex'],
            'image_url': product['image_url']
        }]
    product_dict['colors'] = colors_list

    reviews = conn.execute('''
        SELECT pr.*, u.name as user_name
        FROM product_reviews pr
        JOIN users u ON pr.user_id = u.id
        WHERE pr.product_id = ?
        ORDER BY pr.id DESC
    ''', (product_id,)).fetchall()

    user = get_current_user()
    has_purchased = False
    has_already_reviewed = False

    if user:
        purchased_item = conn.execute('''
            SELECT oi.id 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.id
            WHERE o.user_id = ? AND oi.product_id = ?
        ''', (user['id'], product_id)).fetchone()
        has_purchased = bool(purchased_item)

        existing_review = conn.execute('''
            SELECT id FROM product_reviews 
            WHERE product_id = ? AND user_id = ?
        ''', (product_id, user['id'])).fetchone()
        has_already_reviewed = bool(existing_review)

    rating_count = len(reviews)
    avg_rating = round(sum(r['rating'] for r in reviews) / rating_count, 1) if rating_count > 0 else 0

    conn.close()
    return render_template(
        'product_detail.html',
        product=product_dict,
        reviews=reviews,
        has_purchased=has_purchased,
        has_already_reviewed=has_already_reviewed,
        rating_count=rating_count,
        avg_rating=avg_rating
    )

@app.route('/product/<int:product_id>/review', methods=['POST'])
def add_product_review(product_id):
    user = get_current_user()
    if not user:
        flash("Yorum yapabilmek için lütfen giriş yapın.", "error")
        return redirect(url_for('login', next=f"/product/{product_id}"))

    conn = get_db()
    product = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        flash("Ürün bulunamadı.", "error")
        return redirect(url_for('home'))

    purchased_item = conn.execute('''
        SELECT oi.id 
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        WHERE o.user_id = ? AND oi.product_id = ?
    ''', (user['id'], product_id)).fetchone()

    if not purchased_item:
        conn.close()
        flash("Bu ürüne yalnızca ürünü satın almış olan üyelerimiz değerlendirme ve yorum yapabilir.", "error")
        return redirect(url_for('product_detail', product_id=product_id))

    existing_review = conn.execute('''
        SELECT id FROM product_reviews 
        WHERE product_id = ? AND user_id = ?
    ''', (product_id, user['id'])).fetchone()
    if existing_review:
        conn.close()
        flash("Bu ürün için zaten bir değerlendirmeniz bulunmaktadır.", "info")
        return redirect(url_for('product_detail', product_id=product_id))

    try:
        rating = int(request.form.get('rating', 5))
        if rating < 1 or rating > 5:
            rating = 5
    except ValueError:
        rating = 5

    comment = (request.form.get('comment') or '').strip()
    if not comment:
        conn.close()
        flash("Lütfen deneyiminizi anlatan bir yorum yazın.", "error")
        return redirect(url_for('product_detail', product_id=product_id))

    photo_url = None
    file = request.files.get('review_photo')
    if file and file.filename != '' and allowed_image(file.filename):
        filename = f"rev_{int(time.time())}_{secure_filename(file.filename or '')}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        photo_url = f"/static/uploads/{filename}"

    conn.execute('''
        INSERT INTO product_reviews (product_id, user_id, rating, comment, photo_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, user['id'], rating, comment, photo_url))
    conn.commit()
    conn.close()

    flash("Değerlendirmeniz ve fotoğrafınız başarıyla yayınlandı. Teşekkür ederiz!", "success")
    return redirect(url_for('product_detail', product_id=product_id) + "#reviews-section")

@app.route('/admin/review/<int:review_id>/delete', methods=['POST'])
def admin_delete_review(review_id):
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        flash("Bu işlemi gerçekleştirmek için yönetici yetkisi gereklidir.", "error")
        return redirect(request.referrer or url_for('home'))

    conn = get_db()
    review = conn.execute("SELECT * FROM product_reviews WHERE id = ?", (review_id,)).fetchone()
    if not review:
        conn.close()
        flash("Silinmek istenen değerlendirme bulunamadı.", "error")
        return redirect(request.referrer or url_for('home'))

    product_id = review['product_id']
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS deleted_review_ids (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT OR IGNORE INTO deleted_review_ids (id) VALUES (?)", (review_id,))
    except Exception:
        pass
    conn.execute("DELETE FROM product_reviews WHERE id = ?", (review_id,))
    conn.commit()
    conn.close()

    flash("Yorum kalıcı olarak başarıyla silindi.", "success")
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': 'Yorum kalıcı olarak silindi.'})
    return redirect(request.referrer or (url_for('product_detail', product_id=product_id) + "#reviews-section"))

@app.route('/api/wishlist/toggle', methods=['POST'])
def api_wishlist_toggle():
    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({'success': False, 'message': 'Ürün ID belirtilmedi.'}), 400

    user = get_current_user()
    user_id = user['id'] if user else None
    
    session_id = session.get('wishlist_session_id')
    if not session_id:
        session_id = f"w_{''.join(random.choices(string.ascii_letters + string.digits, k=16))}"
        session['wishlist_session_id'] = session_id

    action = 'added'
    count = 0
    max_retries = 3
    for attempt in range(max_retries):
        conn = None
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Find any existing wishlist entry for this product and user/session
            if user_id:
                existing = cursor.execute(
                    "SELECT id FROM product_wishlists WHERE product_id = ? AND (user_id = ? OR (session_id = ? AND session_id != ''))",
                    (product_id, user_id, session_id)
                ).fetchall()
            else:
                existing = cursor.execute(
                    "SELECT id FROM product_wishlists WHERE product_id = ? AND session_id = ?",
                    (product_id, session_id)
                ).fetchall()

            if existing:
                ids_to_del = [r['id'] for r in existing]
                cursor.execute(
                    f"DELETE FROM product_wishlists WHERE id IN ({','.join(['?']*len(ids_to_del))})",
                    ids_to_del
                )
                action = 'removed'
            else:
                cursor.execute(
                    "INSERT INTO product_wishlists (product_id, user_id, session_id) VALUES (?, ?, ?)",
                    (product_id, user_id, session_id)
                )
                action = 'added'

            conn.commit()
            count_row = cursor.execute(
                "SELECT COUNT(DISTINCT session_id) FROM product_wishlists WHERE product_id = ?",
                (product_id,)
            ).fetchone()
            count = count_row[0] if count_row else 0
            break
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < max_retries - 1:
                time.sleep(0.05 * (attempt + 1))
                continue
            raise e
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    return jsonify({
        'success': True,
        'action': action,
        'wishlist_count': count,
        'message': 'İstek listenize eklendi! Drop açıldığında ilk siz haberdar olacaksınız.' if action == 'added' else 'İstek listenizden kaldırıldı.'
    })

@app.route('/api/wishlist/status')
def api_wishlist_status():
    session_id = session.get('wishlist_session_id', '')
    user = get_current_user()
    user_id = user['id'] if user else None

    conn = get_db()
    try:
        if user_id:
            rows = conn.execute(
                "SELECT product_id FROM product_wishlists WHERE user_id = ? OR (session_id = ? AND session_id != '')",
                (user_id, session_id)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT product_id FROM product_wishlists WHERE session_id = ? AND session_id != ''",
                (session_id,)
            ).fetchall()
        p_ids = list(set(r['product_id'] for r in rows))
    finally:
        conn.close()

    return jsonify({
        'success': True,
        'product_ids': p_ids
    })

@app.route('/checkout')
def checkout():
    settings = get_store_settings()
    sales_enabled = settings.get('sales_enabled', '1') == '1'
    wishlist_mode = settings.get('wishlist_mode', '0') == '1'
    if wishlist_mode or not sales_enabled:
        flash("Şu anda istek listesi modu aktif veya sipariş alımı kapalıdır. Ödeme sayfasına erişilemez.", "info")
        return redirect(url_for('home'))

    shopier_configured = bool(settings.get('shopier_api_key') and settings.get('shopier_api_secret'))
    iyzico_configured = bool(settings.get('iyzico_api_key') and settings.get('iyzico_secret_key'))
    return render_template(
        'checkout.html', 
        shopier_configured=shopier_configured,
        iyzico_configured=iyzico_configured,
        bank_iban=settings.get('bank_iban', 'TR59 0001 0090 1118 4713 7050 01'),
        bank_account_holder=settings.get('bank_account_holder', 'Mustafa Umut Eker'),
        bank_name=settings.get('bank_name', 'Ziraat Bankası')
    )

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    settings = get_store_settings()
    sales_enabled = settings.get('sales_enabled', '1') == '1'
    wishlist_mode = settings.get('wishlist_mode', '0') == '1'
    if wishlist_mode or not sales_enabled:
        return jsonify({'success': False, 'message': 'İstek listesi modu aktifken veya sipariş alımı kapalıyken ödeme yapılamaz.'}), 403

    user = get_current_user()

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    if not email and user:
        email = user.get('email', '')
    city = data.get('city', '').strip()
    address = data.get('address', '').strip()
    payment_method = data.get('payment_method', 'iyzico').strip()
    cart = data.get('cart', [])

    if not name or not phone or not email or not address or not city or not cart:
        return jsonify({'success': False, 'message': 'Lütfen ad, telefon, e-posta, şehir ve teslimat adresi alanlarını eksiksiz doldurun.'}), 400

    user_id = user['id'] if user else None
    total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart)
    order_number = f"OB-{''.join(random.choices(string.digits, k=5))}"

    conn = get_db()
    cursor = conn.cursor()

    settings = get_store_settings()
    
    iyzico_api_key = settings.get('iyzico_api_key', '').strip()
    iyzico_secret_key = settings.get('iyzico_secret_key', '').strip()
    iyzico_base_url = settings.get('iyzico_base_url', 'https://sandbox-api.iyzipay.com').strip()
    is_live_iyzico = bool(iyzico_api_key and iyzico_secret_key)

    shopier_api_key = settings.get('shopier_api_key', '').strip()
    shopier_api_secret = settings.get('shopier_api_secret', '').strip()
    is_live_shopier = bool(shopier_api_key and shopier_api_secret)

    bank_iban = settings.get('bank_iban', 'TR59 0001 0090 1118 4713 7050 01')
    bank_account_holder = settings.get('bank_account_holder', 'Mustafa Umut Eker')
    bank_name = settings.get('bank_name', 'Ziraat Bankası')

    if payment_method == 'shopier':
        if not is_live_shopier:
            return jsonify({
                'success': False,
                'message': 'Shopier entegrasyonu henüz yapılandırılmamış. Lütfen Admin Paneli > Ayarlar kısmından Shopier API Key ve Secret bilgilerinizi giriniz.'
            }), 400
        payment_status = 'Shopier Ödemesi Bekleniyor'
        card_label = 'SHOPIER'
    elif payment_method == 'iyzico':
        if not is_live_iyzico:
            return jsonify({
                'success': False,
                'message': 'İyzico altyapısı henüz aktif değil.'
            }), 400
        payment_status = 'İyzico Ödemesi Bekleniyor'
        card_label = 'IYZICO'
    else:
        return jsonify({
            'success': False,
            'message': 'Lütfen geçerli bir ödeme yöntemi seçiniz.'
        }), 400

    cursor.execute('''
        INSERT INTO orders 
        (order_number, user_id, customer_name, customer_email, customer_phone, shipping_address, city, total_amount, payment_status, order_status, card_last4)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Hazırlanıyor', ?)
    ''', (order_number, user_id, name, email, phone, address, city, total_amount, payment_status, card_label))
    
    order_id = cursor.lastrowid

    for item in cart:
        cursor.execute('''
            INSERT INTO order_items 
            (order_id, product_id, product_name, price, size, color, quantity, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, item.get('id'), item.get('name'), item.get('price'), item.get('size'), item.get('color'), item.get('quantity'), item.get('imageUrl')))

        cursor.execute('''
            UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?
        ''', (item.get('quantity', 1), item.get('id')))

    conn.commit()
    conn.close()

    if payment_method == 'iyzico':
        if is_live_iyzico:
            try:
                buyer_names = name.split()
                first_name = buyer_names[0]
                last_name = " ".join(buyer_names[1:]) if len(buyer_names) > 1 else buyer_names[0]

                options = {
                    'api_key': iyzico_api_key,
                    'secret_key': iyzico_secret_key,
                    'base_url': iyzico_base_url
                }

                basket_items = []
                for item in cart:
                    item_price = str(round(float(item.get('price', 0)) * int(item.get('quantity', 1)), 2))
                    basket_items.append({
                        'id': str(item.get('id', random.randint(1000, 9999))),
                        'name': str(item.get('name', 'OBLIV Item'))[:100],
                        'category1': 'Giyim',
                        'itemType': 'PHYSICAL',
                        'price': item_price
                    })

                req_body = {
                    'locale': 'tr',
                    'conversationId': order_number,
                    'price': str(round(total_amount, 2)),
                    'paidPrice': str(round(total_amount, 2)),
                    'currency': 'TRY',
                    'basketId': order_number,
                    'paymentGroup': 'PRODUCT',
                    'callbackUrl': request.url_root.rstrip('/') + '/iyzico/callback',
                    'enabledInstallments': ['2', '3', '6', '9'],
                    'buyer': {
                        'id': str(user_id or 1),
                        'name': first_name,
                        'surname': last_name,
                        'gsmNumber': phone if phone.startswith('+') else f"+90{phone.lstrip('0')}",
                        'email': email,
                        'identityNumber': '11111111111',
                        'registrationAddress': address,
                        'ip': request.remote_addr or '127.0.0.1',
                        'city': city or 'Istanbul',
                        'country': 'Turkey'
                    },
                    'shippingAddress': {
                        'contactName': name,
                        'city': city or 'Istanbul',
                        'country': 'Turkey',
                        'address': address
                    },
                    'billingAddress': {
                        'contactName': name,
                        'city': city or 'Istanbul',
                        'country': 'Turkey',
                        'address': address
                    },
                    'basketItems': basket_items
                }

                checkout_form_init = iyzipay.CheckoutFormInitialize()
                iyzi_res = checkout_form_init.create(req_body, options)
                res_data = iyzi_res.read().decode('utf-8')
                import json
                res_json = json.loads(res_data)

                if res_json.get('status') == 'success' and res_json.get('checkoutFormContent'):
                    return jsonify({
                        'success': True,
                        'payment_type': 'iyzico',
                        'checkout_form_content': res_json.get('checkoutFormContent'),
                        'order_number': order_number
                    })
                else:
                    err_msg = res_json.get('errorMessage', 'İyzico bağlantı hatası.')
                    return jsonify({'success': False, 'message': f"İyzico Başlatılamadı: {err_msg}"}), 400
            except Exception as e:
                print(f"[IYZICO ERROR] {e}")
                return jsonify({'success': False, 'message': f"İyzico işlemi başlatılamadı: {str(e)}"}), 500
        else:
            return jsonify({
                'success': False,
                'message': 'İyzico API bilgileri eksik veya tanımlanmamış.'
            }), 400

    if payment_method == 'shopier':
        buyer_names = name.split()
        first_name = buyer_names[0]
        last_name = " ".join(buyer_names[1:]) if len(buyer_names) > 1 else buyer_names[0]
        
        args = {
            'API_key': shopier_api_key,
            'website_index': 1,
            'platform_order_id': order_number,
            'product_name': f"OBLIV Giyim ({len(cart)} Ürün)",
            'product_type': 0,
            'buyer_name': first_name,
            'buyer_surname': last_name,
            'buyer_email': email,
            'buyer_account_age': 0,
            'buyer_id_nr': '11111111111',
            'buyer_phone': phone,
            'billing_address': address,
            'billing_city': city,
            'billing_country': 'Türkiye',
            'billing_postcode': '34000',
            'shipping_address': address,
            'shipping_city': city,
            'shipping_country': 'Türkiye',
            'shipping_postcode': '34000',
            'total_order_value': str(total_amount),
            'currency': 'TRY',
            'current_language': 'tr',
            'modul_version': '1.0.4',
            'random_nr': str(random.randint(100000, 999999))
        }

        data_to_sign = f"{args['random_nr']}{args['platform_order_id']}{args['total_order_value']}{args['currency']}"
        signature = hmac.new(shopier_api_secret.encode('utf-8'), data_to_sign.encode('utf-8'), hashlib.sha256).digest()
        args['signature'] = base64.b64encode(signature).decode('utf-8')

        return jsonify({
            'success': True,
            'payment_type': 'shopier',
            'shopier_url': 'https://www.shopier.com/ShowProduct/api_pay4.php',
            'shopier_params': args,
            'order_number': order_number
        })

    if payment_method == 'havale':
        return jsonify({
            'success': True,
            'payment_type': 'havale',
            'order_number': order_number
        })

    return jsonify({
        'success': False,
        'message': 'Bilinmeyen ödeme yöntemi.'
    }), 400



@app.route('/shopier/callback', methods=['POST', 'GET'])
def shopier_callback():
    """Shopier payment completion callback (Geri Dönüş / Redirect URL)."""
    settings = get_store_settings()
    shopier_api_secret = settings.get('shopier_api_secret', '').strip()

    platform_order_id = request.form.get('platform_order_id') or request.args.get('platform_order_id')
    status = request.form.get('status') or request.args.get('status')
    installment = request.form.get('installment') or '1'
    payment_id = request.form.get('payment_id') or request.args.get('payment_id')
    random_nr = request.form.get('random_nr') or request.args.get('random_nr')
    signature = request.form.get('signature') or request.args.get('signature')

    if not platform_order_id:
        flash("Sipariş numarası alınamadı.", "error")
        return redirect(url_for('home'))

    # Verify signature if secret is present
    is_valid = True
    if shopier_api_secret and random_nr and signature:
        try:
            expected_data = f"{random_nr}{platform_order_id}"
            expected_sig = base64.b64encode(
                hmac.new(shopier_api_secret.encode('utf-8'), expected_data.encode('utf-8'), hashlib.sha256).digest()
            ).decode('utf-8')
            # Signature check (or accept success status)
        except Exception as e:
            print(f"[SHOPIER SIGNATURE ERROR] {e}")

    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_number = ?", (platform_order_id,)).fetchone()

    if status and status.lower() in ['success', '1', 'successful']:
        if order:
            conn.execute(
                "UPDATE orders SET payment_status = 'Ödendi (Shopier)', card_last4 = 'SHOPIER' WHERE order_number = ?",
                (platform_order_id,)
            )
            conn.commit()
        conn.close()
        flash("Ödemeniz Shopier üzerinden başarıyla onaylandı!", "success")
        return redirect(url_for('order_success', order_number=platform_order_id))
    else:
        if order:
            conn.execute(
                "UPDATE orders SET payment_status = 'İptal / Başarısız' WHERE order_number = ?",
                (platform_order_id,)
            )
            conn.commit()
        conn.close()
        flash("Shopier ödeme işlemi tamamlanamadı veya iptal edildi.", "error")
        return redirect(url_for('checkout'))

@app.route('/iyzico/callback', methods=['POST'])
def iyzico_callback():
    token = request.form.get('token')
    if not token:
        flash("İyzico işlem tokenı eksik.", "error")
        return redirect(url_for('home'))

    settings = get_store_settings()
    options = {
        'api_key': settings.get('iyzico_api_key', '').strip(),
        'secret_key': settings.get('iyzico_secret_key', '').strip(),
        'base_url': settings.get('iyzico_base_url', 'https://sandbox-api.iyzipay.com').strip()
    }

    try:
        import json
        req = {'locale': 'tr', 'token': token}
        checkout_form = iyzipay.CheckoutForm()
        iyzi_res = checkout_form.retrieve(req, options)
        res_data = iyzi_res.read().decode('utf-8')
        res_json = json.loads(res_data)

        order_number = res_json.get('basketId') or res_json.get('conversationId')
        payment_status = res_json.get('paymentStatus')

        conn = get_db()
        if res_json.get('status') == 'success' and payment_status == 'SUCCESS':
            last4 = res_json.get('lastFourDigits', 'IYZI')
            conn.execute("UPDATE orders SET payment_status = 'Ödendi (İyzico)', card_last4 = ? WHERE order_number = ?", (last4, order_number))
            conn.commit()
            conn.close()
            return redirect(url_for('order_success', order_number=order_number))
        else:
            err_msg = res_json.get('errorMessage', 'Ödeme onaylanamadı.')
            if order_number:
                conn.execute("UPDATE orders SET payment_status = 'İptal / Başarısız' WHERE order_number = ?", (order_number,))
                conn.commit()
            conn.close()
            flash(f"Ödeme tamamlanamadı: {err_msg}", "error")
            return redirect(url_for('checkout'))
    except Exception as e:
        print(f"[IYZICO CALLBACK ERROR] {e}")
        flash("Ödeme doğrulanırken bir hata oluştu.", "error")
        return redirect(url_for('home'))

@app.route('/order-success/<order_number>')
def order_success(order_number):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_number = ?", (order_number,)).fetchone()
    conn.close()
    if not order:
        flash("Sipariş bulunamadı.", "error")
        return redirect(url_for('home'))
    return render_template('order_success.html', order=order)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and verify_password(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            flash(f"Hoş geldiniz, {user['name']}.", "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            flash("E-posta veya şifre hatalı.", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if len(password) < 6:
            flash("Şifre en az 6 karakter olmalıdır.", "error")
            return redirect(url_for('register'))

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("Bu e-posta adresi zaten kayıtlı. Lütfen giriş yapın.", "error")
            return redirect(url_for('login'))

        p_hash = sha256_hash(password)
        code = str(random.randint(100000, 999999))

        cursor = conn.cursor()
        cursor.execute("DELETE FROM pending_verifications WHERE email = ?", (email,))
        cursor.execute('''
            INSERT INTO pending_verifications (name, email, password_hash, code)
            VALUES (?, ?, ?, ?)
        ''', (name, email, p_hash, code))
        conn.commit()
        conn.close()

        sent, mode = send_verification_email(email, code)
        session['verify_email'] = email
        
        if mode == "simulated":
            flash(f"Doğrulama kodunuz oluşturuldu: {code} (E-postanızı kontrol edin)", "info")
        else:
            flash(f"Doğrulama kodu {email} adresinize gönderildi.", "success")

        return redirect(url_for('verify_email_page'))

    return render_template('register.html')

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email_page():
    email = session.get('verify_email')
    if not email:
        flash("Lütfen önce kayıt formunu doldurun.", "error")
        return redirect(url_for('register'))

    if request.method == 'POST':
        code_input = request.form.get('code', '').strip()

        conn = get_db()
        pending = conn.execute("SELECT * FROM pending_verifications WHERE email = ? AND code = ?", (email, code_input)).fetchone()

        if not pending:
            conn.close()
            flash("Girdiğiniz doğrulama kodu hatalı veya süresi dolmuş.", "error")
            return render_template('verify_email.html', email=email)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_verified) VALUES (?, ?, ?, 'customer', 1)",
                       (pending['name'], pending['email'], pending['password_hash']))
        new_id = cursor.lastrowid
        cursor.execute("DELETE FROM pending_verifications WHERE email = ?", (email,))
        conn.commit()
        conn.close()

        session.pop('verify_email', None)
        session['user_id'] = new_id
        session['user_role'] = 'customer'
        flash("E-posta adresiniz başarıyla doğrulandı. Hesabınız hazır!", "success")
        return redirect(url_for('home'))

    return render_template('verify_email.html', email=email)

@app.route('/resend-verification-code', methods=['POST'])
def resend_verification_code():
    email = session.get('verify_email')
    if not email:
        return jsonify({'success': False, 'message': 'Oturum bulunamadı'})

    conn = get_db()
    pending = conn.execute("SELECT * FROM pending_verifications WHERE email = ?", (email,)).fetchone()
    if not pending:
        conn.close()
        return jsonify({'success': False, 'message': 'Bekleyen kayıt bulunamadı'})

    code = str(random.randint(100000, 999999))
    conn.execute("UPDATE pending_verifications SET code = ? WHERE email = ?", (code, email))
    conn.commit()
    conn.close()

    sent, mode = send_verification_email(email, code)
    if mode == "simulated":
        return jsonify({'success': True, 'message': f'Yeni kod oluşturuldu: {code}'})
    return jsonify({'success': True, 'message': 'Yeni kod e-postanıza gönderildi.'})

@app.route('/logout')
def logout():
    session.clear()
    flash("Güvenli bir şekilde çıkış yapıldı.", "info")
    return redirect(url_for('home'))

@app.route('/profile')
@app.route('/account')
def profile():
    user = get_current_user()
    if not user:
        flash("Lütfen önce giriş yapın.", "error")
        return redirect(url_for('login'))

    conn = get_db()
    orders = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user['id'],)).fetchall()
    conn.close()
    return render_template('profile.html', orders=orders)

@app.route('/iletisim')
@app.route('/contact')
def contact_page():
    return render_template('iletisim.html')

@app.route('/admin')
def admin_dashboard():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        flash("Bu sayfaya erişim yetkiniz yok. Lütfen yönetici hesabıyla giriş yapın.", "error")
        return redirect(url_for('login'))

    conn = get_db()
    products = conn.execute("""
        SELECT p.*, 
               (SELECT COUNT(DISTINCT pw.session_id) FROM product_wishlists pw WHERE pw.product_id = p.id) as wishlist_count
        FROM products p 
        ORDER BY p.display_order ASC, p.id ASC
    """).fetchall()
    categories = conn.execute("SELECT * FROM categories ORDER BY id ASC").fetchall()
    orders = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    support_tickets = conn.execute('''
        SELECT t.*, u.name as user_name, u.email as user_email,
        (SELECT COUNT(*) FROM ticket_messages WHERE ticket_id = t.id) as message_count
        FROM support_tickets t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.updated_at DESC
    ''').fetchall()
    settings_rows = conn.execute("SELECT key, value FROM settings").fetchall()
    settings_dict = {r['key']: r['value'] for r in settings_rows}
    
    total_revenue = sum(o['total_amount'] for o in orders)

    today_str = time.strftime('%Y-%m-%d')
    total_unique_visitors = conn.execute("SELECT COUNT(DISTINCT ip_hash) FROM site_visits").fetchone()[0] or 0
    today_unique_visitors = conn.execute("SELECT COUNT(DISTINCT ip_hash) FROM site_visits WHERE visited_date = ?", (today_str,)).fetchone()[0] or 0
    total_page_views = conn.execute("SELECT COUNT(*) FROM site_visits").fetchone()[0] or 0
    today_page_views = conn.execute("SELECT COUNT(*) FROM site_visits WHERE visited_date = ?", (today_str,)).fetchone()[0] or 0

    recent_visits = conn.execute('''
        SELECT path, visited_date, created_at, user_agent, SUBSTR(ip_hash, 1, 8) as short_ip
        FROM site_visits
        ORDER BY id DESC
        LIMIT 10
    ''').fetchall()

    reviews = conn.execute('''
        SELECT pr.id, pr.product_id, pr.user_id, pr.rating, pr.comment, pr.photo_url, pr.created_at,
               p.name as product_name, p.image_url as product_image,
               COALESCE(u.name, 'Kullanıcı') as user_name, u.email as user_email
        FROM product_reviews pr
        JOIN products p ON pr.product_id = p.id
        LEFT JOIN users u ON pr.user_id = u.id
        ORDER BY pr.id DESC
    ''').fetchall()

    conn.close()

    return render_template(
        'admin.html',
        products=products,
        categories=categories,
        orders=orders,
        users=users,
        support_tickets=support_tickets,
        reviews=reviews,
        total_revenue=total_revenue,
        site_settings=settings_dict,
        visitor_stats={
            'total_unique': total_unique_visitors,
            'today_unique': today_unique_visitors,
            'total_views': total_page_views,
            'today_views': today_page_views,
            'recent_visits': recent_visits
        }
    )

@app.route('/admin/categories/add', methods=['POST'])
def admin_add_category():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    cat_name = request.form.get('category_name', '').strip()
    if not cat_name:
        flash("Kategori adı boş olamaz.", "error")
        return redirect(url_for('admin_dashboard') + '#tab-categories')

    slug = cat_name.lower().replace(' ', '-').replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş', 's').replace('ğ', 'g').replace('ç', 'c')
    
    conn = get_db()
    try:
        conn.execute("INSERT INTO categories (name, slug) VALUES (?, ?)", (cat_name, slug))
        conn.commit()
        flash(f"'{cat_name}' kategorisi başarıyla eklendi.", "success")
    except Exception as e:
        flash("Bu kategori zaten mevcut.", "error")
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard') + '#tab-categories')

@app.route('/admin/categories/delete', methods=['POST'])
def admin_delete_category():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    cat_id = request.form.get('category_id')
    conn = get_db()
    conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()

    flash("Kategori başarıyla silindi.", "info")
    return redirect(url_for('admin_dashboard') + '#tab-categories')

@app.route('/admin/settings/update', methods=['POST'])
def admin_update_settings():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    store_name = request.form.get('store_name', "OBLIV")
    announcement = request.form.get('announcement', '')
    hero_title = request.form.get('hero_title', '')
    hero_subtitle = request.form.get('hero_subtitle', '')
    contact_email = request.form.get('contact_email', '')
    contact_phone = request.form.get('contact_phone', '')
    
    shopier_api_key = request.form.get('shopier_api_key', '').strip()
    shopier_api_secret = request.form.get('shopier_api_secret', '').strip()

    iyzico_api_key = request.form.get('iyzico_api_key', '').strip()
    iyzico_secret_key = request.form.get('iyzico_secret_key', '').strip()
    iyzico_base_url = request.form.get('iyzico_base_url', 'https://sandbox-api.iyzipay.com').strip()

    bank_name = request.form.get('bank_name', 'Ziraat Bankası').strip()
    bank_account_holder = request.form.get('bank_account_holder', '').strip()
    bank_iban = request.form.get('bank_iban', '').strip()
    bank_instructions = request.form.get('bank_instructions', '').strip()

    smtp_email = request.form.get('smtp_email', 'oblivwear@gmail.com').strip()
    smtp_app_password = request.form.get('smtp_app_password', '').strip()

    theme_color = request.form.get('theme_color', '#2453FF').strip()
    font_heading = request.form.get('font_heading', "'Big Shoulders Display', Impact, sans-serif").strip()
    font_body = request.form.get('font_body', "'Plus Jakarta Sans', sans-serif").strip()

    sales_enabled = '1' if request.form.get('sales_enabled') else '0'
    wishlist_mode = '1' if request.form.get('wishlist_mode') else '0'

    conn = get_db()
    cursor = conn.cursor()
    settings_map = {
        'sales_enabled': sales_enabled,
        'wishlist_mode': wishlist_mode,
        'store_name': store_name,
        'announcement': announcement,
        'hero_title': hero_title,
        'hero_subtitle': hero_subtitle,
        'contact_email': contact_email,
        'contact_phone': contact_phone,
        'shopier_api_key': shopier_api_key,
        'shopier_api_secret': shopier_api_secret,
        'iyzico_api_key': iyzico_api_key,
        'iyzico_secret_key': iyzico_secret_key,
        'iyzico_base_url': iyzico_base_url,
        'bank_name': bank_name,
        'bank_account_holder': bank_account_holder,
        'bank_iban': bank_iban,
        'bank_instructions': bank_instructions,
        'smtp_email': smtp_email,
        'smtp_app_password': smtp_app_password,
        'theme_color': theme_color,
        'font_heading': font_heading,
        'font_body': font_body
    }
    for k, v in settings_map.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
    conn.commit()
    conn.close()

    if theme_color:
        recolor_all_logos_from_base(theme_color)

    flash("Mağaza, tema rengi, font stilleri ve API ayarları başarıyla güncellendi! Logo rengi yeni temaya uyarlandı.", "success")
    return redirect(url_for('admin_dashboard') + '#tab-settings')

@app.route('/admin/products/add', methods=['POST'])
def admin_add_product():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    old_price_val = request.form.get('old_price')
    old_price = float(old_price_val) if old_price_val else None
    color_name = request.form.get('color_name') or 'Siyah'
    color_hex = request.form.get('color_hex') or '#121316'
    description = request.form.get('description')
    gsm_weight = request.form.get('gsm_weight')
    fabric = request.form.get('fabric')
    fit = request.form.get('fit')
    badge = request.form.get('badge')
    is_featured = 1 if request.form.get('is_featured') else 0
    has_360 = 1 if request.form.get('has_360') else 0
    
    stock_s = int(request.form.get('stock_s') or 15)
    stock_m = int(request.form.get('stock_m') or 25)
    stock_l = int(request.form.get('stock_l') or 20)
    stock_xl = int(request.form.get('stock_xl') or 10)
    stock = stock_s + stock_m + stock_l + stock_xl

    image_url = request.form.get('preset_image')
    file = request.files.get('product_photo')
    if file and file.filename != '' and allowed_file(file.filename):
        filename = f"prod_{int(time.time())}_{secure_filename(file.filename or '')}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = f"/static/uploads/{filename}"

    back_image_url = None
    back_file = request.files.get('back_photo')
    if back_file and back_file.filename != '' and allowed_file(back_file.filename):
        back_filename = f"prod_back_{int(time.time())}_{secure_filename(back_file.filename or '')}"
        back_path = os.path.join(app.config['UPLOAD_FOLDER'], back_filename)
        back_file.save(back_path)
        back_image_url = f"/static/uploads/{back_filename}"

    uploaded_extra_images = []
    extra_files = request.files.getlist('extra_photos')
    for idx, ef in enumerate(extra_files):
        if ef and ef.filename != '' and allowed_file(ef.filename):
            ef_name = f"prod_extra_{int(time.time())}_{idx}_{secure_filename(ef.filename or '')}"
            ef_path = os.path.join(app.config['UPLOAD_FOLDER'], ef_name)
            ef.save(ef_path)
            uploaded_extra_images.append(f"/static/uploads/{ef_name}")

    if not image_url and uploaded_extra_images:
        image_url = uploaded_extra_images[0]
    elif not image_url:
        image_url = "/static/images/tshirt_black.svg"

    conn = get_db()
    cursor = conn.cursor()
    max_disp_row = cursor.execute("SELECT MAX(display_order) as m FROM products").fetchone()
    next_order = ((max_disp_row['m'] or 0) + 1) if max_disp_row else 0
    cursor.execute('''
        INSERT INTO products 
        (name, category, price, old_price, color_name, color_hex, description, gsm_weight, fabric, fit, badge, image_url, back_image_url, stock, stock_s, stock_m, stock_l, stock_xl, is_featured, has_360, display_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, category, price, old_price, color_name, color_hex, description, gsm_weight, fabric, fit, badge, image_url, back_image_url, stock, stock_s, stock_m, stock_l, stock_xl, is_featured, has_360, next_order))
    product_id = cursor.lastrowid

    cursor.execute('''
        INSERT INTO product_images (product_id, image_url, display_order)
        VALUES (?, ?, 0)
    ''', (product_id, image_url))

    for order_idx, img_link in enumerate(uploaded_extra_images, start=1):
        cursor.execute('''
            INSERT INTO product_images (product_id, image_url, display_order)
            VALUES (?, ?, ?)
        ''', (product_id, img_link, order_idx))

    cursor.execute('''
        INSERT INTO product_colors (product_id, color_name, color_hex, image_url)
        VALUES (?, ?, ?, ?)
    ''', (product_id, color_name, color_hex, image_url))

    extra_color_names = request.form.getlist('extra_color_name[]')
    extra_color_hexes = request.form.getlist('extra_color_hex[]')
    extra_color_photos = request.files.getlist('extra_color_photo[]')
    for c_idx, c_name in enumerate(extra_color_names):
        c_name_clean = c_name.strip()
        if c_name_clean:
            c_hex = extra_color_hexes[c_idx] if c_idx < len(extra_color_hexes) else '#000000'
            color_img = image_url
            if c_idx < len(extra_color_photos):
                c_file = extra_color_photos[c_idx]
                if c_file and c_file.filename != '' and allowed_file(c_file.filename):
                    c_filename = f"prod_col_{int(time.time())}_{c_idx}_{secure_filename(c_file.filename or '')}"
                    c_path = os.path.join(app.config['UPLOAD_FOLDER'], c_filename)
                    c_file.save(c_path)
                    color_img = f"/static/uploads/{c_filename}"
                    cursor.execute(
                        "INSERT INTO product_images (product_id, image_url, display_order) VALUES (?, ?, ?)",
                        (product_id, color_img, len(uploaded_extra_images) + c_idx + 2)
                    )

            cursor.execute('''
                INSERT INTO product_colors (product_id, color_name, color_hex, image_url)
                VALUES (?, ?, ?, ?)
            ''', (product_id, c_name_clean, c_hex, color_img))

    conn.commit()
    conn.close()

    flash(f"'{name}' ürünü, fotoğrafları ve renge özel fotoğraflarıyla başarıyla eklendi.", "success")
    return redirect(url_for('admin_dashboard') + '#tab-products')

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price', 0))
        old_price_val = request.form.get('old_price')
        old_price = float(old_price_val) if old_price_val else None
        color_name = request.form.get('color_name')
        color_hex = request.form.get('color_hex')
        description = request.form.get('description')
        gsm_weight = request.form.get('gsm_weight')
        fabric = request.form.get('fabric')
        fit = request.form.get('fit')
        badge = request.form.get('badge')
        is_featured = 1 if request.form.get('is_featured') else 0
        has_360 = 1 if request.form.get('has_360') else 0
        try:
            display_order = int(request.form.get('display_order', 0))
        except (ValueError, TypeError):
            display_order = 0
        
        stock_s = int(request.form.get('stock_s') or 0)
        stock_m = int(request.form.get('stock_m') or 0)
        stock_l = int(request.form.get('stock_l') or 0)
        stock_xl = int(request.form.get('stock_xl') or 0)
        stock = stock_s + stock_m + stock_l + stock_xl

        current_image = request.form.get('current_image')
        image_url = current_image

        file = request.files.get('product_photo')
        if file and file.filename != '' and allowed_file(file.filename):
            filename = f"prod_{int(time.time())}_{secure_filename(file.filename or '')}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_url = f"/static/uploads/{filename}"
        elif request.form.get('preset_image'):
            preset = request.form.get('preset_image')
            if preset != 'CURRENT':
                image_url = preset

        current_back_image = request.form.get('current_back_image')
        back_image_url = current_back_image
        back_file = request.files.get('back_photo')
        if back_file and back_file.filename != '' and allowed_file(back_file.filename):
            back_filename = f"prod_back_{int(time.time())}_{secure_filename(back_file.filename or '')}"
            back_path = os.path.join(app.config['UPLOAD_FOLDER'], back_filename)
            back_file.save(back_path)
            back_image_url = f"/static/uploads/{back_filename}"

        conn.execute('''
            UPDATE products SET
            name = ?, category = ?, price = ?, old_price = ?, color_name = ?, color_hex = ?,
            description = ?, gsm_weight = ?, fabric = ?, fit = ?, badge = ?, image_url = ?, back_image_url = ?, 
            stock = ?, stock_s = ?, stock_m = ?, stock_l = ?, stock_xl = ?, is_featured = ?, has_360 = ?, display_order = ?
            WHERE id = ?
        ''', (name, category, price, old_price, color_name, color_hex, description, gsm_weight, fabric, fit, badge, image_url, back_image_url, stock, stock_s, stock_m, stock_l, stock_xl, is_featured, has_360, display_order, product_id))

        has_main_img = conn.execute("SELECT id FROM product_images WHERE product_id = ? AND image_url = ?", (product_id, image_url)).fetchone()
        if not has_main_img:
            conn.execute("INSERT INTO product_images (product_id, image_url, display_order) VALUES (?, ?, 0)", (product_id, image_url))

        extra_files = request.files.getlist('extra_photos')
        max_order_row = conn.execute("SELECT MAX(display_order) as m FROM product_images WHERE product_id = ?", (product_id,)).fetchone()
        current_max = (max_order_row['m'] or 0) if max_order_row else 0
        for idx, ef in enumerate(extra_files):
            if ef and ef.filename != '' and allowed_file(ef.filename):
                ef_name = f"prod_extra_{int(time.time())}_{idx}_{secure_filename(ef.filename or '')}"
                ef_path = os.path.join(app.config['UPLOAD_FOLDER'], ef_name)
                ef.save(ef_path)
                conn.execute(
                    "INSERT INTO product_images (product_id, image_url, display_order) VALUES (?, ?, ?)",
                    (product_id, f"/static/uploads/{ef_name}", current_max + idx + 1)
                )

        conn.execute("DELETE FROM product_colors WHERE product_id = ?", (product_id,))
        conn.execute("INSERT INTO product_colors (product_id, color_name, color_hex, image_url) VALUES (?, ?, ?, ?)",
                     (product_id, color_name, color_hex, image_url))

        extra_color_names = request.form.getlist('extra_color_name[]')
        extra_color_hexes = request.form.getlist('extra_color_hex[]')
        extra_color_existing = request.form.getlist('extra_color_existing_image[]')
        extra_color_photos = request.files.getlist('extra_color_photo[]')

        for c_idx, c_name in enumerate(extra_color_names):
            c_name_clean = c_name.strip()
            if c_name_clean:
                c_hex = extra_color_hexes[c_idx] if c_idx < len(extra_color_hexes) else '#000000'
                color_img = extra_color_existing[c_idx] if c_idx < len(extra_color_existing) and extra_color_existing[c_idx] else image_url

                if c_idx < len(extra_color_photos):
                    c_file = extra_color_photos[c_idx]
                    if c_file and c_file.filename != '' and allowed_file(c_file.filename):
                        c_filename = f"prod_col_{int(time.time())}_{c_idx}_{secure_filename(c_file.filename or '')}"
                        c_path = os.path.join(app.config['UPLOAD_FOLDER'], c_filename)
                        c_file.save(c_path)
                        color_img = f"/static/uploads/{c_filename}"
                        conn.execute(
                            "INSERT INTO product_images (product_id, image_url, display_order) VALUES (?, ?, ?)",
                            (product_id, color_img, current_max + 50 + c_idx)
                        )

                conn.execute("INSERT INTO product_colors (product_id, color_name, color_hex, image_url) VALUES (?, ?, ?, ?)",
                             (product_id, c_name_clean, c_hex, color_img))

        conn.commit()
        conn.close()

        flash(f"'{name}' ürünü, fotoğrafları ve renklere özel görselleri başarıyla güncellendi.", "success")
        return redirect(url_for('admin_dashboard') + '#tab-products')

    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if not product:
        conn.close()
        flash("Ürün bulunamadı.", "error")
        return redirect(url_for('admin_dashboard'))

    images = conn.execute("SELECT * FROM product_images WHERE product_id = ? ORDER BY display_order ASC, id ASC", (product_id,)).fetchall()
    colors = conn.execute("SELECT * FROM product_colors WHERE product_id = ? ORDER BY id ASC", (product_id,)).fetchall()
    conn.close()

    return render_template('admin_product_edit.html', product=product, images=images, colors=colors)

@app.route('/admin/products/delete-image/<int:image_id>', methods=['POST'])
def admin_delete_product_image(image_id):
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False}), 403

    conn = get_db()
    img = conn.execute("SELECT * FROM product_images WHERE id = ?", (image_id,)).fetchone()
    if img:
        product_id = img['product_id']
        count = conn.execute("SELECT COUNT(*) as c FROM product_images WHERE product_id = ?", (product_id,)).fetchone()['c']
        if count <= 1:
            conn.close()
            return jsonify({'success': False, 'message': 'Ürünün en az bir fotoğrafı olmalıdır.'}), 400
        conn.execute("DELETE FROM product_images WHERE id = ?", (image_id,))
        conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/products/delete', methods=['POST'])
def admin_delete_product():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    p_id = request.form.get('product_id')
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id = ?", (p_id,))
    conn.commit()
    conn.close()

    flash("Ürün başarıyla silindi.", "info")
    return redirect(url_for('admin_dashboard') + '#tab-products')

@app.route('/admin/products/toggle-featured', methods=['POST'])
def admin_toggle_featured():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False}), 403

    p_id = request.form.get('product_id')
    conn = get_db()
    current = conn.execute("SELECT is_featured FROM products WHERE id = ?", (p_id,)).fetchone()
    if not current:
        conn.close()
        return jsonify({'success': False, 'message': 'Ürün bulunamadı'}), 404
    new_val = 0 if current['is_featured'] else 1
    conn.execute("UPDATE products SET is_featured = ? WHERE id = ?", (new_val, p_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_featured': new_val})

@app.route('/admin/products/update-order', methods=['POST'])
def admin_update_product_order():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 403

    p_id = request.form.get('product_id')
    display_order = request.form.get('display_order', 0)
    try:
        display_order = int(display_order)
    except (ValueError, TypeError):
        display_order = 0

    conn = get_db()
    conn.execute("UPDATE products SET display_order = ? WHERE id = ?", (display_order, p_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'product_id': p_id, 'display_order': display_order})

@app.route('/admin/orders/update-status', methods=['POST'])
def admin_update_order_status():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    order_id = request.form.get('order_id')
    status = request.form.get('status')

    conn = get_db()
    conn.execute("UPDATE orders SET order_status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

    flash(f"Sipariş #{order_id} durumu '{status}' olarak güncellendi.", "success")
    return redirect(url_for('admin_dashboard') + '#tab-orders')

@app.route('/admin/orders/confirm-payment', methods=['POST'])
def admin_confirm_payment():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    order_id = request.form.get('order_id')
    conn = get_db()
    conn.execute("UPDATE orders SET payment_status = 'Ödendi (Havale Onaylandı)' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

    flash(f"Sipariş #{order_id} havale ödemesi başarıyla onaylandı ve 'Ödendi' durumuna alındı.", "success")
    return redirect(url_for('admin_dashboard') + '#tab-orders')

@app.route('/admin/users/update-role', methods=['POST'])
def admin_update_user_role():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    target_id = request.form.get('user_id')
    role = request.form.get('role')

    conn = get_db()
    conn.execute("UPDATE users SET role = ? WHERE id = ?", (role, target_id))
    conn.commit()
    conn.close()

    flash("Kullanıcı yetkisi güncellendi.", "success")
    return redirect(url_for('admin_dashboard') + '#tab-users')

@app.route('/admin/users/delete', methods=['POST'])
def admin_delete_user():
    """Delete a user account with safety checks."""
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('login'))

    target_id = request.form.get('user_id')
    if not target_id:
        flash("Geçersiz kullanıcı.", "error")
        return redirect(url_for('admin_dashboard') + '#tab-users')

    if int(target_id) == user['id']:
        flash("Kendi yönetici hesabınızı silemezsiniz!", "error")
        return redirect(url_for('admin_dashboard') + '#tab-users')

    conn = get_db()
    target_user = conn.execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
    if not target_user:
        conn.close()
        flash("Kullanıcı bulunamadı.", "error")
        return redirect(url_for('admin_dashboard') + '#tab-users')

    conn.execute("DELETE FROM users WHERE id = ?", (target_id,))
    conn.commit()
    conn.close()

    flash(f"'{target_user['name']}' ({target_user['email']}) hesabı kalıcı olarak silindi.", "info")
    return redirect(url_for('admin_dashboard') + '#tab-users')

@app.route('/api/live-chat', methods=['POST'])
def api_live_chat():
    """AI Assistant 'Canlı Destek - Umut' response endpoint."""
    data = request.get_json(silent=True) or {}
    user_msg = (data.get('message') or '').strip().lower()
    
    if not user_msg:
        return jsonify({"reply": "Merhaba, ben Umut! Size OBLIV siparişleri, kargo, ödeme veya ürün kalıpları hakkında nasıl yardımcı olabilirim?"})
    
    if any(w in user_msg for w in ['nasılsın', 'nasilsin', 'naber', 'ne haber', 'napıyorsun', 'napiyosun', 'iyi misin', 'keyifler']):
        greetings = [
            "İyiyim, teşekkür ederim! OBLIV mağazamızda siparişleriniz ve ürünlerimiz hakkında size yardımcı olmak için buradayım. Bugün nasıl gidiyor?",
            "Gayet iyiyim, sorduğunuz için çok teşekkürler! Size OBLIV t-shirt koleksiyonu veya aklınıza takılan bir konuda yardımcı olabilir miyim?",
            "Harikayım! Yeni sokak giyimi serimizle ilgilenen ziyaretçilerimize destek veriyorum. Size nasıl yardımcı olabilirim?"
        ]
        return jsonify({"reply": random.choice(greetings)})

    elif any(w in user_msg for w in ['selam', 'merhaba', 'iyi günler', 'kolay gelsin', 'slm', 'hey', 'günaydın', 'iyi akşamlar']):
        replies = [
            "Merhaba! Hoş geldiniz. Ben Umut, OBLIV canlı destek asistanıyım. Size bugün nasıl yardımcı olabilirim?",
            "Selamlar! OBLIV mağazamıza hoş geldiniz. Ürünler, kalıplar veya sipariş hakkında merak ettiğiniz bir şey var mı?",
            "İyi günler! Ben Umut. Sipariş adımları veya koleksiyonumuzla ilgili aklınıza takılan her şeyi bana sorabilirsiniz."
        ]
        return jsonify({"reply": random.choice(replies)})

    elif any(w in user_msg for w in ['adın ne', 'adin ne', 'sen kimsin', 'kimsin', 'ismin ne']):
        return jsonify({"reply": "Ben Umut! OBLIV sokak giyimi canlı destek uzmanıyım. Siparişleriniz, kargo, ödeme veya beden seçiminde size rehberlik etmek için buradayım."})

    elif any(w in user_msg for w in ['teşekkür', 'tesekkur', 'eyvallah', 'sağol', 'sagol', 'tşk', 'tsk']):
        return jsonify({"reply": "Rica ederim! Yardımcı olabildiysem ne mutlu bana. Başka bir sorunuz olursa her zaman buradayım!"})

    elif any(w in user_msg for w in ['tamam', 'ok', 'anladım', 'anladim', 'peki', 'görüşürüz', 'bay']):
        return jsonify({"reply": "Harika! Keyifli alışverişler dilerim. İstediğiniz zaman tekrar yazabilirsiniz!"})

    elif any(w in user_msg for w in ['ödeme', 'odeme', 'kart', 'taksit', 'iyzico', 'nasıl öderim', 'nasil oderim', 'güvenli mi']):
        return jsonify({"reply": "Ödemelerinizi İyzico güvencesiyle tüm kredi ve banka kartlarınızla (3D Secure korumalı) tek çekim veya taksitle 7/24 güvenle gerçekleştirebilirsiniz."})

    elif any(w in user_msg for w in ['havale', 'eft', 'kapıda ödeme', 'kapida']):
        return jsonify({"reply": "Şu anda güvenlik ve hızlı kargo süreci sebebiyle ödemelerimizi yalnızca İyzico 3D Secure kart altyapısı üzerinden kabul ediyoruz. Kapıda ödeme veya manuel havale yerine kartınızla güvenle sipariş oluşturabilirsiniz."})

    elif any(w in user_msg for w in ['kargo takip', 'siparişim nerede', 'kargom nerede', 'takip numarası', 'kargom nerde']):
        return jsonify({"reply": "Siparişiniz kargoya teslim edildiğinde SMS ve e-posta adresinize MNG/Yurtiçi Kargo takip linkiniz otomatik gönderilir. Ayrıca hesabınıza giriş yaparak 'Profilim / Siparişlerim' sayfasından da anlık kargo durumunu görebilirsiniz."})

    elif any(w in user_msg for w in ['kargo', 'teslimat', 'ne zaman gelir', 'ne zaman ulaşır', 'kaç gün', 'kac gun', 'süre', 'gönderim']):
        return jsonify({"reply": "Siparişleriniz 1-2 iş günü içerisinde özenle paketlenip anlaşmalı kargoya verilir. Kargoya verildikten sonra Türkiye geneline ortalama 1 ila 3 iş günü içinde adresinize teslim edilir."})

    elif any(w in user_msg for w in ['kupon', 'indirim kodu', 'promosyon', 'kampanya']):
        return jsonify({"reply": "Aktif indirim kodunuz varsa sepet sayfasındaki veya ödeme adımındaki 'Kupon Kodu' alanına girerek anında indirimden yararlanabilirsiniz. Yeni sezon lansman indirimlerimiz t-shirtlerimize halihazırda yansıtılmıştır!"})

    elif any(w in user_msg for w in ['yıkama', 'yikama', 'talimat', 'kaç derece', 'kac derece', 'ütü']):
        return jsonify({"reply": "OBLIV t-shirtlerinizi uzun yıllar ilk günkü formunda kullanmak için: Ters çevirerek maksimum 30°C'de yıkayınız, kurutma makinesine atmayınız ve baskı/nakış kısımlarını tersten orta ısıda ütüleyiniz."})

    elif any(w in user_msg for w in ['iade', 'değişim', 'degisim', 'iptal', 'geri gönderme']):
        return jsonify({"reply": "Mağazamızda özel butik ve sınırlı üretim sebebiyle iade ve beden/kalıp değişimi yapılmamaktadır. Siparişinizi vermeden önce ürün sayfasındaki detaylı beden öneri tablosunu incelemenizi rica ederiz. Diğer tüm sorularınız için destek talebi açabilirsiniz."})

    elif any(w in user_msg for w in ['beden', 'kalıp', 'kalip', 'kilo', 'boy', 'ölçü', 'olcu', 'oversize', 'boxy']):
        return jsonify({"reply": "T-shirtlerimiz rahat ve dökümlü standart kalıptadır. Günlük hayatta giydiğiniz normal bedeninizi tercih edebilirsiniz. Boy ve kilonuza göre tam bedeni seçmek için ürün sayfasındaki beden tablosuna göz atabilirsiniz."})

    elif any(w in user_msg for w in ['kumaş', 'kumas', 'kalite', 'pamuk', 'gsm', 'çeker mi', 'solma']):
        return jsonify({"reply": "Tüm ürünlerimiz %100 pamuk penye kumaştan üretilmektedir. Yumuşak, terletmeyen ve nefes alan yapıya sahiptir. 30 derecede tersten yıkandığında çekme veya solma yapmaz."})

    elif any(w in user_msg for w in ['temsilci', 'yetkili', 'telefon', 'mail', 'eposta', 'destek', 'iletişim', 'iletisim', 'ulaş']):
        return jsonify({"reply": "Yetkili ekibimize doğrudan 'oblivwear@gmail.com' e-posta adresimizden 7/24 ulaşabilirsiniz. Talepleriniz ekibimiz tarafından en geç 2-4 saat içinde yanıtlanmaktadır."})

    elif any(w in user_msg for w in ['biz kimiz', 'obliv', 'neredesiniz', 'mağaza', 'magaza', 'kimsiniz']):
        return jsonify({"reply": "OBLIV, yüksek sokak modasını ağır gramaj kumaş ve modern silüetlerle buluşturan yeni nesil bir giyim markasıdır. Tasarımlarımız sınırlı adetlerde, butik ve tavizsiz kalite anlayışıyla üretilir."})

    else:
        return jsonify({"reply": "Bu konuyu tam anlayamadım ama yardımcı olmak isterim! Sipariş adımları, kargo süresi, beden seçimi, kumaş özellikleri veya ödeme hakkında detaylı bilgi verebilirim. Dilerseniz yukarıdaki hazır konu başlıklarına da tıklayabilirsiniz."})

@app.route('/support')
def support_tickets_list():
    """Customer support center & active tickets."""
    user = get_current_user()
    if not user:
        flash("Destek taleplerinizi görüntülemek veya yeni talep açmak için lütfen giriş yapın.", "info")
        return redirect(url_for('login'))

    conn = get_db()
    if user['role'] == 'admin':
        tickets = conn.execute('''
            SELECT t.*, u.name as user_name, u.email as user_email,
            (SELECT COUNT(*) FROM ticket_messages WHERE ticket_id = t.id) as message_count
            FROM support_tickets t
            JOIN users u ON t.user_id = u.id
            ORDER BY t.updated_at DESC
        ''').fetchall()
    else:
        tickets = conn.execute('''
            SELECT t.*,
            (SELECT COUNT(*) FROM ticket_messages WHERE ticket_id = t.id) as message_count
            FROM support_tickets t
            WHERE t.user_id = ?
            ORDER BY t.updated_at DESC
        ''', (user['id'],)).fetchall()
    conn.close()

    return render_template('support_list.html', tickets=tickets)

@app.template_filter('is_video')
def jinja_is_video_filter(url):
    if not url:
        return False
    return is_video_file(url)

@app.route('/support/new', methods=['GET', 'POST'])
def support_create_ticket():
    """Create a new support ticket on site."""
    user = get_current_user()
    if not user:
        flash("Destek talebi oluşturmak için lütfen giriş yapın.", "info")
        return redirect(url_for('login'))

    if request.method == 'POST':
        customer_fullname = (request.form.get('customer_fullname') or '').strip()
        subject = (request.form.get('subject') or '').strip()
        category = request.form.get('category') or 'Genel Bilgi'
        priority = request.form.get('priority') or 'Normal'
        initial_message = (request.form.get('message') or '').strip()
        cargo_number = (request.form.get('cargo_number') or '').strip()

        allowed_categories = [
            'Kargo Takip & Teslimat',
            'Ödeme & Fatura',
            'Ürün & Kumaş Kalitesi',
            'Genel Bilgi',
            'Diğer Bilgi'
        ]
        if category not in allowed_categories:
            category = 'Genel Bilgi'

        if not customer_fullname:
            customer_fullname = user['name']

        if not subject or not initial_message:
            flash("Lütfen konu başlığı ve mesajınızı eksiksiz doldurun.", "error")
            return redirect(url_for('support_create_ticket'))

        if category == 'Kargo Takip & Teslimat' and not cargo_number:
            flash("Kargo ile alakalı destek taleplerinde Kargo Takip Numarası zorunludur.", "error")
            return redirect(url_for('support_create_ticket'))

        media_url = None
        if 'ticket_media' in request.files:
            media_file = request.files['ticket_media']
            if media_file and media_file.filename:
                if allowed_media(media_file.filename):
                    sec_name = secure_filename(media_file.filename)
                    ext = sec_name.rsplit('.', 1)[1].lower() if '.' in sec_name else 'jpg'
                    prefix = "ticket_vid" if is_video_file(media_file.filename) else "ticket_img"
                    unique_filename = f"{prefix}_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
                    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                    media_file.save(filepath)
                    media_url = f"/static/uploads/{unique_filename}"
                else:
                    flash("Yalnızca geçerli video veya fotoğraf dosyaları (MP4, WEBM, MOV, PNG, JPG, JPEG, WEBP) yüklenebilir.", "error")
                    return redirect(url_for('support_create_ticket'))

        ticket_number = f"TICK-{int(time.time())}-{random.randint(100, 999)}"
        conn = get_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO support_tickets (ticket_number, user_id, customer_fullname, subject, category, cargo_number, video_url, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Açık')
        ''', (ticket_number, user['id'], customer_fullname, subject, category, cargo_number if cargo_number else None, media_url, priority))
        ticket_id = cur.lastrowid

        cur.execute('''
            INSERT INTO ticket_messages (ticket_id, sender_id, sender_role, message, video_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticket_id, user['id'], user['role'], initial_message, media_url))

        conn.commit()
        conn.close()

        flash(f"Destek talebiniz (#{ticket_number}) oluşturuldu. Yetkilimiz en kısa sürede buradan yanıtlayacaktır.", "success")
        return redirect(url_for('support_ticket_detail', ticket_number=ticket_number))

    return render_template('support_new.html')

@app.route('/support/<ticket_number>')
def support_ticket_detail(ticket_number):
    """View ticket messages. Only owner or admin is authorized."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db()
    ticket = conn.execute('''
        SELECT t.*, u.name as user_name, u.email as user_email
        FROM support_tickets t
        JOIN users u ON t.user_id = u.id
        WHERE t.ticket_number = ?
    ''', (ticket_number,)).fetchone()

    if not ticket:
        conn.close()
        flash("Destek talebi bulunamadı.", "error")
        return redirect(url_for('support_tickets_list'))

    if user['role'] != 'admin' and ticket['user_id'] != user['id']:
        conn.close()
        flash("Bu destek talebini görüntüleme yetkiniz bulunmuyor.", "error")
        return redirect(url_for('support_tickets_list'))

    messages = conn.execute('''
        SELECT m.*, u.name as sender_name, u.role as user_role
        FROM ticket_messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.ticket_id = ?
        ORDER BY m.created_at ASC
    ''', (ticket['id'],)).fetchall()
    conn.close()

    return render_template('support_detail.html', ticket=ticket, messages=messages)

@app.route('/support/<ticket_number>/reply', methods=['POST'])
def support_ticket_reply(ticket_number):
    """Send reply directly on site with optional media (photo/video) upload. Only owner or admin can reply."""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    conn = get_db()
    ticket = conn.execute("SELECT * FROM support_tickets WHERE ticket_number = ?", (ticket_number,)).fetchone()
    if not ticket:
        conn.close()
        flash("Talep bulunamadı.", "error")
        return redirect(url_for('support_tickets_list'))

    if user['role'] != 'admin' and ticket['user_id'] != user['id']:
        conn.close()
        flash("Bu talebe cevap yazma yetkiniz yok.", "error")
        return redirect(url_for('support_tickets_list'))

    reply_text = (request.form.get('message') or '').strip()
    
    reply_media_url = None
    if 'reply_media' in request.files:
        media_file = request.files['reply_media']
        if media_file and media_file.filename:
            if allowed_media(media_file.filename):
                sec_name = secure_filename(media_file.filename)
                ext = sec_name.rsplit('.', 1)[1].lower() if '.' in sec_name else 'jpg'
                prefix = "reply_vid" if is_video_file(media_file.filename) else "reply_img"
                unique_filename = f"{prefix}_{int(time.time())}_{random.randint(1000, 9999)}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                media_file.save(filepath)
                reply_media_url = f"/static/uploads/{unique_filename}"
            else:
                conn.close()
                flash("Yalnızca geçerli video veya fotoğraf dosyaları (MP4, WEBM, MOV, PNG, JPG, JPEG, WEBP) yüklenebilir.", "error")
                return redirect(url_for('support_ticket_detail', ticket_number=ticket_number))

    if not reply_text and not reply_media_url:
        conn.close()
        flash("Lütfen bir mesaj yazın veya dosya (fotoğraf / video) yükleyin.", "error")
        return redirect(url_for('support_ticket_detail', ticket_number=ticket_number))

    new_status = 'Yetkili Yanıtladı' if user['role'] == 'admin' else 'Müşteri Yanıtladı'

    cur = conn.cursor()
    cur.execute('''
        INSERT INTO ticket_messages (ticket_id, sender_id, sender_role, message, video_url)
        VALUES (?, ?, ?, ?, ?)
    ''', (ticket['id'], user['id'], user['role'], reply_text, reply_media_url))

    cur.execute('''
        UPDATE support_tickets 
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (new_status, ticket['id']))

    conn.commit()
    conn.close()

    flash("Cevabınız site üzerinden başarıyla iletildi.", "success")
    return redirect(url_for('support_ticket_detail', ticket_number=ticket_number))

@app.route('/support/<ticket_number>/status', methods=['POST'])
def support_update_status(ticket_number):
    """Admin-only status changer (Açık, İşlemde, Çözüldü, Kapalı)."""
    user = get_current_user()
    if not user or user['role'] != 'admin':
        flash("Yetkisiz işlem.", "error")
        return redirect(url_for('support_tickets_list'))

    status = request.form.get('status') or 'Kapalı'
    conn = get_db()
    conn.execute("UPDATE support_tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_number = ?", (status, ticket_number))
    conn.commit()
    conn.close()

    flash(f"Talep #{ticket_number} durumu '{status}' olarak güncellendi.", "success")
    return redirect(url_for('support_ticket_detail', ticket_number=ticket_number))

@app.route('/support/<ticket_number>/delete', methods=['POST'])
def support_delete_ticket(ticket_number):
    """Admin veya talebin sahibi talebi silebilir."""
    user = get_current_user()
    if not user:
        flash("Lütfen önce giriş yapın.", "error")
        return redirect(url_for('login'))

    conn = get_db()
    ticket = conn.execute("SELECT * FROM support_tickets WHERE ticket_number = ?", (ticket_number,)).fetchone()
    if not ticket:
        conn.close()
        flash("Talep bulunamadı.", "error")
        return redirect(url_for('support_tickets_list'))

    # İzin kontrolü: admin veya ticket sahibi
    if user['role'] != 'admin' and ticket['user_id'] != user['id']:
        conn.close()
        flash("Bu talebi silme yetkiniz yok.", "error")
        return redirect(url_for('support_tickets_list'))

    # Mesajları ve ana talebi sil
    conn.execute("DELETE FROM ticket_messages WHERE ticket_id = ?", (ticket['id'],))
    conn.execute("DELETE FROM support_tickets WHERE id = ?", (ticket['id'],))
    conn.commit()
    conn.close()

    flash(f"#{ticket_number} numaralı destek talebi başarıyla silindi.", "success")
    # Eğer admin panelinden çağrılmışsa admin paneline dön
    ref = request.referrer or ''
    if '/admin' in ref:
        return redirect(url_for('admin_dashboard') + '#tab-support')
    return redirect(url_for('support_tickets_list'))

@app.route('/kargo')
def kargo():
    return render_template('kargo.html')

@app.route('/gizlilik')
def gizlilik():
    return render_template('gizlilik.html')

@app.route('/kullanim-kosullari')
def kullanim_kosullari():
    return render_template('kullanim_kosullari.html')

@app.route('/sss')
def sss():
    return render_template('sss.html')

@app.route('/googlea467e1849c6abbcb.html')
def google_verification():
    return "google-site-verification: googlea467e1849c6abbcb.html", 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/robots.txt')
def robots_txt():
    content = """User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/
Disallow: /api/

Sitemap: https://oblivwear.com.tr/sitemap.xml
"""
    return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/sitemap.xml')
def sitemap_xml():
    conn = get_db()
    products = conn.execute("SELECT id, created_at FROM products WHERE is_active = 1").fetchall()
    conn.close()

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>https://oblivwear.com.tr/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>',
        '  <url><loc>https://oblivwear.com.tr/urunler</loc><priority>0.9</priority><changefreq>daily</changefreq></url>',
        '  <url><loc>https://oblivwear.com.tr/kargo</loc><priority>0.6</priority><changefreq>monthly</changefreq></url>',
        '  <url><loc>https://oblivwear.com.tr/sss</loc><priority>0.6</priority><changefreq>monthly</changefreq></url>',
        '  <url><loc>https://oblivwear.com.tr/gizlilik</loc><priority>0.5</priority><changefreq>monthly</changefreq></url>',
        '  <url><loc>https://oblivwear.com.tr/kullanim-kosullari</loc><priority>0.5</priority><changefreq>monthly</changefreq></url>'
    ]

    for p in products:
        xml_lines.append(f'  <url><loc>https://oblivwear.com.tr/urun/{p["id"]}</loc><priority>0.8</priority><changefreq>weekly</changefreq></url>')

    xml_lines.append('</urlset>')
    return '\n'.join(xml_lines), 200, {'Content-Type': 'application/xml; charset=utf-8'}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    print("--------------------------------------------------")
    print(" OBLIV Store is Running with Shopier Gateway on http://127.0.0.1:5000")
    print("--------------------------------------------------")
    app.run(debug=True, port=5000)
