# Traca Property Management Portals Startup Script
Write-Host "Starting Traca Property Management Portals..." -ForegroundColor Green
Write-Host ""

# Navigate to the script's directory
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Definition)

# Activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated successfully!" -ForegroundColor Green
} else {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please ensure 'venv' directory exists." -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Starting Django server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PORTALS WILL BE AVAILABLE AT:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Main Website: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  Landlord Portal: http://127.0.0.1:8000/landlord/" -ForegroundColor White
Write-Host "  Tenant Portal: http://127.0.0.1:8000/tenant/" -ForegroundColor White
Write-Host "  Admin Panel: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Django server
python manage.py runserver 127.0.0.1:8000
