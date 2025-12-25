from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Use /tmp directory for SQLite on Render (ephemeral but writable)
DATABASE = os.path.join('/tmp', 'paypal_mvp.db') if os.path.exists('/tmp') else 'paypal_mvp.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            balance REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cards table (simulated) - Now with card type and USD balance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            card_number TEXT NOT NULL,
            card_holder TEXT NOT NULL,
            card_type TEXT NOT NULL,
            expiry TEXT NOT NULL,
            cvv TEXT NOT NULL,
            balance_usd REAL DEFAULT 200000.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER,
            from_card_id INTEGER,
            to_card_id INTEGER,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'TL',
            type TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users (id),
            FOREIGN KEY (to_user_id) REFERENCES users (id),
            FOREIGN KEY (from_card_id) REFERENCES cards (id),
            FOREIGN KEY (to_card_id) REFERENCES cards (id)
        )
    ''')
    
    # Exchange rates table - All major currencies
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exchange_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_code TEXT UNIQUE NOT NULL,
            rate_to_usd REAL NOT NULL,
            currency_name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default exchange rates if not exists
    cursor.execute('SELECT COUNT(*) FROM exchange_rates')
    if cursor.fetchone()[0] == 0:
        default_rates = [
            ('USD', 1.0, 'US Dollar', '$'),
            ('EUR', 0.92, 'Euro', '€'),
            ('GBP', 0.79, 'British Pound', '£'),
            ('JPY', 149.50, 'Japanese Yen', '¥'),
            ('CHF', 0.88, 'Swiss Franc', 'Fr'),
            ('CAD', 1.35, 'Canadian Dollar', 'C$'),
            ('AUD', 1.52, 'Australian Dollar', 'A$'),
            ('TRY', 34.50, 'Turkish Lira', '₺'),
            ('CNY', 7.24, 'Chinese Yuan', '¥'),
            ('RUB', 92.50, 'Russian Ruble', '₽'),
            ('SAR', 3.75, 'Saudi Riyal', '﷼'),
            ('AED', 3.67, 'UAE Dirham', 'د.إ'),
            ('INR', 83.12, 'Indian Rupee', '₹'),
            ('BRL', 4.97, 'Brazilian Real', 'R$'),
            ('KRW', 1305.50, 'South Korean Won', '₩'),
            ('MXN', 17.15, 'Mexican Peso', '$'),
            ('SEK', 10.35, 'Swedish Krona', 'kr'),
            ('NOK', 10.52, 'Norwegian Krone', 'kr'),
            ('DKK', 6.87, 'Danish Krone', 'kr'),
            ('PLN', 4.02, 'Polish Zloty', 'zł')
        ]
        
        for rate in default_rates:
            cursor.execute('''
                INSERT INTO exchange_rates (currency_code, rate_to_usd, currency_name, symbol)
                VALUES (?, ?, ?, ?)
            ''', rate)
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email ve şifre gerekli'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        hashed_pw = hash_password(password)
        cursor.execute('INSERT INTO users (email, password, balance) VALUES (?, ?, ?)',
                      (email, hashed_pw, 100.0))  # 100 TL başlangıç bonusu
        conn.commit()
        user_id = cursor.lastrowid
        
        return jsonify({
            'message': 'Hesap oluşturuldu! 100 TL hoş geldin bonusu eklendi.',
            'user_id': user_id,
            'email': email
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Bu email zaten kayıtlı'}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email ve şifre gerekli'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)
    cursor.execute('SELECT id, email, balance FROM users WHERE email = ? AND password = ?',
                  (email, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'user_id': user['id'],
            'email': user['email'],
            'balance': user['balance']
        }), 200
    else:
        return jsonify({'error': 'Email veya şifre hatalı'}), 401

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, balance FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'user_id': user['id'],
            'email': user['email'],
            'balance': user['balance']
        }), 200
    else:
        return jsonify({'error': 'Kullanıcı bulunamadı'}), 404

@app.route('/api/cards/<int:user_id>', methods=['GET'])
def get_cards(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, card_number, card_holder, card_type, expiry, balance_usd FROM cards WHERE user_id = ?',
                  (user_id,))
    cards = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': card['id'],
        'card_number': '**** **** **** ' + card['card_number'][-4:],
        'card_holder': card['card_holder'],
        'card_type': card['card_type'],
        'expiry': card['expiry'],
        'balance_usd': card['balance_usd']
    } for card in cards]), 200

@app.route('/api/cards', methods=['POST'])
def add_card():
    data = request.json
    user_id = data.get('user_id')
    card_number = data.get('card_number')
    card_holder = data.get('card_holder')
    card_type = data.get('card_type')
    expiry = data.get('expiry')
    cvv = data.get('cvv')
    
    if not all([user_id, card_number, card_holder, card_type, expiry, cvv]):
        return jsonify({'error': 'Tüm kart bilgileri gerekli'}), 400
    
    # Simple validation
    if len(card_number.replace(' ', '')) != 16:
        return jsonify({'error': 'Kart numarası 16 haneli olmalı'}), 400
    
    if card_type not in ['Visa', 'Mastercard', 'Troy']:
        return jsonify({'error': 'Geçersiz kart tipi'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO cards (user_id, card_number, card_holder, card_type, expiry, cvv, balance_usd)
            VALUES (?, ?, ?, ?, ?, ?, 200000.0)
        ''', (user_id, card_number.replace(' ', ''), card_holder, card_type, expiry, cvv))
        conn.commit()
        card_id = cursor.lastrowid
        
        return jsonify({
            'message': f'{card_type} kart başarıyla eklendi (200,000 USD bakiye)',
            'card_id': card_id
        }), 201
    finally:
        conn.close()

