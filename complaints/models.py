from django.conf import settings
from django.db import models
from authorities.models import OversightAuthority


class Complaint(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        RECEIVED = "RECEIVED", "Received"
        PENDING = "PENDING", "Pending"
        CLOSED = "CLOSED", "Closed"

    class Category(models.TextChoices):
        BRIBERY = "BRIBERY", "Bribery"
        ASSAULT = "ASSAULT", "Assault"
        HARASSMENT = "HARASSMENT", "Harassment"
        WRONGFUL_ARREST = "WRONGFUL_ARREST", "Wrongful Arrest"
        EXTORTION = "EXTORTION", "Extortion"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="complaints")
    authority = models.ForeignKey(
        OversightAuthority, on_delete=models.SET_NULL, null=True, blank=True, related_name="complaints"
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    incident_date = models.DateField()
    incident_location = models.CharField(max_length=255)

    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


class Evidence(models.Model):
    class EvidenceType(models.TextChoices):
        VIDEO = "VIDEO", "Video"
        IMAGE = "IMAGE", "Image"
        DOCUMENT = "DOCUMENT", "Document"
        LINK = "LINK", "Link"

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="evidence")
    type = models.CharField(max_length=20, choices=EvidenceType.choices, default=EvidenceType.LINK)
    url = models.URLField()
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} evidence for complaint {self.complaint_id}"