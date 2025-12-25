const API_URL = 'http://localhost:5000/api';
let currentUser = null;
let userCards = [];
let exchangeRates = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showDashboard();
    }
    
    // Load theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon();
    }
    
    // Auto-format card number input
    const cardNumberInput = document.getElementById('cardNumber');
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\s/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;
        });
    }
    
    // Auto-format expiry input
    const expiryInput = document.getElementById('cardExpiry');
    if (expiryInput) {
        expiryInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\//g, '');
            if (value.length >= 2) {
                e.target.value = value.slice(0, 2) + '/' + value.slice(2, 4);
            } else {
                e.target.value = value;
            }
        });
    }
    
    // Load exchange rate
    loadExchangeRate();
});

// Theme Functions
function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon();
}

function updateThemeIcon() {
    const isDark = document.body.classList.contains('dark-theme');
    const icons = document.querySelectorAll('.theme-icon');
    icons.forEach(icon => {
        icon.textContent = isDark ? '☀️' : '🌙';
    });
}

// Auth Functions
function showLogin() {
    document.getElementById('loginForm').classList.add('active');
    document.getElementById('registerForm').classList.remove('active');
    clearMessage('authMessage');
}

function showRegister() {
    document.getElementById('registerForm').classList.add('active');
    document.getElementById('loginForm').classList.remove('active');
    clearMessage('authMessage');
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            localStorage.setItem('currentUser', JSON.stringify(data));
            showDashboard();
        } else {
            showMessage('authMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('authMessage', 'Bağlantı hatası', 'error');
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('authMessage', data.message, 'success');
            setTimeout(() => {
                currentUser = { user_id: data.user_id, email: data.email };
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                showDashboard();
            }, 1500);
        } else {
            showMessage('authMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('authMessage', 'Bağlantı hatası', 'error');
    }
}

function handleLogout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    document.getElementById('dashboardScreen').classList.remove('active');
    document.getElementById('authScreen').classList.add('active');
    showLogin();
}

// Dashboard Functions
async function showDashboard() {
    document.getElementById('authScreen').classList.remove('active');
    document.getElementById('dashboardScreen').classList.add('active');
    
    document.getElementById('userEmail').textContent = currentUser.email;
    
    await updateBalance();
    await loadCards();
    await loadTransactions();
}

async function updateBalance() {
    try {
        const response = await fetch(`${API_URL}/user/${currentUser.user_id}`);
        const data = await response.json();
        
        if (response.ok) {
            currentUser.balance = data.balance;
            document.getElementById('balanceAmount').textContent = 
                `${data.balance.toFixed(2)} ₺`;
        }
    } catch (error) {
        console.error('Balance update error:', error);
    }
}

// Tab Functions
function showTab(tabName) {
    // Update tab buttons with smooth transition
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Find the clicked tab button
    const clickedTab = event.target.closest('.tab');
    if (clickedTab) {
        clickedTab.classList.add('active');
    }
    
    // Update tab content with fade effect
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.opacity = '0';
        setTimeout(() => {
            content.classList.remove('active');
        }, 200);
    });
    
    setTimeout(() => {
        const targetTab = document.getElementById(tabName + 'Tab');
        targetTab.classList.add('active');
        setTimeout(() => {
            targetTab.style.opacity = '1';
        }, 10);
    }, 200);
    
    // Reload data based on tab
    if (tabName === 'transactions') {
        loadTransactions();
    } else if (tabName === 'cards') {
        loadCards();
    }
}

// Card Functions
async function loadCards() {
    try {
        const response = await fetch(`${API_URL}/cards/${currentUser.user_id}`);
        userCards = await response.json();
        
        const cardsList = document.getElementById('cardsList');
        
        if (userCards.length === 0) {
            cardsList.innerHTML = '<p class="empty-state">Henüz kart eklenmemiş</p>';
        } else {
            cardsList.innerHTML = userCards.map(card => {
                const cardTypeIcon = card.card_type === 'Visa' ? '💳' : 
                                    card.card_type === 'Mastercard' ? '💳' : '💳';
                return `
                    <div class="card-item">
                        <div class="card-type">${cardTypeIcon} ${card.card_type}</div>
                        <div class="card-number">${card.card_number}</div>
                        <div class="card-holder">${card.card_holder}</div>
                        <div class="card-balance">💰 ${card.balance_usd.toLocaleString('en-US')} USD</div>
                        <div class="card-expiry">Exp: ${card.expiry}</div>
                    </div>
                `;
            }).join('');
        }
        
        // Update card selections
        updateCardSelection();
        updateCardSelections();
    } catch (error) {
        console.error('Load cards error:', error);
    }
}

function updateCardSelection() {
    const select = document.getElementById('selectedCard');
    select.innerHTML = '<option value="">Kart seçiniz...</option>';
    
    userCards.forEach(card => {
        const option = document.createElement('option');
        option.value = card.id;
        option.textContent = `${card.card_number} - ${card.card_holder}`;
        select.appendChild(option);
    });
}

function showAddCard() {
    document.getElementById('addCardModal').classList.add('active');
}

