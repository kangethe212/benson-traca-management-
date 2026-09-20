@echo off
echo ========================================
echo    TRACA Management System Cleanup
echo ========================================
echo.

echo [1/5] Cleaning Python cache files...
if exist "__pycache__" rmdir /s /q "__pycache__"
for /r . %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d"
if exist "*.pyc" del /q "*.pyc"
echo ✅ Python cache files cleaned

echo [2/5] Cleaning Django database files...
if exist "db.sqlite3" (
    echo 📊 Keeping database file (db.sqlite3)
) else (
    echo ℹ️  No database file found
)

echo [3/5] Cleaning temporary files...
if exist "*.log" del /q "*.log"
if exist "*.tmp" del /q "*.tmp"
if exist "temp" rmdir /s /q "temp"
echo ✅ Temporary files cleaned

echo [4/5] Cleaning unused static files...
if exist "static\images\*.txt" del /q "static\images\*.txt"
if exist "static\images\placeholder.*" del /q "static\images\placeholder.*"
echo ✅ Unused static files cleaned

echo [5/5] Cleaning development files...
if exist ".DS_Store" del /q ".DS_Store"
for /r . %%f in (.DS_Store) do if exist "%%f" del /q "%%f"
echo ✅ Development files cleaned

echo.
echo ========================================
echo    Cleanup Complete!
echo ========================================
echo.
echo 📁 Project size reduced
echo 🚀 System optimized
echo ✨ Ready for deployment
echo.
echo Press any key to continue...
pause >nul
