#!/usr/bin/env python
"""
Test all 6 templates to ensure they work correctly
Run this from the backend directory: python test_all_templates.py
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
import base64, mimetypes

def test_all_templates():
    """Test PDF generation for all 6 templates"""
    print("=== Testing All 6 Templates ===")
    
    # Get or create a test biodata record
    try:
        biodata = Biodata.objects.filter(user_name="Test All Templates").first()
        if not biodata:
            biodata = Biodata.objects.create(
                title="Test All Templates",
                user_name="Test All Templates User",
                user_email="test@example.com",
                template_choice="1",  # We'll change this for each test
                data={
                    "PersonalDetails": {
                        "name": "John Doe",
                        "age": "28",
                        "height": "5'10\"",
                        "occupation": "Software Engineer",
                        "education": "B.Tech Computer Science",
                        "location": "Mumbai"
                    },
                    "FamilyDetails": {
                        "father_name": "Mr. Father Name",
                        "mother_name": "Mrs. Mother Name",
                        "family_income": "5 LPA",
                        "siblings": "1 Brother"
                    },
                    "HabitsDeclaration": {
                        "smoking": "No",
                        "drinking": "Occasionally",
                        "diet": "Vegetarian",
                        "hobbies": "Reading"
                    }
                }
            )
            print(f"Created test biodata with ID: {biodata.id}")
    except Exception as e:
        print(f"Error creating/accessing biodata: {e}")
        return
    
    # Template mapping from admin.py
    template_map = {
        "1": ("biodata_download.html", "White.png"),
        "2": ("biodata_template_2.html", "bg0.png"),
        "3": ("biodata_template_3.html", "bg6.png"),
        "4": ("biodata_template_4.html", "bg8.jpg"),
        "5": ("biodata_template_5.html", "bg9.jpg"),
        "6": ("biodata_template_6.html", "bg10.jpg"),
    }
    
    # Function to split data into left/right columns
    def split_data_for_columns(data_dict):
        if not data_dict:
            return [], []
        items = [(k, v) for k, v in data_dict.items() if v and str(v).strip()]
        mid = len(items) // 2
        return items[:mid], items[mid:]
    
    for template_id, (template_name, border_image) in template_map.items():
        print(f"\n--- Testing Template {template_id} ({template_name}) ---")
        
        try:
            # Create context with static file path for PDF generation
            border_path = os.path.join(settings.BASE_DIR.parent, 'assets', 'border', border_image)
            border_url = f"file:///{border_path.replace(os.sep, '/')}"
            
            # Try to embed the border image as a data URI
            border_data_uri = None
            try:
                if os.path.exists(border_path):
                    with open(border_path, 'rb') as bf:
                        b = bf.read()
                    mime, _ = mimetypes.guess_type(border_path)
                    if not mime:
                        mime = 'image/jpeg'
                    b64 = base64.b64encode(b).decode('ascii')
                    border_data_uri = f"data:{mime};base64,{b64}"
                    print(f"  ✓ Border image embedded as data URI (size: {len(b)} bytes)")
            except Exception:
                border_data_uri = None
                print(f"  ⚠ Could not embed border image, using file path")
            
            # Prepare split data for columns (for templates that need it)
            personal_left, personal_right = split_data_for_columns(biodata.data.get('PersonalDetails', {}))
            family_left, family_right = split_data_for_columns(biodata.data.get('FamilyDetails', {}))
            habits_left, habits_right = split_data_for_columns(biodata.data.get('HabitsDeclaration', {}))
            
            context = {
                'biodata': biodata,
                'border_image_path': border_data_uri if border_data_uri else border_url,
                'profile_image_path': None,  # We can add this if needed
                'personal_left': personal_left,
                'personal_right': personal_right,
                'family_left': family_left,
                'family_right': family_right,
                'habits_left': habits_left,
                'habits_right': habits_right,
            }
            
            # Render the HTML template
            html = render_to_string(template_name, context)
            print(f"  ✓ Template rendered successfully. HTML length: {len(html)} characters")
            
            # Generate PDF
            pdf_buffer = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
            
            if pisa_status.err:
                print(f"  ✗ PDF generation failed with errors")
                for error in pisa_status.err:
                    print(f"    Error: {error}")
            else:
                pdf_size = len(pdf_buffer.getvalue())
                print(f"  ✓ PDF generated successfully. Size: {pdf_size} bytes")
                
                # Save PDF for inspection
                pdf_path = os.path.join(backend_dir, f"test_template_{template_id}.pdf")
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                print(f"  ✓ PDF saved to: {pdf_path}")
                
        except Exception as e:
            print(f"  ✗ Error testing template {template_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n=== Template Testing Complete ===")

if __name__ == "__main__":
    test_all_templates()