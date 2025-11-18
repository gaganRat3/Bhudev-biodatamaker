# Email Configuration Setup Script for Windows PowerShell
# Run this script from the backend directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Biodata Project - Email Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "Found existing .env file" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/n)"
    if ($overwrite -ne "y") {
        Write-Host "Keeping existing .env file" -ForegroundColor Green
    } else {
        Copy-Item ".env.example" ".env" -Force
        Write-Host "✓ Created new .env file" -ForegroundColor Green
    }
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Gmail App Password Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: You need a Gmail App Password!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Steps to get App Password:" -ForegroundColor White
Write-Host "  1. Enable 2-Factor Authentication on your Gmail" -ForegroundColor Gray
Write-Host "     → https://myaccount.google.com/security" -ForegroundColor Gray
Write-Host "  2. Generate App Password" -ForegroundColor Gray
Write-Host "     → https://myaccount.google.com/apppasswords" -ForegroundColor Gray
Write-Host "  3. Copy the 16-character password" -ForegroundColor Gray
Write-Host ""

$setupMethod = Read-Host "Choose setup method: [1] Edit .env file manually  [2] Enter credentials now (1 or 2)"

if ($setupMethod -eq "2") {
    Write-Host ""
    $email = Read-Host "Enter your Gmail address"
    Write-Host "Enter your Gmail App Password (input will be hidden):" -ForegroundColor Yellow
    $password = Read-Host -AsSecureString
    $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    )
    
    # Update .env file
    $envContent = Get-Content ".env"
    $envContent = $envContent -replace "EMAIL_HOST_USER=.*", "EMAIL_HOST_USER=$email"
    $envContent = $envContent -replace "EMAIL_HOST_PASSWORD=.*", "EMAIL_HOST_PASSWORD=$passwordPlain"
    $envContent = $envContent -replace "DEFAULT_FROM_EMAIL=.*", "DEFAULT_FROM_EMAIL=$email"
    $envContent | Set-Content ".env"
    
    Write-Host "✓ Updated .env file with your credentials" -ForegroundColor Green
    
    # Also set environment variables for current session
    $env:EMAIL_HOST_USER = $email
    $env:EMAIL_HOST_PASSWORD = $passwordPlain
    $env:DEFAULT_FROM_EMAIL = $email
    
    Write-Host "✓ Set environment variables for current session" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Please edit the .env file and add your credentials:" -ForegroundColor Yellow
    Write-Host "  - Replace 'your-email@gmail.com' with your Gmail" -ForegroundColor Gray
    Write-Host "  - Replace 'xxxx xxxx xxxx xxxx' with your App Password" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Press Enter when done, or type 'skip' to skip testing"
    if ($continue -eq "skip") {
        Write-Host "Skipping tests. Run 'python test_email_config.py' manually later." -ForegroundColor Yellow
        exit
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Testing Email Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python or add it to PATH" -ForegroundColor Yellow
    pause
    exit
}

# Run diagnostic test
Write-Host ""
Write-Host "Running diagnostic test..." -ForegroundColor Cyan
Write-Host ""

python test_email_config.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Setup Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. If tests failed, check .env file credentials" -ForegroundColor Gray
Write-Host "  2. Start server: python manage.py runserver" -ForegroundColor Gray
Write-Host "  3. Test admin approval at http://localhost:8000/admin/" -ForegroundColor Gray
Write-Host ""

# Ask if user wants to start the server
$startServer = Read-Host "Do you want to start the Django server now? (y/n)"
if ($startServer -eq "y") {
    Write-Host ""
    Write-Host "Starting Django server..." -ForegroundColor Green
    python manage.py runserver
}
