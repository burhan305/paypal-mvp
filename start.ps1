# PayPal MVP - PowerShell Start Script

Write-Host "====================================" -ForegroundColor Cyan
Write-Host " PayPal MVP - Sanal Para Transferi" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Find Python installation
$pythonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "python",
    "python3"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    try {
        $version = & $path --version 2>&1
        if ($version -match "Python") {
            $pythonExe = $path
            Write-Host "Python bulundu: $version" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonExe) {
    Write-Host "Hata: Python bulunamadi!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Python kurulum adresi: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Kurulum sirasinda 'Add Python to PATH' secenegini isaretleyin." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Devam etmek icin bir tusa basin"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[1/2] Bagimliliklar kontrol ediliyor..." -ForegroundColor Green
& $pythonExe -m pip install -q flask flask-cors 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "Uyari: Paket kurulumunda sorun olabilir, devam ediliyor..." -ForegroundColor Yellow
}

# Start server
Write-Host "[2/2] Sunucu baslatiliyor..." -ForegroundColor Green
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host " Tarayicinizda acin:" -ForegroundColor White
Write-Host " http://localhost:5000" -ForegroundColor Yellow
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demo Hesaplar:" -ForegroundColor Gray
Write-Host "  Email: test@example.com | Sifre: 123456" -ForegroundColor Gray
Write-Host "  Email: alici@example.com | Sifre: 123456" -ForegroundColor Gray
Write-Host ""
Write-Host "Sunucuyu durdurmak icin CTRL+C basin" -ForegroundColor Gray
Write-Host ""

# Start Flask app
& $pythonExe app.py
