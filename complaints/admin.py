from django.contrib import admin
from .models import Complaint, Evidence

admin.site.register(Complaint)
admin.site.register(Evidence)