# 💎 PayPal MVP - Modern Para Transferi Platformu

Modern, güvenli ve kullanıcı dostu para transferi ve döviz çevirme platformu.

## 🌟 Özellikler

### 💳 Kart Yönetimi
- **3 Kart Tipi:** Visa, Mastercard, Troy
- Her kart **200,000 USD** başlangıç bakiyesi
- Gerçek zamanlı bakiye takibi
- Kartlar arası transfer

### 💱 Döviz İşlemleri (20 Para Birimi)
- 🇺🇸 USD - US Dollar
- 🇪🇺 EUR - Euro
- 🇬🇧 GBP - British Pound
- 🇯🇵 JPY - Japanese Yen
- 🇨🇭 CHF - Swiss Franc
- 🇨🇦 CAD - Canadian Dollar
- 🇦🇺 AUD - Australian Dollar
- 🇹🇷 TRY - Turkish Lira
- 🇨🇳 CNY - Chinese Yuan
- 🇷🇺 RUB - Russian Ruble
- 🇸🇦 SAR - Saudi Riyal
- 🇦🇪 AED - UAE Dirham
- 🇮🇳 INR - Indian Rupee
- 🇧🇷 BRL - Brazilian Real
- 🇰🇷 KRW - South Korean Won
- 🇲🇽 MXN - Mexican Peso
- 🇸🇪 SEK - Swedish Krona
- 🇳🇴 NOK - Norwegian Krone
- 🇩🇰 DKK - Danish Krone
- 🇵🇱 PLN - Polish Zloty

### 🎨 Tema Sistemi
- **Light Mode** - Modern aydınlık tema
- **Dark Mode** - Göz yormayan karanlık tema
- Otomatik tema saklama
- Smooth geçiş animasyonları

### 💸 Transfer Özellikleri
- Email ile para gönderme
- Kartlar arası USD transferi
- 20 farklı para birimi arası çevirme
- Anlık kur hesaplama
- Detaylı işlem geçmişi

## 🚀 Kurulum

### Gereksinimler
- Python 3.7+
- pip veya uv

### Adım 1: Depoyu İndirin
```bash
git clone <repo-url>
cd paypal_mvp_blueprint
```

### Adım 2: Sunucuyu Başlatın

**Windows (PowerShell):**
```powershell
.\start.ps1
```

**Windows (CMD):**
```cmd
start.bat
```

**Manuel Başlatma:**
```bash
# Virtual environment oluştur
python -m venv .venv

# Aktif et (Windows)
.venv\Scripts\activate

# Aktif et (Linux/Mac)
source .venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Sunucuyu başlat
python app.py
```

### Adım 3: Tarayıcıda Açın
```
http://localhost:5000
```

## 📱 Kullanım

### 1. Hesap Oluşturma
- Email ve şifre ile kayıt olun
- 100 TL hoş geldin bonusu kazanın

### 2. Kart Ekleme
- Kartlar sekmesine gidin
- "Yeni Kart Ekle" butonuna tıklayın
- Visa, Mastercard veya Troy seçin
- Her kart otomatik 200,000 USD ile gelir

### 3. Döviz Çevirme
- Döviz sekmesine gidin
- 20 farklı para birimi görün
- Kaynak ve hedef para birimini seçin
- Anlık önizleme ile çevirme yapın

### 4. Para Transferi
- Para Gönder sekmesinden email ile transfer
- Kart Transfer sekmesinden kartlar arası USD transferi
- İşlemler sekmesinden geçmişi görün

## 🎯 Demo Hesap

Test için hazır hesap:
- **Email:** demo@paypal.com
- **Şifre:** 123456
- **3 Kart:** Visa, Mastercard, Troy (her biri 200k USD)

## 🛠️ Teknolojiler

### Backend
- **Flask** - Python web framework
- **SQLite** - Veritabanı
- **Flask-CORS** - Cross-origin desteği

### Frontend
- **Vanilla JavaScript** - Framework'süz modern JS
- **HTML5 & CSS3** - Modern web standartları
- **Glassmorphism** - Modern UI tasarımı
- **Google Fonts (Inter)** - Tipografi

## 📊 Veritabanı Yapısı

### Users (Kullanıcılar)
- id, email, password, balance (TL), created_at

### Cards (Kartlar)
- id, user_id, card_number, card_holder, card_type, expiry, cvv, balance_usd, created_at

### Transactions (İşlemler)
- id, from_user_id, to_user_id, from_card_id, to_card_id, amount, currency, type, description, created_at

### Exchange Rates (Döviz Kurları)
- id, currency_code, rate_to_usd, currency_name, symbol, updated_at

## 🔒 Güvenlik Notları

⚠️ **Bu bir MVP/Demo projesidir. Production kullanımı için:**

1. **Şifreleme:** Bcrypt veya Argon2 kullanın (şu anda SHA256)
2. **JWT Token:** Session yönetimi için JWT ekleyin
3. **HTTPS:** SSL sertifikası kullanın
4. **Rate Limiting:** API rate limiting ekleyin
5. **Input Validation:** Daha güçlü validasyon
6. **Database:** PostgreSQL/MySQL kullanın (şu anda SQLite)
7. **Environment Variables:** Hassas bilgiler için .env kullanın
8. **CSRF Protection:** Cross-site request forgery koruması
9. **SQL Injection:** Prepared statements (mevcut ama ekstra kontrol)
10. **XSS Protection:** Content Security Policy ekleyin

## 🌐 Production Deployment

### Render.com (Ücretsiz)
1. GitHub'a push yapın
2. Render.com'da yeni Web Service oluşturun
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Environment Variables ekleyin

### Heroku (Ücretsiz/Ücretli)
1. `Procfile` oluşturun: `web: gunicorn app:app`
2. `heroku create`
3. `git push heroku main`
4. `heroku open`

### Railway (Ücretsiz)
1. GitHub repository bağlayın
2. Otomatik deploy başlar
3. Environment variables ayarlayın

### Production Gereksinimler
```txt
gunicorn==21.2.0
flask==3.0.0
flask-cors==4.0.0
psycopg2-binary==2.9.9  # PostgreSQL için
```

## 📈 Gelecek Özellikler

- [ ] 2FA (Two-Factor Authentication)
- [ ] Email bildirimleri
- [ ] Profil fotoğrafı
- [ ] İşlem limitleri
- [ ] Aylık raporlar
- [ ] Mobil uygulama
- [ ] QR kod ile ödeme
- [ ] Otomatik tasarruf
- [ ] Kripto para desteği

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

MIT License - Detaylar için `LICENSE` dosyasına bakın.

## 👤 Geliştirici

Geliştirilme Tarihi: Aralık 2025

## 🙏 Teşekkürler

- PayPal logo renkleri ilhamı
- Inter font ailesi
- Flask ve Python topluluğu
- Tüm açık kaynak katkıcıları

---

**⭐ Projeyi beğendiyseniz yıldız vermeyi unutmayın!**

Proje şaka amaçlı yapılmıştır buradaki herşey sahtedir
