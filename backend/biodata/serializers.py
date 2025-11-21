from rest_framework import serializers
from .models import Biodata
import json




class BiodataSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        # Auto-approve free biodata (template_choice == 1 or '1')
        template_choice = validated_data.get('template_choice')
        if str(template_choice) == '1' or template_choice == 1:
            validated_data['is_approved'] = True
        return super().create(validated_data)

    class Meta:
        model = Biodata
        fields = (
            'id', 'title', 'data', 'profile_image', 'payment_screenshot',
            'template_choice', 'user_name', 'user_email', 'user_phone',
            'is_approved', 'download_link',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'is_approved', 'download_link', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        """Normalize incoming multipart data into plain dict and parse data JSON.

        When using multipart/form-data, DRF provides a QueryDict which stores values as
        strings. Assigning a Python dict back into a QueryDict can break validation for
        JSONField (it expects a real dict). We therefore build a plain dict and parse
        the `data` field if it is a JSON string.
        Additionally, ensure all biodata fields are always {label, value} objects for consistency.
        """
        import copy
        incoming = {}
        for key in ('title', 'profile_image', 'payment_screenshot', 'data', 'template_choice', 'user_name', 'user_email', 'user_phone'):
            if key in data:
                incoming[key] = data.get(key)

        raw = incoming.get('data')
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode('utf-8', errors='ignore')

        if isinstance(raw, str):
            try:
                incoming['data'] = json.loads(raw)
            except Exception:
                pass

        # --- PERMANENT FIX: ensure all fields are {label, value} objects ---
        def normalize_section(section):
            if not isinstance(section, dict):
                return section
            result = {}
            for k, v in section.items():
                # If already {label, value}, keep as is
                if isinstance(v, dict) and 'label' in v and 'value' in v:
                    result[k] = v
                # If plain string, wrap as {label, value}
                elif isinstance(v, str):
                    result[k] = {'label': k.replace('_', ' ').title(), 'value': v}
                # If dict but not {label, value}, flatten
                elif isinstance(v, dict):
                    label = v.get('label', k.replace('_', ' ').title())
                    value = v.get('value', '')
                    result[k] = {'label': label, 'value': value}
                else:
                    result[k] = {'label': k.replace('_', ' ').title(), 'value': str(v)}
            return result

        if 'data' in incoming and isinstance(incoming['data'], dict):
            d = copy.deepcopy(incoming['data'])
            for section in ['PersonalDetails', 'FamilyDetails', 'HabitsDeclaration']:
                if section in d:
                    d[section] = normalize_section(d[section])
            incoming['data'] = d

        return super().to_internal_value(incoming)
