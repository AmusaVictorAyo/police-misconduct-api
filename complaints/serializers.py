from rest_framework import serializers
from .models import Complaint, Evidence

class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ["id", "type", "url", "description", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]

class ComplaintSerializer(serializers.ModelSerializer):
    evidence = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = Complaint
        fields = [
            "id",
            "user",
            "authority",
            "title",
            "description",
            "incident_date",
            "incident_location",
            "category",
            "status",
            "created_at",
            "updated_at",
            "evidence",
        ]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]