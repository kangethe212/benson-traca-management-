@echo off
echo Starting Traca Property Management Portals...
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call .\venv\Scripts\activate.bat

echo.
echo Starting Django server...
echo.
echo ========================================
echo  PORTALS WILL BE AVAILABLE AT:
echo ========================================
echo  Main Website: http://127.0.0.1:8000/
echo  Landlord Portal: http://127.0.0.1:8000/landlord/
echo  Tenant Portal: http://127.0.0.1:8000/tenant/
echo  Admin Panel: http://127.0.0.1:8000/admin/
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver 127.0.0.1:8000

pause
