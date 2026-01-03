from django.core.management.base import BaseCommand
from biodata.models import Biodata
from biodata.views import build_biodata_template_context
import json

class Command(BaseCommand):
    help = 'Debug biodata context to see what is passed to the template'

    def handle(self, *args, **options):
        biodata = Biodata.objects.first()
        if not biodata:
            print('No biodata records found.')
            return
        
        print(f'Biodata ID: {biodata.id}')
        print('\n=== Raw Database Data ===')
        print(json.dumps(biodata.data, indent=2))
        
        print('\n=== Context Built for Template ===')
        context = build_biodata_template_context(biodata)
        
        print(f'\nBorder Image Path: {context["border_image_path"]}')
        print(f'Profile Image Path: {context["profile_image_path"]}')
        
        print('\n=== Personal Left ===')
        for key, value in context['personal_left']:
            print(f'  Key: {key}')
            print(f'  Value Type: {type(value)}')
            print(f'  Value: {value}')
            if isinstance(value, dict):
                print(f'    .label: {value.get("label")}')
                print(f'    .value: {value.get("value")}')
        
        print('\n=== Personal Right ===')
        for key, value in context['personal_right']:
            print(f'  Key: {key}')
            print(f'  Value Type: {type(value)}')
            print(f'  Value: {value}')
            if isinstance(value, dict):
                print(f'    .label: {value.get("label")}')
                print(f'    .value: {value.get("value")}')
