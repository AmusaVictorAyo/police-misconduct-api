from rest_framework import serializers
from .models import OversightAuthority

class OversightAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = OversightAuthority
        fields = ["id", "name", "region", "contact_email"]