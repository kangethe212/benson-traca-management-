@echo off
echo ========================================
echo    TRACA Management Services
echo    Starting Development Server
echo ========================================
echo.

echo [1/3] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

echo [2/3] Checking Django installation...
python -c "import django; print('Django version:', django.get_version())"
if %errorlevel% neq 0 (
    echo ERROR: Django not found! Please install requirements first.
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [3/3] Starting Django development server...
echo.
echo ========================================
echo    Server will start at:
echo    http://127.0.0.1:8000/
echo.
echo    Admin Panel:
echo    http://127.0.0.1:8000/admin/
echo    Username: admin
echo    Password: admin123
echo.
echo    Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver

echo.
echo Server stopped. Press any key to exit...
pause >nul
