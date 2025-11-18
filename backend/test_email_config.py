#!/usr/bin/env python
"""
Comprehensive email configuration test script.
Run this from the backend directory: python test_email_config.py
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biodata_project.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_django_settings():
    """Check Django email settings"""
    print_section("1. Django Email Settings")
    
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Check if password is set
    if not settings.EMAIL_HOST_PASSWORD:
        print("\n⚠️  WARNING: EMAIL_HOST_PASSWORD is not set!")
        return False
    
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("\n⚠️  INFO: Using console backend - emails will print to console only")
        return True
        
    return True

def test_smtp_connection():
    """Test direct SMTP connection"""
    print_section("2. Testing Direct SMTP Connection")
    
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("Skipping SMTP test (console backend is active)")
        return True
    
    try:
        print(f"Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...")
        
        if settings.EMAIL_USE_TLS:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
        
        print("✓ Connected successfully")
        
        print(f"Logging in as {settings.EMAIL_HOST_USER}...")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print("✓ Authentication successful")
        
        server.quit()
        print("✓ SMTP connection test passed")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("\nCommon causes:")
        print("  1. Wrong email/password")
        print("  2. Gmail: Need to use App Password (not regular password)")
        print("  3. Gmail: Enable 'Less secure app access' or use App Password")
        return False
        
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        return False
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_django_send_mail():
    """Test Django's send_mail function"""
    print_section("3. Testing Django send_mail()")
    
    test_email = settings.EMAIL_HOST_USER
    print(f"Sending test email to: {test_email}")
    
    try:
        result = send_mail(
            subject='Test Email from Biodata Project',
            message='This is a test email. If you receive this, email configuration is working!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result == 1:
            print(f"✓ Email sent successfully!")
            print(f"  Check inbox: {test_email}")
            return True
        else:
            print(f"✗ send_mail returned {result} (expected 1)")
            return False
            
    except Exception as e:
        print(f"✗ Failed to send email: {e}")
        import traceback
        traceback.print_exc()
        return False

def diagnose_common_issues():
    """Provide diagnosis for common email issues"""
    print_section("4. Common Issues & Solutions")
    
    if settings.EMAIL_HOST == 'smtp.gmail.com':
        print("\n📧 Gmail Configuration:")
        print("   1. Enable 2-Factor Authentication on your Google account")
        print("   2. Generate an App Password:")
        print("      → https://myaccount.google.com/apppasswords")
        print("   3. Use the 16-character App Password (without spaces)")
        print("   4. Update settings.py: EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'")
        
    print("\n🔐 Security Checklist:")
    print("   □ Never commit passwords to git")
    print("   □ Use environment variables in production")
    print("   □ Consider using .env file for local development")
    
    print("\n🐛 Debugging Tips:")
    print("   1. Check Django logs: backend/logs/django.log")
    print("   2. Use console backend for testing:")
    print("      EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")
    print("   3. Test with a different email provider (SendGrid, Mailgun)")

def main():
    print("\n" + "="*60)
    print("  BIODATA PROJECT - EMAIL CONFIGURATION TEST")
    print("="*60)
    
    results = {
        'settings': test_django_settings(),
        'smtp': test_smtp_connection(),
        'send_mail': test_django_send_mail(),
    }
    
    diagnose_common_issues()
    
    print_section("Summary")
    print(f"Settings Check: {'✓ PASS' if results['settings'] else '✗ FAIL'}")
    print(f"SMTP Connection: {'✓ PASS' if results['smtp'] else '✗ FAIL'}")
    print(f"Django send_mail: {'✓ PASS' if results['send_mail'] else '✗ FAIL'}")
    
    if all(results.values()):
        print("\n🎉 All tests passed! Email is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Review the output above for fixes.")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
