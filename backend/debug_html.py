#!/usr/bin/env python
"""
Debug script to check HTML output with border image
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

def debug_html_output():
    """Debug HTML output to see if border image is correctly referenced"""
    print("=== Debugging HTML Output ===")
    
    # Get test biodata
    biodata = Biodata.objects.first()
    if not biodata:
        print("No biodata found")
        return
    
    # Construct border image path
    border_image = "bg8.jpg"
    border_path = os.path.join(settings.BASE_DIR.parent, 'assets', 'border', border_image)
    border_url = f"file:///{border_path.replace(os.sep, '/')}"
    
    print(f"Border path: {border_path}")
    print(f"Border exists: {os.path.exists(border_path)}")
    print(f"Border URL: {border_url}")
    
    # Render template
    context = {
        'biodata': biodata,
        'border_image_path': border_url
    }
    html = render_to_string('biodata_template_4.html', context)
    
    # Save HTML for inspection
    html_file = os.path.join(backend_dir, 'debug_output.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML saved to: {html_file}")
    print("\n=== HTML Content ===")
    print(html)

if __name__ == "__main__":
    debug_html_output()