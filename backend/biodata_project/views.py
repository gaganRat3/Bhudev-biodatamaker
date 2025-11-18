from django.http import HttpResponse
from django.conf import settings
from pathlib import Path
import os

def serve_static_html(request, template_name):
    """
    Serve static HTML files without Django template processing
    """
    # Construct the path to the HTML file
    frontend_root = Path(settings.BASE_DIR).parent
    html_file_path = frontend_root / template_name
    
    # Check if file exists
    if not html_file_path.exists():
        return HttpResponse("File not found", status=404)
    
    # Read and return the file content as-is
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    return HttpResponse(content, content_type='text/html')