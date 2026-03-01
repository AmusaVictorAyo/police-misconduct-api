from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from authorities.models import OversightAuthority
from .models import Complaint, Evidence
from .serializers import ComplaintSerializer, EvidenceSerializer
from .permissions import IsOwnerOrOversight, IsOversightOrAdmin


class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [IsOwnerOrOversight]

    # Week 3: enable filtering/search/ordering if you already added django-filter settings
    filterset_fields = ["status", "category", "authority"]
    search_fields = ["title", "description", "incident_location"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.profile, "role", "CITIZEN")

        qs = Complaint.objects.all().order_by("-created_at")

        # Citizen sees only their own complaints
        if role == "CITIZEN":
            return qs.filter(user=user)

        # Oversight/Admin sees all (Week 3/4 can restrict by authority later)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def evidence(self, request, pk=None):
        """
        Add evidence metadata to a complaint.
        Body: {"type": "LINK", "url": "https://...", "description": "optional"}
        """
        complaint = self.get_object()

        serializer = EvidenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Evidence.objects.create(
            complaint=complaint,
            **serializer.validated_data
        )

        return Response({"detail": "Evidence added"}, status=201)

    @action(detail=True, methods=["post"], permission_classes=[IsOversightOrAdmin])
    def status(self, request, pk=None):
        """
        Update complaint status (oversight/admin only).
        Body: {"status": "PENDING"} etc.
        """
        complaint = self.get_object()
        new_status = request.data.get("status")

        # NEW RULE: cannot change status after CLOSED
        if complaint.status == Complaint.Status.CLOSED:
            return Response(
                {"detail": "Closed complaints cannot be reopened in MVP"},
                status=400
            )

        valid = {s for s, _ in Complaint.Status.choices}
        if new_status not in valid:
            return Response({"detail": "Invalid status"}, status=400)

        complaint.status = new_status
        complaint.save(update_fields=["status", "updated_at"])

        return Response({"detail": "Status updated", "status": complaint.status})

    @action(detail=True, methods=["post"], permission_classes=[IsOversightOrAdmin])
    def route(self, request, pk=None):
        """
        Assign complaint to an oversight authority (oversight/admin only).
        Body: {"authority_id": 1}
        """
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