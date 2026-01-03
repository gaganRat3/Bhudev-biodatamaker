"""Test biodata creation with profile image upload"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biodata_project.settings')
django.setup()

import json
from django.core.files.uploadedfile import SimpleUploadedFile
from biodata.models import Biodata
from biodata.serializers import BiodataSerializer

# Get a sample image from the profiles folder
media_profiles = os.path.join(os.path.dirname(__file__), 'media', 'profiles')
image_files = [f for f in os.listdir(media_profiles) if f.endswith('.jpg')]
if not image_files:
    print("No test images found in media/profiles")
    exit(1)

sample_image_path = os.path.join(media_profiles, image_files[0])
print(f"Using test image: {sample_image_path}")

# Create test data
test_data = {
    'PersonalDetails': {
        'name': {'label': 'Name', 'value': 'Test User'},
        'date_of_birth': {'label': 'Birth Date', 'value': '1990-01-01'},
    },
    'FamilyDetails': {
        'father_name': {'label': 'Father Name', 'value': 'Father Test'},
    },
    'HabitsDeclaration': {}
}

# Read the image file
with open(sample_image_path, 'rb') as f:
    image_data = f.read()

# Create uploaded file
uploaded_file = SimpleUploadedFile(
    name='test_profile.jpg',
    content=image_data,
    content_type='image/jpeg'
)

# Create biodata with serializer
serializer_data = {
    'data': json.dumps(test_data),
    'profile_image': uploaded_file,
    'template_choice': '1',
    'user_name': 'Test User',
    'user_email': 'test@example.com',
}

serializer = BiodataSerializer(data=serializer_data)
if serializer.is_valid():
    biodata = serializer.save()
    print(f"\n✓ Biodata created successfully!")
    print(f"  ID: {biodata.pk}")
    print(f"  Profile Image: {biodata.profile_image}")
    print(f"  Profile Image Name: {biodata.profile_image.name if biodata.profile_image else 'None'}")
    print(f"  Profile Image URL: {biodata.profile_image.url if biodata.profile_image else 'None'}")
    
    # Verify file exists
    if biodata.profile_image:
        from django.conf import settings
        full_path = os.path.join(settings.MEDIA_ROOT, biodata.profile_image.name)
        print(f"  File exists: {os.path.exists(full_path)}")
        print(f"  Full path: {full_path}")
else:
    print(f"\n✗ Serializer validation failed:")
    print(serializer.errors)
