from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

        Evidence.objects.create(complaint=complaint, **serializer.validated_data)
        return Response({"detail": "Evidence added"}, status=201)

    @action(detail=True, methods=["post"], permission_classes=[IsOversightOrAdmin])
    def status(self, request, pk=None):
        complaint = self.get_object()
        new_status = request.data.get("status")

        valid = {s for s, _ in Complaint.Status.choices}
        if new_status not in valid:
            return Response({"detail": "Invalid status"}, status=400)

        complaint.status = new_status
        complaint.save(update_fields=["status", "updated_at"])
        return Response({"detail": "Status updated", "status": complaint.status})