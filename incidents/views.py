from rest_framework.viewsets import ModelViewSet
from .models import Incident
from .serializers import IncidentSerializer

class IncidentViewSet(ModelViewSet):
    queryset = Incident.objects.all().order_by("-created_at")
    serializer_class = IncidentSerializer