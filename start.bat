@echo off
echo ====================================
echo  PayPal MVP - Sanal Para Transferi
echo ====================================
echo.

REM Install dependencies globally (simpler approach)
echo [1/2] Bagimliliklar yukleniyor...
pip install -q flask flask-cors 2>nul
if errorlevel 1 (
    echo Hata: pip bulunamadi! 
    echo.
    echo Python kurulumu icin: https://www.python.org/downloads/
    echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin.
    echo.
    pause
    exit /b 1
)

echo [2/2] Sunucu baslatiliyor...
echo.
echo ====================================
echo  Tarayicinizda acin:
echo  http://localhost:5000
echo ====================================
echo.
echo Sunucuyu durdurmak icin CTRL+C basin
echo.

REM Start the Flask application
python app.py
