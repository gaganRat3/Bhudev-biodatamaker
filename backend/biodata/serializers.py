from rest_framework import serializers
from .models import Biodata
import json



class BiodataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biodata
        fields = (
            'id', 'title', 'data', 'profile_image',
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
        """
        # Extract only fields we care about into a plain dict
        incoming = {}
        # include fields that may be submitted from the frontend when requesting premium downloads
        for key in ('title', 'profile_image', 'data', 'template_choice', 'user_name', 'user_email', 'user_phone'):
            if key in data:
                incoming[key] = data.get(key)

        raw = incoming.get('data')
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode('utf-8', errors='ignore')

        if isinstance(raw, str):
            try:
                incoming['data'] = json.loads(raw)
            except Exception:
                # Keep as string; JSONField will raise a clear error which our client surfaces
                pass

        return super().to_internal_value(incoming)
