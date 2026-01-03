"""
Test script to verify biodata rendering is fixed.
This will generate test HTML for all templates to verify .value is displayed correctly.
"""
from django.core.management.base import BaseCommand
from biodata.models import Biodata
from biodata.views import build_biodata_template_context
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Test biodata template rendering to verify only values are displayed, not full objects'

    def handle(self, *args, **options):
        biodata = Biodata.objects.first()
        if not biodata:
            print('No biodata records found.')
            return
        
        print(f'Testing with Biodata ID: {biodata.id}')
        print('=' * 60)
        
        context = build_biodata_template_context(biodata)
        
        # Test main download template
        print('\n1. Testing biodata_download.html...')
        try:
            html = render_to_string("biodata_download.html", context)
            # Check for dictionary patterns that shouldn't be in output
            if "{'label':" in html or '{"label":' in html:
                print('   ❌ FAILED: Found raw dictionary objects in HTML')
            else:
                print('   ✅ PASSED: No raw dictionary objects found')
        except Exception as e:
            print(f'   ❌ ERROR: {e}')
        
        # Test other templates (2-5)
        for i in range(2, 6):
            template_name = f"biodata_template_{i}.html"
            print(f'\n{i}. Testing {template_name}...')
            try:
                html = render_to_string(template_name, context)
                if "{'label':" in html or '{"label":' in html:
                    print(f'   ❌ FAILED: Found raw dictionary objects in HTML')
                else:
                    print(f'   ✅ PASSED: No raw dictionary objects found')
            except Exception as e:
                print(f'   ❌ ERROR: {e}')
        
        print('\n' + '=' * 60)
        print('Testing complete!')
        print('\nIf all tests passed, your templates will display only values.')
        print('If any failed, check the template file for {{ value }} instead of {{ value.value }}')
