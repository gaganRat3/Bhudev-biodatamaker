from django.core.management.base import BaseCommand
from biodata.models import Biodata

class Command(BaseCommand):
    help = 'Fix legacy biodata records to ensure all fields are normalized as {label, value}'

    def handle(self, *args, **options):
        import ast
        updated = 0
        qs = Biodata.objects.all()
        for obj in qs:
            data = obj.data
            changed = False
            for section in ['PersonalDetails', 'FamilyDetails', 'HabitsDeclaration']:
                section_data = data.get(section, {})
                for key, value in list(section_data.items()):
                    # If value is a string that looks like a dict, parse it
                    if isinstance(value, str) and value.strip().startswith('{') and value.strip().endswith('}'):
                        try:
                            parsed = ast.literal_eval(value)
                            value = parsed
                        except Exception:
                            pass
                    # If not normalized, convert
                    if not (isinstance(value, dict) and 'value' in value):
                        section_data[key] = {'label': key.replace('_', ' ').title(), 'value': value}
                        changed = True
                    else:
                        section_data[key] = value
                data[section] = section_data
            if changed:
                obj.data = data
                obj.save()
                updated += 1
        print(f'Updated {updated} legacy records (including stringified dicts).')
        print('Done. All records should now be normalized.')
