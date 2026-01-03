#!/usr/bin/env python
"""Test email sending with PDF attachment"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biodata_project.settings')
django.setup()

from biodata.models import Biodata, Payment
from biodata.admin import PaymentAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory

def test_email_with_pdf():
    # Get a payment with biodata
    payment = Payment.objects.filter(biodata__isnull=False).first()
    if not payment:
        print("❌ No payment found with biodata")
        return False
    
    biodata = payment.biodata
    print(f"Testing email for Payment {payment.pk}")
    print(f"Biodata: {biodata.pk} - {biodata.user_name}")
    print(f"Email: {biodata.user_email}")
    print(f"Template: {biodata.template_choice}")
    
    # Approve the payment first
    payment.is_approved = True
    payment.save()
    print(f"✅ Payment marked as approved")
    
    # Create admin and request context
    site = AdminSite()
    admin = PaymentAdmin(Payment, site)
    factory = RequestFactory()
    request = factory.get('/admin/')
    request.user = User.objects.filter(is_superuser=True).first()
    
    # Create queryset
    from django.db.models import QuerySet
    queryset = Payment.objects.filter(pk=payment.pk)
    
    try:
        print("\n🔄 Sending approval email with PDF...")
        admin.send_approval_email(request, queryset)
        print("✅ Email sending process completed!")
        print("📧 Check the console output above for email status")
        return True
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_email_with_pdf()
    sys.exit(0 if success else 1)
