import base64
from rest_framework import serializers
from django.core.files.base import ContentFile

class Base64BinaryField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            # Handle data URI (e.g., "data:image/jpeg;base64,...")
            if data.startswith("data:"):
                _, data = data.split(";base64,", 1)
            try:
                return base64.b64decode(data)
            except Exception as e:
                raise serializers.ValidationError("Invalid base64-encoded data")
        raise serializers.ValidationError("Expected base64-encoded string")

    def to_representation(self, value):
        # Optional: encode the binary data back to base64 string in response
        if value is not None:
            return base64.b64encode(value).decode('utf-8')
        return None
