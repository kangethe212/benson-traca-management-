@echo off
echo ========================================
echo    TRACA Management System Startup
echo ========================================
echo.

echo [1/3] Starting Django Backend Server...
start "Django Backend" cmd /k "cd /d %~dp0 && python manage.py runserver 8000"

echo Waiting for Django server to start...
timeout /t 3 >nul

echo [2/3] Checking Django server status...
curl -s http://localhost:8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Django Backend is running on http://localhost:8000
) else (
    echo ❌ Django Backend failed to start
    pause
    exit /b 1
)

echo [3/3] Opening browser...
timeout /t 2 >nul
start http://localhost:8000

echo.
echo ========================================
echo    TRACA Management System Ready!
echo ========================================
echo.
echo 🏠 Frontend: http://localhost:8000
echo 🔧 Admin Panel: http://localhost:8000/admin
echo 📊 API: http://localhost:8000/api
echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping Django server...
taskkill /F /IM python.exe >nul 2>&1

echo ✅ All servers stopped
timeout /t 2 >nul
exit
