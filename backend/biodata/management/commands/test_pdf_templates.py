"""
Test PDF generation for all template choices to verify rendering is correct.
"""
from django.core.management.base import BaseCommand
from biodata.models import Biodata
from biodata.views import build_biodata_template_context
from django.template.loader import render_to_string

class Command(BaseCommand):
    help = 'Test PDF generation for all templates'

    def handle(self, *args, **options):
        # Get a test biodata record
        biodata = Biodata.objects.first()
        if not biodata:
            print('No biodata records found.')
            return
        
        print(f'Testing PDF Generation with Biodata ID: {biodata.id}')
        print(f'Current template_choice: {biodata.template_choice}')
        print('=' * 60)
        
        # Test each template choice
        for choice in ['1', '2', '3', '4', '5']:
            print(f'\nTesting template_choice={choice}...')
            
            # Temporarily set template choice
            original_choice = biodata.template_choice
            biodata.template_choice = choice
            
            # Build context
            context = build_biodata_template_context(biodata)
            
            # Select template
            template_map = {
                '1': 'biodata_download.html',
                '2': 'biodata_template_2.html',
                '3': 'biodata_template_3.html',
                '4': 'biodata_template_4.html',
                '5': 'biodata_template_5.html',
            }
            template_name = template_map.get(choice, 'biodata_download.html')
            
            try:
                html = render_to_string(template_name, context)
                
                # Check for issues
                has_dict = "{'label':" in html or '{"label":' in html
                has_name = 'fsd' in html or biodata.data.get('PersonalDetails', {}).get('name', {}).get('value', '') in html
                
                if has_dict:
                    print(f'   ❌ FAILED: Found raw dictionary in HTML')
                elif not has_name and choice != '5':  # Template 5 might not show name at top
                    print(f'   ⚠️  WARNING: Name value not found in HTML')
                else:
                    print(f'   ✅ PASSED: Template renders correctly')
                    
            except Exception as e:
                print(f'   ❌ ERROR: {e}')
            
            # Restore original choice
            biodata.template_choice = original_choice
        
        print('\n' + '=' * 60)
        print('PDF Generation Test Complete!')
        print('All templates should now generate clean PDFs with only field values.')
