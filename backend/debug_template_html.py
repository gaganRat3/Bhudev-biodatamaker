#!/usr/bin/env python
"""
Debug script to see the actual HTML being generated for PDF
Run this from the backend directory: python debug_template_html.py
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
import base64, mimetypes

def debug_template_html():
    """Debug the actual HTML being generated"""
    print("=== Debugging Template HTML Generation ===")
    
    # Get or create a test biodata
    biodata = Biodata.objects.filter(template_choice="4").first()
    if not biodata:
        biodata = Biodata.objects.create(
            title="Debug Biodata",
            user_name="Debug User",
            user_email="debug@example.com",
            template_choice="4",
            data={
                "PersonalDetails": {
                    "name": "John Debug",
                    "age": "30",
                    "height": "6'0\"",
                    "occupation": "Developer"
                },
                "FamilyDetails": {
                    "father_name": "Father Debug",
                    "mother_name": "Mother Debug"
                },
                "HabitsDeclaration": {
                    "smoking": "No",
                    "drinking": "No"
                }
            }
        )
    
    # Use the same logic as admin.py
    template_name = "biodata_template_4.html"
    border_image = "bg8.jpg"
    border_path = os.path.join(settings.BASE_DIR.parent, 'assets', 'border', border_image)
    
    # Create data URI
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
            print(f"✓ Border data URI created, length: {len(border_data_uri)} chars")
    except Exception as e:
        print(f"✗ Error creating border data URI: {e}")
    
    context = {
        'biodata': biodata,
        'border_image_path': border_data_uri,
        'profile_image_path': None,
    }
    
    html = render_to_string(template_name, context)
    
    # Save HTML for inspection
    html_path = os.path.join(backend_dir, "debug_template.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML saved to: {html_path}")
    print(f"✓ HTML length: {len(html)} characters")
    
    # Check if content is in HTML
    if "John Debug" in html:
        print("✓ User name found in HTML")
    else:
        print("✗ User name NOT found in HTML")
    
    if "template-inner" in html:
        print("✓ template-inner wrapper found in HTML")
    else:
        print("✗ template-inner wrapper NOT found in HTML")
    
    if "Personal Details" in html:
        print("✓ Section headers found in HTML")
    else:
        print("✗ Section headers NOT found in HTML")
    
    # Show a snippet of the HTML around the content
    print("\n=== HTML Content Preview ===")
    start_idx = html.find('<h2 class="biodata-name">')
    if start_idx > -1:
        snippet = html[start_idx:start_idx+500]
        print(snippet)
    else:
        print("Could not find biodata-name in HTML")

if __name__ == "__main__":
    debug_template_html()