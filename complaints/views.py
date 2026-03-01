from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from authorities.models import OversightAuthority

from .models import Complaint, Evidence
from .serializers import ComplaintSerializer, EvidenceSerializer
from .permissions import IsOwnerOrOversight, IsOversightOrAdmin

class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [IsOwnerOrOversight]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", "CITIZEN")

        qs = Complaint.objects.all().order_by("-created_at")

        if role == "CITIZEN":
            return qs.filter(user=user)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def evidence(self, request, pk=None):
        complaint = self.get_object()
        serializer = EvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Evidence.objects.create(
            complaint=complaint,
            **serializer.validated_data
        )

        return Response({"detail": "Evidence added"}, status=201)

    @action(detail=True, methods=["post"], permission_classes=[IsOversightOrAdmin])
    def route(self, request, pk=None):
        complaint = self.get_object()
        authority_id = request.data.get("authority_id")

        if not authority_id:
            return Response({"detail": "authority_id is required"}, status=400)

        try:
            authority = OversightAuthority.objects.get(id=authority_id)
        except OversightAuthority.DoesNotExist:
            return Response({"detail": "Authority not found"}, status=404)

        complaint.authority = authority
        complaint.save(update_fields=["authority", "updated_at"])

        return Response({"detail": "Complaint routed", "authority": authority.id})