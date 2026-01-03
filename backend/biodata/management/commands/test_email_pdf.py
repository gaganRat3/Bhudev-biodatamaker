"""
Test email PDF generation to verify it uses .value correctly
"""
from django.core.management.base import BaseCommand
from biodata.models import Biodata
from biodata.admin import BiodataAdmin
from django.contrib.admin.sites import site

class Command(BaseCommand):
    help = 'Test email PDF HTML generation'

    def handle(self, *args, **options):
        biodata = Biodata.objects.first()
        if not biodata:
            print('No biodata records found.')
            return
        
        print(f'Testing Email PDF HTML Generation with Biodata ID: {biodata.id}')
        print('=' * 60)
        
        admin = BiodataAdmin(Biodata, site)
        
        # Test HTML generation
        print('\nGenerating email PDF HTML...')
        try:
            html = admin.build_frontend_html(biodata)
            
            # Check for issues
            has_dict = "{'label':" in html or '{"label":' in html
            has_value = biodata.data.get('PersonalDetails', {}).get('name', {}).get('value', '') in html
            
            if has_dict:
                print('   ❌ FAILED: Found raw dictionary in email PDF HTML')
                # Show a snippet
                import re
                matches = re.findall(r"\{'label':[^}]+\}", html)
                if matches:
                    print(f'   Example: {matches[0][:100]}...')
            else:
                print('   ✅ PASSED: No raw dictionaries found')
                
            if has_value:
                print('   ✅ PASSED: Field value found in HTML')
            else:
                print('   ⚠️  WARNING: Field value not found in HTML')
                
        except Exception as e:
            print(f'   ❌ ERROR: {e}')
            import traceback
            traceback.print_exc()
        
        print('\n' + '=' * 60)
        print('Email PDF HTML Generation Test Complete!')
