# Email Configuration Setup Guide

## Problem: Email Not Working

The email functionality wasn't working because:
1. **Hardcoded App Password** was directly in `settings.py` (security risk)
2. **No proper validation** to check if credentials are set
3. **Missing diagnostic tools** to test email configuration
4. **App Password might be expired or incorrect**

## Permanent Solution

### Step 1: Generate Gmail App Password

Since you're using Gmail (`bhudevnetwork@gmail.com`), you need an **App Password**:

1. **Enable 2-Factor Authentication** on your Gmail account
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or Other)
   - Click "Generate"
   - You'll get a 16-character password like: `abcd efgh ijkl mnop`

3. **Copy this password** (you'll need it in the next step)

### Step 2: Set Environment Variables

#### Option A: Windows PowerShell (Current Session)
```powershell
# Navigate to backend directory
cd backend

# Set environment variables
$env:EMAIL_HOST_PASSWORD="abcd efgh ijkl mnop"  # Replace with YOUR App Password
$env:EMAIL_HOST_USER="bhudevnetwork@gmail.com"
$env:DEFAULT_FROM_EMAIL="bhudevnetwork@gmail.com"

# Run Django server
python manage.py runserver
```

#### Option B: Create .env File (Recommended)

1. Create `.env` file in `backend/` directory:
```bash
cd backend
copy .env.example .env
```

2. Edit `.env` file with your actual credentials:
```env
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=bhudevnetwork@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=bhudevnetwork@gmail.com
```

3. Install python-decouple (to read .env files):
```bash
pip install python-decouple
```

4. Update `settings.py` to use decouple (optional, but recommended):
```python
from decouple import config

EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
```

#### Option C: Windows System Environment Variables (Permanent)

1. Open **System Properties** → **Environment Variables**
2. Add new User/System variables:
   - `EMAIL_HOST_PASSWORD` = `your-app-password`
   - `EMAIL_HOST_USER` = `bhudevnetwork@gmail.com`
3. **Restart PowerShell and VS Code** for changes to take effect

### Step 3: Test Email Configuration

Run the diagnostic script:

```bash
cd backend
python test_email_config.py
```

This will:
- ✓ Check all Django email settings
- ✓ Test SMTP connection
- ✓ Attempt to send a test email
- ✓ Provide detailed error messages if anything fails

### Step 4: Test Management Command

```bash
cd backend
python manage.py send_test_email --to=your-email@example.com
```

### Step 5: Test Admin Approval Flow

1. Start Django server: `python manage.py runserver`
2. Go to: http://localhost:8000/admin/
3. Login with admin credentials
4. Go to Biodata section
5. Select a pending biodata entry
6. Choose "Approve selected biodata and send email" action
7. Check the recipient's email inbox

## Testing Without Gmail (Alternative)

If you want to test without sending real emails:

### Console Backend (Prints emails to terminal)
```bash
$env:DJANGO_EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend"
python manage.py runserver
```

Emails will print in the terminal instead of being sent.

### File Backend (Saves emails to files)
```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'
```

Emails will be saved as `.eml` files in `backend/sent_emails/`

## Common Issues & Solutions

### Issue 1: "SMTPAuthenticationError"
**Cause**: Wrong password or 2FA not enabled
**Solution**: 
- Generate a new App Password
- Make sure 2-Factor Authentication is enabled on Gmail

### Issue 2: "SMTPSenderRefused" 
**Cause**: Gmail blocking sign-in attempt
**Solution**:
- Check https://myaccount.google.com/notifications
- Allow the sign-in attempt
- Use App Password instead of regular password

### Issue 3: Environment variables not working
**Cause**: Variables not set in current session
**Solution**:
- Restart PowerShell/VS Code after setting system variables
- Or use .env file approach with python-decouple

### Issue 4: "Connection timeout"
**Cause**: Firewall or network blocking SMTP
**Solution**:
- Check firewall settings (allow port 587)
- Try different network/disable VPN
- Try port 465 with SSL instead of TLS

## Verification Checklist

- [ ] 2-Factor Authentication enabled on Gmail
- [ ] App Password generated
- [ ] Environment variable `EMAIL_HOST_PASSWORD` set
- [ ] Ran `test_email_config.py` successfully
- [ ] Test email received in inbox
- [ ] Admin approval email working

## Production Deployment

For production servers:

1. **Never commit passwords to git**
   - Add `.env` to `.gitignore`
   - Use environment variables on server

2. **Use a dedicated email service**
   - SendGrid (free tier: 100 emails/day)
   - Mailgun (free tier: 5000 emails/month)
   - Amazon SES (very cheap)

3. **Set proper error handling**
   - Already implemented in `admin.py` and `send_test_email.py`
   - Logs saved to `backend/logs/django.log`

## Support

If email still not working after following all steps:

1. Check `backend/logs/django.log` for detailed errors
2. Run `python test_email_config.py` and share output
3. Verify App Password is correct (regenerate if needed)
4. Check Gmail account for security alerts

## Files Modified

1. ✅ `backend/biodata_project/settings.py` - Removed hardcoded password, added validation
2. ✅ `backend/test_email_config.py` - NEW diagnostic script
3. ✅ `backend/.env.example` - NEW environment variables template
4. ✅ `backend/biodata/admin.py` - Already has proper error handling
5. ✅ `backend/biodata/management/commands/send_test_email.py` - Already has proper error handling

## Next Steps

1. **Set up environment variables** (choose Option A, B, or C above)
2. **Run test script**: `python test_email_config.py`
3. **Fix any issues** reported by the script
4. **Test actual email sending** via admin panel
5. **Consider using SendGrid/Mailgun** for production
