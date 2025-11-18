# Email Quick Fix - TL;DR

## Problem
Emails not sending because Gmail App Password was hardcoded and might be expired/incorrect.

## Quick Fix (5 minutes)

### Step 1: Get Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Generate new App Password
3. Copy the 16-character code

### Step 2: Set Environment Variable (PowerShell)
```powershell
cd backend
$env:EMAIL_HOST_PASSWORD="your-app-password-here"
python test_email_config.py
```

### Step 3: If Test Passes, Start Server
```powershell
python manage.py runserver
```

## Alternative: Automated Setup
```powershell
cd backend
.\setup_email.ps1
```

This script will:
- Create .env file
- Guide you through entering credentials
- Test email configuration
- Start the server

## Files Created
- ✅ `test_email_config.py` - Diagnostic tool
- ✅ `setup_email.ps1` - Automated setup
- ✅ `.env.example` - Configuration template
- ✅ `EMAIL_SETUP_GUIDE.md` - Full documentation

## Changes Made to Existing Files
- ✅ `settings.py` - Removed hardcoded password, added validation

## Test Commands
```bash
# Test email configuration
python test_email_config.py

# Send test email
python manage.py send_test_email --to=your-email@example.com

# Start server
python manage.py runserver
```

## Still Not Working?
Read: `EMAIL_SETUP_GUIDE.md` for detailed troubleshooting
