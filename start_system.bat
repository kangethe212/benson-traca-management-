@echo off
echo Starting TRACA Management System...
echo.

echo [1/2] Starting Django Backend Server...
start cmd /k "python manage.py runserver 8000"

echo [2/2] Opening browser...
timeout /t 5 >nul
start http://localhost:8000

echo.
echo TRACA Management System is running!
echo Frontend: http://localhost:8000
echo Admin: http://localhost:8000/admin
echo.
pause
