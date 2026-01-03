from django.core.management.base import BaseCommand
from biodata.models import Biodata
import json

class Command(BaseCommand):
    help = 'Check normalization of biodata records (fields as {label, value})'

    def handle(self, *args, **options):
        qs = Biodata.objects.all()[:20]
        for obj in qs:
            print(f'ID: {obj.id}')
            data = obj.data
            for section in ['PersonalDetails', 'FamilyDetails', 'HabitsDeclaration']:
                section_data = data.get(section, {})
                print(f'  {section}:')
                for key, value in section_data.items():
                    if isinstance(value, dict) and 'value' in value:
                        print(f'    {key}: OK (label={value.get('label')}, value={value.get('value')})')
                    else:
                        print(f'    {key}: NOT NORMALIZED (raw={value})')
            print('-' * 40)
        print('Done. If you see any NOT NORMALIZED lines, those records need fixing.')
