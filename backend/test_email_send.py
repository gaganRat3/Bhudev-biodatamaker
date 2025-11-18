#!/usr/bin/env python
"""
Test script to verify email sending with PDF attachment
Run this from the backend directory: python test_email_send.py
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

from django.contrib.admin.sites import site
from biodata.models import Biodata
from biodata.admin import BiodataAdmin
from django.http import HttpRequest
from django.contrib.auth.models import User

def test_email_send():
    """Test email sending with PDF attachment"""
    print("=== Testing Email Send with PDF Attachment ===")
    
    # Get or create a test biodata record
    try:
        biodata = Biodata.objects.filter(template_choice="4").first()
        if not biodata:
            biodata = Biodata.objects.create(
                title="Test Biodata for Email",
                user_name="Test User",
                user_email="test@example.com",  # Replace with your email for testing
                user_phone="1234567890",
                template_choice="4",
                data={
                    "PersonalDetails": {
                        "name": "John Doe",
                        "age": "28",
                        "height": "5'10\"",
                        "occupation": "Software Engineer",
                        "education": "B.Tech Computer Science"
                    },
                    "FamilyDetails": {
                        "father_name": "Mr. Father Name",
                        "mother_name": "Mrs. Mother Name",
                        "family_income": "5 LPA"
                    },
                    "HabitsDeclaration": {
                        "smoking": "No",
                        "drinking": "Occasionally",
                        "diet": "Vegetarian"
                    }
                },
                is_approved=False
            )
            print(f"Created test biodata with ID: {biodata.id}")
        else:
            print(f"Using existing biodata with ID: {biodata.id}")
    except Exception as e:
        print(f"Error creating/accessing biodata: {e}")
        return
    
    # Create a mock request object
    request = HttpRequest()
    request.user = User.objects.filter(is_superuser=True).first()
    if not request.user:
        print("No superuser found. Creating one...")
        request.user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    # Ensure build_absolute_uri works in tests (provide host and scheme)
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.META['SERVER_NAME'] = 'localhost'
    request.META['SERVER_PORT'] = '8000'
    request.META['wsgi.url_scheme'] = 'http'
    # Use cookie storage (no session requirement) for messages
    from django.contrib.messages.storage.cookie import CookieStorage
    request._messages = CookieStorage(request)
    
    # Create admin instance
    admin = BiodataAdmin(Biodata, site)
    
    # Create queryset
    queryset = Biodata.objects.filter(id=biodata.id)
    
    try:
        print(f"Attempting to send email to: {biodata.user_email}")
        
        # Call the approve_biodata action
        admin.approve_biodata(request, queryset)
        
        print("✓ Email send process completed!")
        print("Check the terminal output above for success/error messages")
        
    except Exception as e:
        print(f"✗ Error during email send: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_email_send()