@app.route('/api/add-balance', methods=['POST'])
def add_balance():
    data = request.json
    user_id = data.get('user_id')
    card_id = data.get('card_id')
    amount = data.get('amount')
    
    if not all([user_id, card_id, amount]):
        return jsonify({'error': 'Eksik bilgi'}), 400
    
    if amount <= 0:
        return jsonify({'error': 'Miktar 0\'dan büyük olmalı'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify card belongs to user
    cursor.execute('SELECT id FROM cards WHERE id = ? AND user_id = ?', (card_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Kart bulunamadı'}), 404
    
    # Update balance
    cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
    
    # Record transaction
    cursor.execute('''
        INSERT INTO transactions (to_user_id, amount, type, description)
        VALUES (?, ?, ?, ?)
    ''', (user_id, amount, 'deposit', f'Kredi kartından {amount} TL yükleme'))
    
    conn.commit()
    
    # Get new balance
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    new_balance = cursor.fetchone()['balance']
    conn.close()
    
    return jsonify({
        'message': f'{amount} TL bakiye eklendi',
        'new_balance': new_balance
    }), 200

@app.route('/api/send-money', methods=['POST'])
def send_money():
    data = request.json
    from_user_id = data.get('from_user_id')
    to_email = data.get('to_email')
    amount = data.get('amount')
    description = data.get('description', '')
    
    if not all([from_user_id, to_email, amount]):
        return jsonify({'error': 'Eksik bilgi'}), 400
    
    if amount <= 0:
        return jsonify({'error': 'Miktar 0\'dan büyük olmalı'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get sender
    cursor.execute('SELECT balance, email FROM users WHERE id = ?', (from_user_id,))
    sender = cursor.fetchone()
    
    if not sender:
        conn.close()
        return jsonify({'error': 'Gönderen kullanıcı bulunamadı'}), 404
    
    if sender['balance'] < amount:
        conn.close()
        return jsonify({'error': 'Yetersiz bakiye'}), 400
    
    # Get receiver
    cursor.execute('SELECT id FROM users WHERE email = ?', (to_email,))
    receiver = cursor.fetchone()
    
    if not receiver:
        conn.close()
        return jsonify({'error': 'Alıcı kullanıcı bulunamadı'}), 404
    
    if sender['email'] == to_email:
        conn.close()
        return jsonify({'error': 'Kendinize para gönderemezsiniz'}), 400
    
    # Perform transaction
    cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?',
                  (amount, from_user_id))
    cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?',
                  (amount, receiver['id']))
    
    # Record transaction
    cursor.execute('''
        INSERT INTO transactions (from_user_id, to_user_id, amount, type, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (from_user_id, receiver['id'], amount, 'transfer', description))
    
    conn.commit()
    
    # Get new balance
    cursor.execute('SELECT balance FROM users WHERE id = ?', (from_user_id,))
    new_balance = cursor.fetchone()['balance']
    conn.close()
    
    return jsonify({
        'message': f'{amount} TL gönderildi',
        'new_balance': new_balance
    }), 200

@app.route('/api/exchange-rates', methods=['GET'])
def get_exchange_rates():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT currency_code, rate_to_usd, currency_name, symbol FROM exchange_rates ORDER BY currency_code')
    rates = cursor.fetchall()
    conn.close()
    
    result = {}
    for rate in rates:
        result[rate['currency_code']] = {
            'rate_to_usd': rate['rate_to_usd'],
            'currency_name': rate['currency_name'],
            'symbol': rate['symbol']
        }
    
    return jsonify(result), 200

@app.route('/api/convert-currency', methods=['POST'])
def convert_currency():
    data = request.json
    user_id = data.get('user_id')
    card_id = data.get('card_id')
    from_currency = data.get('from_currency')
    to_currency = data.get('to_currency')
    amount = data.get('amount')
    
    if not all([user_id, card_id, from_currency, to_currency, amount]):
        return jsonify({'error': 'Eksik bilgi'}), 400
    
    if amount <= 0:
        return jsonify({'error': 'Miktar 0\'dan büyük olmalı'}), 400
    
    if from_currency == to_currency:
        return jsonify({'error': 'Aynı para birimine çevrilemez'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get exchange rates
    cursor.execute('SELECT currency_code, rate_to_usd, symbol FROM exchange_rates WHERE currency_code IN (?, ?)',
                  (from_currency, to_currency))
    rates = {row['currency_code']: {'rate': row['rate_to_usd'], 'symbol': row['symbol']} 
             for row in cursor.fetchall()}
    
    if len(rates) != 2:
        conn.close()
        return jsonify({'error': 'Geçersiz para birimi'}), 400
    
    # Get card
    cursor.execute('SELECT balance_usd FROM cards WHERE id = ? AND user_id = ?', (card_id, user_id))
    card = cursor.fetchone()
    
    if not card:
        conn.close()
        return jsonify({'error': 'Kart bulunamadı'}), 404
    
    # Calculate conversion
    # Convert from_currency to USD, then USD to to_currency
    amount_in_usd = amount / rates[from_currency]['rate']
    converted_amount = amount_in_usd * rates[to_currency]['rate']
    
    # Get current user balance
    cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    # Determine source (card USD or user balance)
    if from_currency == 'USD':
        # From card USD
        if card['balance_usd'] < amount:
            conn.close()
            return jsonify({'error': f'Yetersiz USD bakiye'}), 400
        cursor.execute('UPDATE cards SET balance_usd = balance_usd - ? WHERE id = ?', (amount, card_id))
    else:
        # From user balance (stored as TL equivalent for simplicity)
        # We'll store all non-USD as TL in user balance
        if not user or user['balance'] < amount:
            conn.close()
            return jsonify({'error': f'Yetersiz {from_currency} bakiye'}), 400
        cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
    
    # Add to destination
    if to_currency == 'USD':
        # To card USD
        cursor.execute('UPDATE cards SET balance_usd = balance_usd + ? WHERE id = ?', (converted_amount, card_id))
    else:
        # To user balance
        cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (converted_amount, user_id))
    
    # Calculate exchange rate
    exchange_rate = converted_amount / amount
    
    description = f'{amount:.2f} {rates[from_currency]["symbol"]} {from_currency} → {converted_amount:.2f} {rates[to_currency]["symbol"]} {to_currency} (Kur: {exchange_rate:.4f})'
    
    # Record transaction
    cursor.execute('''
        INSERT INTO transactions (from_user_id, from_card_id, amount, currency, type, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, card_id, amount, from_currency, 'conversion', description))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Döviz çevirme başarılı',
        'description': description,
        'converted_amount': converted_amount
    }), 200

@app.route('/api/transfer-between-cards', methods=['POST'])
def transfer_between_cards():
    data = request.json
    user_id = data.get('user_id')
    from_card_id = data.get('from_card_id')
    to_card_id = data.get('to_card_id')
    amount = data.get('amount')
    
    if not all([user_id, from_card_id, to_card_id, amount]):
        return jsonify({'error': 'Eksik bilgi'}), 400
    
    if amount <= 0:
        return jsonify({'error': 'Miktar 0\'dan büyük olmalı'}), 400
    
    if from_card_id == to_card_id:
        return jsonify({'error': 'Aynı karta transfer yapılamaz'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get cards
    cursor.execute('SELECT balance_usd, card_type FROM cards WHERE id = ? AND user_id = ?', (from_card_id, user_id))
    from_card = cursor.fetchone()
    
    cursor.execute('SELECT balance_usd, card_type FROM cards WHERE id = ? AND user_id = ?', (to_card_id, user_id))
    to_card = cursor.fetchone()
    
    if not from_card or not to_card:
        conn.close()
        return jsonify({'error': 'Kart(lar) bulunamadı'}), 404
    
    if from_card['balance_usd'] < amount:
        conn.close()
        return jsonify({'error': 'Yetersiz bakiye'}), 400
    
    # Transfer
    cursor.execute('UPDATE cards SET balance_usd = balance_usd - ? WHERE id = ?', (amount, from_card_id))
    cursor.execute('UPDATE cards SET balance_usd = balance_usd + ? WHERE id = ?', (amount, to_card_id))
    
    # Record transaction
    cursor.execute('''
        INSERT INTO transactions (from_user_id, from_card_id, to_card_id, amount, currency, type, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, from_card_id, to_card_id, amount, 'USD', 'card_transfer', 
          f'{from_card["card_type"]} → {to_card["card_type"]} ({amount} USD)'))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f'{amount} USD transfer başarılı'
    }), 200

@app.route('/api/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT t.*, 
               u_from.email as from_email,
               u_to.email as to_email,
               c_from.card_type as from_card_type,
               c_to.card_type as to_card_type
        FROM transactions t
        LEFT JOIN users u_from ON t.from_user_id = u_from.id
        LEFT JOIN users u_to ON t.to_user_id = u_to.id
        LEFT JOIN cards c_from ON t.from_card_id = c_from.id
        LEFT JOIN cards c_to ON t.to_card_id = c_to.id
        WHERE t.from_user_id = ? OR t.to_user_id = ?
        ORDER BY t.created_at DESC
        LIMIT 50
    ''', (user_id, user_id))
    
    transactions = cursor.fetchall()
    conn.close()
    
    result = []
    for tx in transactions:
        result.append({
            'id': tx['id'],
            'amount': tx['amount'],
            'currency': tx['currency'] if tx['currency'] else 'TL',
            'type': tx['type'],
            'description': tx['description'],
            'from_email': tx['from_email'],
            'to_email': tx['to_email'],
            'from_card_type': tx['from_card_type'],
            'to_card_type': tx['to_card_type'],
            'created_at': tx['created_at'],
            'is_incoming': tx['to_user_id'] == user_id
        })
    
    return jsonify(result), 200

# Error handler for better debugging
@app.errorhandler(Exception)
def handle_error(error):
    import traceback
    app.logger.error(f"Error: {str(error)}")
    app.logger.error(traceback.format_exc())
    return jsonify({'error': str(error), 'type': type(error).__name__}), 500

# Initialize database on app startup (for both gunicorn and direct run)
try:
    with app.app_context():
        init_db()
        app.logger.info(f"Database initialized at {DATABASE}")
except Exception as e:
    app.logger.error(f"Failed to initialize database: {str(e)}")
    raise

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
