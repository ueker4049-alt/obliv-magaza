import os
import sqlite3
import hashlib
import secrets

def sha256_hash(password: str) -> str:
    """Computes a salted SHA-256 hash for secure storage."""
    salt = "obliv_sha256_salt_2026"
    return "sha256$" + hashlib.sha256((salt + password).encode('utf-8')).hexdigest()

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verifies provided password against stored sha256 hash."""
    if not stored_hash:
        return False
    if stored_hash.startswith("sha256$"):
        return stored_hash == sha256_hash(provided_password)
    return stored_hash == sha256_hash(provided_password)

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    default_settings = {
        'store_name': "OBLIV",
        'announcement': "OBLIV // YENİ NESİL KIYAFET & GİYİM KOLEKSİYONU",
        'hero_title': "Gereksiz detaylar yok. Sadece saf kumaş ve net form.",
        'hero_subtitle': "OBLIV, yüksek kaliteli birinci sınıf tok pamuk dokusuyla sokak stilini heykelsi bir lüksle buluşturuyor.",
        'contact_email': "oblivwear@gmail.com",
        'contact_phone': "+90 850 300 3853",
        'smtp_email': "oblivwear@gmail.com",
        'smtp_app_password': "",
        'theme_color': "#FFFFFF",
        'font_heading': "'Big Shoulders Display', Impact, sans-serif",
        'font_body': "'Plus Jakarta Sans', sans-serif",
        'iyzico_api_key': "",
        'iyzico_secret_key': "",
        'iyzico_base_url': "https://sandbox-api.iyzipay.com",
        'bank_name': "Ziraat Bankası",
        'bank_account_holder': "OBLIV Tekstil San. Tic.",
        'bank_iban': "TR00 0000 0000 0000 0000 0000 00",
        'bank_instructions': "Havale / FAST açıklama kısmına lütfen SİPARİŞ KODUNUZU yazınız. Ödemeniz onaylandığında siparişiniz hazırlanacaktır."
    }

    for k, v in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_hash TEXT NOT NULL,
            path TEXT NOT NULL,
            user_agent TEXT,
            visited_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_visits_date ON site_visits(visited_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_visits_ip_date ON site_visits(ip_hash, visited_date)')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            is_verified INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            slug TEXT NOT NULL UNIQUE
        )
    ''')
    default_cats = [
        ("T-Shirt", "t-shirt")
    ]
    for c_name, c_slug in default_cats:
        cursor.execute("INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)", (c_name, c_slug))

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            old_price REAL,
            color_name TEXT NOT NULL,
            color_hex TEXT NOT NULL,
            description TEXT,
            gsm_weight TEXT DEFAULT '240 GSM Ağır Gramaj',
            fabric TEXT DEFAULT '%100 Pamuk Kompakt Penye',
            fit TEXT DEFAULT 'Oversize Street Cut',
            badge TEXT,
            image_url TEXT NOT NULL,
            stock INTEGER DEFAULT 50,
            stock_s INTEGER DEFAULT 15,
            stock_m INTEGER DEFAULT 25,
            stock_l INTEGER DEFAULT 20,
            stock_xl INTEGER DEFAULT 10,
            is_active INTEGER DEFAULT 1,
            is_featured INTEGER DEFAULT 0,
            has_360 INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Migration: Ensure has_360 and back_image_url exist
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN has_360 INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN back_image_url TEXT")
    except Exception:
        pass
    try:
        cursor.execute("UPDATE products SET display_order = 1 WHERE name LIKE '%FANGS%'")
        cursor.execute("UPDATE products SET display_order = 2 WHERE name LIKE '%STAR GIRL%'")
        cursor.execute("UPDATE products SET display_order = 3 WHERE name LIKE '%PEQUENO%'")
        cursor.execute("UPDATE products SET display_order = 4 WHERE name LIKE '%ANGEL%'")
    except Exception:
        pass

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            display_order INTEGER DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_colors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            color_name TEXT NOT NULL,
            color_hex TEXT NOT NULL,
            image_url TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            shipping_address TEXT NOT NULL,
            city TEXT NOT NULL,
            total_amount REAL NOT NULL,
            payment_status TEXT DEFAULT 'Ödendi (Simüle)',
            order_status TEXT DEFAULT 'Hazırlanıyor',
            card_last4 TEXT DEFAULT '4242',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            price REAL NOT NULL,
            size TEXT NOT NULL,
            color TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            image_url TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE SET NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            customer_fullname TEXT NOT NULL,
            subject TEXT NOT NULL,
            category TEXT NOT NULL,
            cargo_number TEXT,
            video_url TEXT,
            status TEXT DEFAULT 'Açık',
            priority TEXT DEFAULT 'Normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            message TEXT NOT NULL,
            video_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES support_tickets (id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT NOT NULL,
            photo_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute("SELECT id FROM users WHERE email = 'core@oblivwear.internal'")
    admin = cursor.fetchone()
    if not admin:
        admin_pass = sha256_hash('Obliv#99!Secure_Admin_2026')
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_verified) VALUES (?, ?, ?, ?, 1)",
                       ("OBLIV Core Admin", 'core@oblivwear.internal', admin_pass, 'admin'))

    cursor.execute("SELECT id FROM users WHERE email = 'musteri@obliv.com'")
    customer = cursor.fetchone()
    if not customer:
        cust_pass = sha256_hash('123456')
        cursor.execute("INSERT INTO users (name, email, password_hash, role, is_verified) VALUES (?, ?, ?, ?, 1)",
                       ('Müşteri', 'musteri@obliv.com', cust_pass, 'customer'))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized cleanly for OBLIV.")
