# OBLIV99 E-Commerce Platform

Yeni nesil, gradientsiz düz renkli ve ağır gramaj t-shirt satış sitesi.

## Özellikler
- **Tasarım:** Sadelik, yüksek okunabilirlik, mat monokrom renkler, sıfır yapay gradient.
- **Katalog & Detay:** 240-260 GSM boxy oversize modeller, beden seçimi, renk paletleri.
- **Sepet & Ödeme:** Hızlı açılır sepet paneli (drawer), 256-bit kartlı ödeme simülasyonu ve sipariş onay ekranı.
- **Üyelik Sistemi:** Müşteri kaydı, şifreleme (werkzeug hashing), müşteri sipariş geçmişi sayfası.
- **Yönetim Paneli (Admin CMS):** 
  - Satış ve ciro istatistikleri
  - Canlı sipariş ve kargo durum takibi (Hazırlanıyor, Kargoda, Teslim Edildi)
  - Yeni t-shirt ekleme ve mevcut ürünleri yönetme/silme
  - Kullanıcı listesi
- **Veritabanı:** Yerel SQLite veritabanı (`database.db`).

## Nasıl Çalıştırılır?
Sunucu arka planda çalışmaktadır. Dilerseniz konsoldan:
```powershell
py app.py
```
komutuyla başlatabilirsiniz.

Tarayıcıdan: **http://127.0.0.1:5000**

### Giriş Bilgileri
- **Admin Girişi:**
  - E-Posta: `admin@OBLIV99.com`
  - Şifre: `admin123`
- **Müşteri Girişi:**
  - E-Posta: `musteri@OBLIV99.com`
  - Şifre: `123456`
