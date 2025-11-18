@echo off
REM Email Configuration Setup Script for Windows
REM This script helps you set up email environment variables

echo ========================================
echo  Biodata Project - Email Setup
echo ========================================
echo.

REM Check if .env file exists
if exist .env (
    echo Found existing .env file
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 goto :skip_env
)

echo Creating .env file...
copy .env.example .env
echo.
echo ✓ Created .env file
echo.
echo IMPORTANT: Edit the .env file and add your Gmail App Password!
echo.
echo Steps:
echo 1. Open .env file in a text editor
echo 2. Replace "xxxx xxxx xxxx xxxx" with your actual App Password
echo 3. Save the file
echo.
echo To generate App Password:
echo   → https://myaccount.google.com/apppasswords
echo.

:skip_env

echo ========================================
echo Testing Email Configuration
echo ========================================
echo.

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to PATH
    goto :end
)

echo Running diagnostic test...
echo.
python test_email_config.py

echo.
echo ========================================
echo  Setup Complete
echo ========================================
echo.
echo Next steps:
echo 1. If tests failed, edit .env file with correct credentials
echo 2. Run: python manage.py runserver
echo 3. Test admin approval flow at http://localhost:8000/admin/
echo.

:end
pause
