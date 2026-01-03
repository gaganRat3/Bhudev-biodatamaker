#!/usr/bin/env python
"""Test PDF generation with server URL approach"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biodata_project.settings')
django.setup()

from biodata.models import Biodata, Payment
from biodata.admin import PaymentAdmin
from django.contrib.admin.sites import AdminSite

def test_pdf_generation():
    # Get a biodata to test
    biodata = Biodata.objects.first()
    if not biodata:
        print("❌ No biodata found in database")
        return
    
    print(f"Testing PDF generation for Biodata {biodata.pk}")
    print(f"Template choice: {biodata.template_choice}")
    print(f"User: {biodata.user_name}")
    
    # Create admin instance
    site = AdminSite()
    admin = PaymentAdmin(Payment, site)
    
    try:
        print("\n🔄 Generating PDF from server URL...")
        pdf_buffer = admin._html_to_pdf(biodata)
        pdf_size = len(pdf_buffer.getvalue())
        print(f"✅ PDF generated successfully!")
        print(f"📄 PDF size: {pdf_size:,} bytes")
        
        # Save for inspection
        output_path = f"test_biodata_{biodata.pk}.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        print(f"💾 Saved to: {output_path}")
        
        return True
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
