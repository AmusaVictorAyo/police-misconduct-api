from django.db import models


class OversightAuthority(models.Model):
    name = models.CharField(max_length=200)
    region = models.CharField(max_length=200)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.region})"