from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from authorities.models import OversightAuthority
from complaints.models import Complaint

User = get_user_model()


class ComplaintWeek3Tests(APITestCase):
    def setUp(self):
        # Create users
        self.citizen = User.objects.create_user(username="citizen", password="pass12345")
        self.oversight = User.objects.create_user(username="oversight", password="pass12345")

        # Set roles (because profile is created by signal)
        self.citizen.profile.role = "CITIZEN"
        self.citizen.profile.save()

        self.oversight.profile.role = "OVERSIGHT"
        self.oversight.profile.save()

        # Create an authority (so we can route complaints)
        self.authority = OversightAuthority.objects.create(
            name="Lagos Oversight Office",
            region="Lagos",
            contact_email="lagos@example.com",
        )

        # Create a complaint owned by citizen
        self.complaint = Complaint.objects.create(
            user=self.citizen,
            title="Checkpoint incident",
            description="Officer demanded money.",
            incident_date="2026-02-28",
            incident_location="Lagos",
            category="EXTORTION",
            status="SUBMITTED",
        )

    def login_and_set_token(self, username, password):
        res = self.client.post(
            "/api/auth/login/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        token = res.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_route_endpoint_works_for_oversight(self):
        # Oversight logs in
        self.login_and_set_token("oversight", "pass12345")

        # Route the complaint to an authority
        res = self.client.post(
            f"/api/complaints/{self.complaint.id}/route/",
            {"authority_id": self.authority.id},
            format="json",
        )
        self.assertEqual(res.status_code, 200)

        # Refresh from DB and confirm authority assigned
        self.complaint.refresh_from_db()
        self.assertIsNotNone(self.complaint.authority)
        self.assertEqual(self.complaint.authority.id, self.authority.id)

    def test_citizen_cannot_route(self):
        # Citizen logs in
        self.login_and_set_token("citizen", "pass12345")

        # Citizen tries to route (should fail)
        res = self.client.post(
            f"/api/complaints/{self.complaint.id}/route/",
            {"authority_id": self.authority.id},
            format="json",
        )
        self.assertIn(res.status_code, [403, 401])  # depending on your permission setup

    def test_status_cannot_be_updated_after_closed(self):
        # Close the complaint first using DB (simulate a case already closed)
        self.complaint.status = "CLOSED"
        self.complaint.save()

        # Oversight logs in
        self.login_and_set_token("oversight", "pass12345")

        # Try to change status after closed (should return 400)
        res = self.client.post(
            f"/api/complaints/{self.complaint.id}/status/",
            {"status": "PENDING"},
            format="json",
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data.get("detail"), "Closed complaints cannot be reopened in MVP")