async function handleAddCard(event) {
    event.preventDefault();
    
    const cardData = {
        user_id: currentUser.user_id,
        card_number: document.getElementById('cardNumber').value,
        card_holder: document.getElementById('cardHolder').value,
        card_type: document.getElementById('cardType').value,
        expiry: document.getElementById('cardExpiry').value,
        cvv: document.getElementById('cardCVV').value
    };
    
    try {
        const response = await fetch(`${API_URL}/cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cardData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('dashboardMessage', data.message, 'success');
            closeModal('addCardModal');
            event.target.reset();
            await loadCards();
            updateCardSelections();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Bağlantı hatası');
    }
}

// Balance Functions
function showAddBalance() {
    if (userCards.length === 0) {
        alert('Önce bir kart eklemelisiniz!');
        showTab('cards');
        return;
    }
    
    updateCardSelection();
    document.getElementById('addBalanceModal').classList.add('active');
}

async function handleAddBalance() {
    const cardId = document.getElementById('selectedCard').value;
    const amount = parseFloat(document.getElementById('addBalanceAmount').value);
    
    if (!cardId) {
        alert('Lütfen bir kart seçin');
        return;
    }
    
    if (!amount || amount <= 0) {
        alert('Geçerli bir miktar girin');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/add-balance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: currentUser.user_id,
                card_id: cardId,
                amount: amount
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('dashboardMessage', data.message, 'success');
            closeModal('addBalanceModal');
            document.getElementById('addBalanceAmount').value = '';
            await updateBalance();
            await loadTransactions();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert('Bağlantı hatası');
    }
}

// Transaction Functions
async function loadTransactions() {
    try {
        const response = await fetch(`${API_URL}/transactions/${currentUser.user_id}`);
        const transactions = await response.json();
        
        const transactionsList = document.getElementById('transactionsList');
        
        if (transactions.length === 0) {
            transactionsList.innerHTML = '<p class="empty-state">Henüz işlem yok</p>';
        } else {
            transactionsList.innerHTML = transactions.map(tx => {
                const isIncoming = tx.is_incoming;
                const otherEmail = isIncoming ? tx.from_email : tx.to_email;
                const amountClass = isIncoming ? 'incoming' : 'outgoing';
                const amountSign = isIncoming ? '+' : '-';
                const label = tx.type === 'deposit' ? 'Bakiye Yükleme' : 
                             (isIncoming ? 'Gelen Transfer' : 'Giden Transfer');
                
                return `
                    <div class="transaction-item">
                        <div class="transaction-info">
                            <div class="transaction-email">${label}</div>
                            ${otherEmail ? `<div class="transaction-desc">${otherEmail}</div>` : ''}
                            ${tx.description ? `<div class="transaction-desc">${tx.description}</div>` : ''}
                            <div class="transaction-date">${formatDate(tx.created_at)}</div>
                        </div>
                        <div class="transaction-amount ${amountClass}">
                            ${amountSign}${tx.amount.toFixed(2)} ₺
                        </div>
                    </div>
                `;
            }).join('');
        }
    } catch (error) {
        console.error('Load transactions error:', error);
    }
}

async function handleSendMoney(event) {
    event.preventDefault();
    
    const recipientEmail = document.getElementById('recipientEmail').value;
    const amount = parseFloat(document.getElementById('sendAmount').value);
    const description = document.getElementById('sendDescription').value;
    
    if (recipientEmail === currentUser.email) {
        showMessage('dashboardMessage', 'Kendinize para gönderemezsiniz', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/send-money`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                from_user_id: currentUser.user_id,
                to_email: recipientEmail,
                amount: amount,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('dashboardMessage', data.message, 'success');
            event.target.reset();
            await updateBalance();
            await loadTransactions();
        } else {
            showMessage('dashboardMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('dashboardMessage', 'Bağlantı hatası', 'error');
    }
}

// Exchange Rate Functions
async function loadExchangeRate() {
    try {
        const response = await fetch(`${API_URL}/exchange-rates`);
        exchangeRates = await response.json();
        
        // Populate currency grid
        const grid = document.getElementById('currencyGrid');
        if (grid) {
            grid.innerHTML = Object.entries(exchangeRates)
                .sort((a, b) => a[0].localeCompare(b[0]))
                .map(([code, data]) => `
                    <div class="currency-item">
                        <div class="currency-code">${data.symbol} ${code}</div>
                        <div class="currency-name">${data.currency_name}</div>
                        <div class="currency-rate">1 ${code} = ${(1 / data.rate_to_usd).toFixed(4)} USD</div>
                    </div>
                `).join('');
        }
        
        // Populate currency selects
        const fromSelect = document.getElementById('fromCurrency');
        const toSelect = document.getElementById('toCurrency');
        
        if (fromSelect && toSelect) {
            const options = Object.entries(exchangeRates)
                .sort((a, b) => a[0].localeCompare(b[0]))
                .map(([code, data]) => 
                    `<option value="${code}">${data.symbol} ${code} - ${data.currency_name}</option>`
                ).join('');
            
            fromSelect.innerHTML = '<option value="">Seçiniz...</option>' + options;
            toSelect.innerHTML = '<option value="">Seçiniz...</option>' + options;
            
            // Set defaults
            fromSelect.value = 'USD';
            toSelect.value = 'TRY';
        }
        
        // Add change listeners for preview
        document.getElementById('fromCurrency')?.addEventListener('change', updateExchangePreview);
        document.getElementById('toCurrency')?.addEventListener('change', updateExchangePreview);
        document.getElementById('exchangeAmount')?.addEventListener('input', updateExchangePreview);
        
    } catch (error) {
        console.error('Load exchange rate error:', error);
    }
}

function updateExchangePreview() {
    const fromCurrency = document.getElementById('fromCurrency').value;
    const toCurrency = document.getElementById('toCurrency').value;
    const amount = parseFloat(document.getElementById('exchangeAmount').value);
    const preview = document.getElementById('exchangePreview');
    
    if (!fromCurrency || !toCurrency || !amount || amount <= 0 || fromCurrency === toCurrency) {
        preview.style.display = 'none';
        return;
    }
    
    const fromRate = exchangeRates[fromCurrency].rate_to_usd;
    const toRate = exchangeRates[toCurrency].rate_to_usd;
    const amountInUsd = amount / fromRate;
    const convertedAmount = amountInUsd * toRate;
    
    const fromSymbol = exchangeRates[fromCurrency].symbol;
    const toSymbol = exchangeRates[toCurrency].symbol;
    
    preview.innerHTML = `
        <div class="exchange-preview-text">
            ${fromSymbol} ${amount.toFixed(2)} ${fromCurrency} = ${toSymbol} ${convertedAmount.toFixed(2)} ${toCurrency}
        </div>
    `;
    preview.style.display = 'block';
}

async function handleExchange(event) {
    event.preventDefault();
    
    const exchangeData = {
        user_id: currentUser.user_id,
        card_id: document.getElementById('exchangeCard').value,
        from_currency: document.getElementById('fromCurrency').value,
        to_currency: document.getElementById('toCurrency').value,
        amount: parseFloat(document.getElementById('exchangeAmount').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/convert-currency`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(exchangeData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('dashboardMessage', data.message + ': ' + data.description, 'success');
            event.target.reset();
            await updateBalance();
            await loadCards();
            await loadTransactions();
        } else {
            showMessage('dashboardMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('dashboardMessage', 'Bağlantı hatası', 'error');
    }
}

async function handleCardTransfer(event) {
    event.preventDefault();
    
    const transferData = {
        user_id: currentUser.user_id,
        from_card_id: document.getElementById('fromCard').value,
        to_card_id: document.getElementById('toCard').value,
        amount: parseFloat(document.getElementById('transferAmount').value)
    };
    
    try {
        const response = await fetch(`${API_URL}/transfer-between-cards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(transferData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('dashboardMessage', data.message, 'success');
            event.target.reset();
            await loadCards();
            await loadTransactions();
        } else {
            showMessage('dashboardMessage', data.error, 'error');
        }
    } catch (error) {
        showMessage('dashboardMessage', 'Bağlantı hatası', 'error');
    }
}

function updateCardSelections() {
    const fromCard = document.getElementById('fromCard');
    const toCard = document.getElementById('toCard');
    const exchangeCard = document.getElementById('exchangeCard');
    
    if (fromCard) {
        fromCard.innerHTML = '<option value="">Kart seçiniz...</option>';
        userCards.forEach(card => {
            const option = document.createElement('option');
            option.value = card.id;
            option.textContent = `${card.card_type} - ${card.card_number} (${card.balance_usd.toLocaleString()} USD)`;
            fromCard.appendChild(option);
        });
    }
    
    if (toCard) {
        toCard.innerHTML = '<option value="">Kart seçiniz...</option>';
        userCards.forEach(card => {
            const option = document.createElement('option');
            option.value = card.id;
            option.textContent = `${card.card_type} - ${card.card_number} (${card.balance_usd.toLocaleString()} USD)`;
            toCard.appendChild(option);
        });
    }
    
    if (exchangeCard) {
        exchangeCard.innerHTML = '<option value="">Kart seçiniz...</option>';
        userCards.forEach(card => {
            const option = document.createElement('option');
            option.value = card.id;
            option.textContent = `${card.card_type} - ${card.card_number} (${card.balance_usd.toLocaleString()} USD)`;
            exchangeCard.appendChild(option);
        });
    }
}

// Helper Functions
function showMessage(elementId, message, type) {
    const messageEl = document.getElementById(elementId);
    messageEl.textContent = message;
    messageEl.className = `message ${type}`;
    
    setTimeout(() => {
        messageEl.className = 'message';
    }, 5000);
}

function clearMessage(elementId) {
    const messageEl = document.getElementById(elementId);
    messageEl.className = 'message';
    messageEl.textContent = '';
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Az önce';
    if (minutes < 60) return `${minutes} dakika önce`;
    if (hours < 24) return `${hours} saat önce`;
    if (days < 7) return `${days} gün önce`;
    
    return date.toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}
