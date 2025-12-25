# 🚀 Deployment Guide - PayPal MVP

Bu guide, PayPal MVP'yi çeşitli platformlarda yayınlamak için adım adım talimatları içerir.

## 📋 Hazırlık

### 1. Git Repository Oluşturma

```bash
git init
git add .
git commit -m "Initial commit: PayPal MVP with 20 currencies"
```

### 2. GitHub'a Push (Opsiyonel ama önerilen)

```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

## 🌐 Deployment Seçenekleri

### Option 1: Render.com (Önerilen - Ücretsiz)

#### Adımlar:
1. **Render.com'a Git:** https://render.com
2. **Sign Up / Login**
3. **New Web Service** butonuna tıkla
4. **GitHub Repository Bağla** veya **Public Git Repository** kullan

#### Ayarlar:
- **Name:** paypal-mvp
- **Environment:** Python 3
- **Build Command:**
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  gunicorn app:app
  ```
- **Plan:** Free

#### Environment Variables (Opsiyonel):
- `FLASK_DEBUG=False`

#### Deploy:
- "Create Web Service" butonuna tıkla
- Otomatik deployment başlar
- URL: `https://paypal-mvp-xxxx.onrender.com`

### Option 2: Railway.app (Kolay ve Hızlı)

#### Adımlar:
1. **Railway.app'e Git:** https://railway.app
2. **GitHub ile Login**
3. **New Project** → **Deploy from GitHub repo**
4. Repository seç
5. Otomatik detect eder ve deploy eder

#### Ayarlar:
Railway otomatik olarak algılar ama custom ayarlar için:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

#### Domain:
- Otomatik bir domain verir: `paypal-mvp.up.railway.app`
- Custom domain ekleyebilirsiniz

### Option 3: Heroku (Klasik)

#### Hazırlık:
```bash
# Heroku CLI kur (Windows)
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# App oluştur
heroku create paypal-mvp-unique-name
```

#### Deploy:
```bash
git push heroku main
```

#### Database (Production için):
```bash
heroku addons:create heroku-postgresql:mini
```

#### Log İzleme:
```bash
heroku logs --tail
```

### Option 4: PythonAnywhere (Basit)

#### Adımlar:
1. **PythonAnywhere.com'a Git:** https://www.pythonanywhere.com
2. **Free Account** oluştur
3. **Web** sekmesine git
4. **Add a new web app** → **Flask** seç
5. **Upload** sekmesinden projeyi yükle

#### Manuel Setup:
```bash
# Virtual environment
mkvirtualenv paypal-env --python=python3.10

# Dependencies yükle
pip install -r requirements.txt

# WSGI file düzenle
# /var/www/<username>_pythonanywhere_com_wsgi.py
```

## 🔒 Production Güvenliği

### 1. Environment Variables Kullanın

`.env` dosyası oluşturun (GIT'e eklemeyin):
```env
FLASK_SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://...
FLASK_DEBUG=False
```

### 2. app.py Güncellemeleri

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Production database
if 'DATABASE_URL' in os.environ:
    # PostgreSQL kullan
    pass
else:
    # SQLite kullan (development)
    pass
```

### 3. HTTPS Kullanın

Tüm modern platformlar otomatik HTTPS sağlar, ancak kontrol edin:
- Render: Otomatik SSL
- Railway: Otomatik SSL
- Heroku: Otomatik SSL

### 4. Rate Limiting Ekleyin

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### 5. CORS Ayarları

Production için CORS'u sınırlayın:

```python
CORS(app, origins=['https://yourdomain.com'])
```

## 📊 Production Database (PostgreSQL)

### 1. psycopg2 Ekle

```txt
# requirements.txt'e ekle
psycopg2-binary==2.9.9
```

### 2. app.py'de Database Switch

```python
import os

DATABASE = os.environ.get('DATABASE_URL', 'paypal_mvp.db')

if DATABASE.startswith('postgres'):
    # PostgreSQL bağlantısı
    import psycopg2
    conn = psycopg2.connect(DATABASE)
else:
    # SQLite bağlantısı
    conn = sqlite3.connect(DATABASE)
```

## 🎯 Deployment Checklist

- [ ] Git repository oluşturuldu
- [ ] README.md hazır
- [ ] .gitignore eklendi
- [ ] requirements.txt güncel
- [ ] Procfile eklendi
- [ ] Debug mode kapatıldı
- [ ] Secret key production-ready
- [ ] CORS ayarları yapıldı
- [ ] Database production-ready
- [ ] HTTPS aktif
- [ ] Rate limiting eklendi
- [ ] Error handling iyileştirildi
- [ ] Logging eklendi

## 🔍 Test Etme

Deployment sonrası test için:

```bash
# Health check
curl https://your-app.com/

# API test
curl https://your-app.com/api/exchange-rates

# Frontend test
# Tarayıcıda aç: https://your-app.com
```

## 📱 Custom Domain

### Render.com
1. Settings → Custom Domain
2. CNAME ekle: `your-domain.com` → `your-app.onrender.com`

### Railway
1. Settings → Domains
2. Custom Domain ekle

### Heroku
```bash
heroku domains:add www.your-domain.com
```

DNS ayarlarında:
```
CNAME www your-app.herokuapp.com
```

## 🚨 Monitoring

### Sentry (Error Tracking)

```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
)
```

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/...')
def endpoint():
    logger.info(f'Request from {request.remote_addr}')
```

## 💡 İpuçları

1. **Free Tier Limitleri:**
   - Render: 750 saat/ay
   - Railway: $5 ücretsiz kredi/ay
   - Heroku: Artık ücretsiz plan yok

2. **Sleep Mode:**
   - Free planlar inaktivitede sleep mode'a girer
   - İlk request 30-60 saniye sürebilir

3. **Database Backup:**
   - SQLite → GitHub'a commit etmeyin
   - PostgreSQL → Otomatik backup yapın

4. **Performance:**
   - CDN kullanın (Cloudflare)
   - Static dosyaları cache'leyin
   - Database query'lerini optimize edin

## 📞 Destek

Sorun yaşarsanız:
1. Platform documentation okuyun
2. Logs kontrol edin
3. GitHub Issues açın

---

**🎉 Başarılı deployment!**

Siteyi paylaşmayı unutmayın: `https://your-paypal-mvp.com`
