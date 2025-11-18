#!/usr/bin/env python
"""
Simple test to generate PDF and check content display
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biodata_project.settings')
django.setup()

from django.template.loader import render_to_string
from biodata.models import Biodata
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
import base64

def test_simple_pdf():
    """Test simple PDF generation to check content display"""
    print("=== Simple PDF Test ===")
    
    # Get or create test biodata
    biodata, created = Biodata.objects.get_or_create(
        template_choice="4",
        defaults={
            'title': "Test PDF",
            'user_name': "John Doe",
            'user_email': "test@example.com",
            'data': {
                "PersonalDetails": {
                    "name": "John Doe",
                    "age": "28",
                    "height": "5'10\"",
                    "occupation": "Software Engineer"
                },
                "FamilyDetails": {
                    "father_name": "Mr. Father",
                    "mother_name": "Mrs. Mother"
                },
                "HabitsDeclaration": {
                    "smoking": "No",
                    "drinking": "No"
                }
            }
        }
    )
    
    # Prepare border image as data URI
    border_path = os.path.join(settings.BASE_DIR.parent, 'assets', 'border', 'bg8.jpg')
    print(f"Border path: {border_path}")
    print(f"Border exists: {os.path.exists(border_path)}")
    
    border_data_uri = None
    if os.path.exists(border_path):
        with open(border_path, 'rb') as f:
            b64_data = base64.b64encode(f.read()).decode('ascii')
            border_data_uri = f"data:image/jpeg;base64,{b64_data}"
        print(f"Border data URI length: {len(border_data_uri)}")
    
    # Render template
    context = {
        'biodata': biodata,
        'border_image_path': border_data_uri if border_data_uri else '/assets/border/bg8.jpg'
    }
    
    html = render_to_string('biodata_template_4.html', context)
    print(f"HTML length: {len(html)}")
    
    # Save HTML for inspection
    with open('debug_template.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ HTML saved to debug_template.html")
    
    # Generate PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    
    if pisa_status.err:
        print(f"✗ PDF errors: {pisa_status.err}")
    else:
        pdf_size = len(pdf_buffer.getvalue())
        print(f"✓ PDF size: {pdf_size} bytes")
        
        # Save PDF
        with open('debug_template.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        print("✓ PDF saved to debug_template.pdf")

if __name__ == "__main__":
    test_simple_pdf()