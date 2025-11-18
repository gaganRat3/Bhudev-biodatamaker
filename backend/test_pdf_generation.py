#!/usr/bin/env python
"""
Test script to verify PDF generation with border images
Run this from the backend directory: python test_pdf_generation.py
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

def test_pdf_generation():
    """Test PDF generation with border images"""
    print("=== Testing PDF Generation with Border Images ===")
    
    # Get the first biodata record or create a test one
    try:
        biodata = Biodata.objects.first()
        if not biodata:
            print("No biodata records found. Creating a test record...")
            biodata = Biodata.objects.create(
                title="Test Biodata",
                user_name="Test User",
                user_email="test@example.com",
                template_choice="4",
                data={
                    "PersonalDetails": {
                        "name": "Test User",
                        "age": "25",
                        "height": "5'8\"",
                        "occupation": "Software Engineer"
                    },
                    "FamilyDetails": {
                        "father_name": "Test Father",
                        "mother_name": "Test Mother"
                    },
                    "HabitsDeclaration": {
                        "smoking": "No",
                        "drinking": "No"
                    }
                }
            )
            print(f"Created test biodata with ID: {biodata.id}")
    except Exception as e:
        print(f"Error accessing biodata: {e}")
        return
    
    # Test template rendering for template 4
    template_name = "biodata_template_4.html"
    
    # Construct the border image path correctly
    border_image = "bg8.jpg"
    border_path = os.path.join(settings.BASE_DIR.parent, 'assets', 'border', border_image)
    print(f"Border image path: {border_path}")
    print(f"Border image exists: {os.path.exists(border_path)}")
    
    # Use file:// URL for xhtml2pdf to find the image
    border_url = f"file:///{border_path.replace(os.sep, '/')}"
    print(f"Border URL for PDF: {border_url}")
    
    try:
        # Render the HTML template
        context = {
            'biodata': biodata,
            'border_image_path': border_url
        }
        html = render_to_string(template_name, context)
        print(f"Template rendered successfully. HTML length: {len(html)} characters")
        
        # Check if border image path is in the HTML
        if 'bg8.jpg' in html:
            print("✓ Border image reference found in HTML")
        else:
            print("✗ Border image reference NOT found in HTML")
        
        # Generate PDF
        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        
        if pisa_status.err:
            print(f"✗ PDF generation failed with errors: {pisa_status.err}")
        else:
            pdf_size = len(pdf_buffer.getvalue())
            print(f"✓ PDF generated successfully. Size: {pdf_size} bytes")
            
            # Save PDF for inspection
            pdf_path = os.path.join(backend_dir, f"test_biodata_{biodata.id}.pdf")
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            print(f"✓ PDF saved to: {pdf_path}")
            
    except Exception as e:
        print(f"✗ Error during PDF generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()