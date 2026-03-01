from rest_framework import viewsets, permissions
from .models import OversightAuthority
from .serializers import OversightAuthoritySerializer

class OversightAuthorityViewSet(viewsets.ModelViewSet):
    queryset = OversightAuthority.objects.all()
    serializer_class = OversightAuthoritySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]