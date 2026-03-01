from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from authorities.models import OversightAuthority
from complaints.models import Complaint

User = get_user_model()


class ReviewerPackTests(APITestCase):
    def setUp(self):
        # Users
        self.citizen = User.objects.create_user(username="citizen", password="pass12345", email="c@test.com")
        self.oversight = User.objects.create_user(username="oversight", password="pass12345", email="o@test.com")

        # Set roles (profile created by signals)
        self.citizen.profile.role = "CITIZEN"
        self.citizen.profile.save()

        self.oversight.profile.role = "OVERSIGHT"
        self.oversight.profile.save()

        # Authority
        self.authority = OversightAuthority.objects.create(
            name="Lagos Oversight Office",
            region="Lagos",
            contact_email="lagos@example.com",
        )

    def login_token(self, username, password):
        res = self.client.post("/api/auth/login/", {"username": username, "password": password}, format="json")
        self.assertEqual(res.status_code, 200)
        token = res.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def create_complaint_as_citizen(self):
        self.login_token("citizen", "pass12345")
        res = self.client.post(
            "/api/complaints/",
            {
                "title": "Checkpoint incident",
                "description": "Officer demanded money.",
                "incident_date": "2026-02-28",
                "incident_location": "Lagos",
                "category": "EXTORTION",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        return res.data["id"]

    # ✅ auth register/login
    def test_auth_register_and_login(self):
        res = self.client.post(
            "/api/auth/register/",
            {"username": "newuser", "email": "new@test.com", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)

        res2 = self.client.post(
            "/api/auth/login/",
            {"username": "newuser", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(res2.status_code, 200)
        self.assertIn("token", res2.data)

    # ✅ citizen create complaint
    def test_citizen_can_create_complaint(self):
        complaint_id = self.create_complaint_as_citizen()
        self.assertIsNotNone(complaint_id)

    # ✅ citizen sees only own
    def test_citizen_sees_only_own_complaints(self):
        # citizen creates one
        complaint_id = self.create_complaint_as_citizen()

        # another citizen creates another complaint
        other = User.objects.create_user(username="citizen2", password="pass12345")
        other.profile.role = "CITIZEN"
        other.profile.save()

        self.client.credentials()  # clear token
        self.login_token("citizen2", "pass12345")
        self.client.post(
            "/api/complaints/",
            {
                "title": "Different case",
                "description": "Something else.",
                "incident_date": "2026-02-28",
                "incident_location": "Abuja",
                "category": "OTHER",
            },
            format="json",
        )

        # citizen1 should see only theirs
        self.client.credentials()
        self.login_token("citizen", "pass12345")
        res = self.client.get("/api/complaints/")
        self.assertEqual(res.status_code, 200)

        returned_ids = [item["id"] for item in res.data]
        self.assertIn(complaint_id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    # ✅ evidence add works
    def test_add_evidence_works(self):
        complaint_id = self.create_complaint_as_citizen()

        res = self.client.post(
            f"/api/complaints/{complaint_id}/evidence/",
            {"type": "LINK", "url": "https://example.com/video", "description": "clip"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)

    # ✅ oversight status update works
    def test_oversight_can_update_status(self):
        complaint_id = self.create_complaint_as_citizen()

        self.client.credentials()
        self.login_token("oversight", "pass12345")

        res = self.client.post(
            f"/api/complaints/{complaint_id}/status/",
            {"status": "PENDING"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get("status"), "PENDING")

    # ✅ citizen cannot status update
    def test_citizen_cannot_update_status(self):
        complaint_id = self.create_complaint_as_citizen()

        # citizen tries to change status
        res = self.client.post(
            f"/api/complaints/{complaint_id}/status/",
            {"status": "PENDING"},
            format="json",
        )
        self.assertIn(res.status_code, [403, 401])

    # ✅ routing works
    def test_oversight_can_route_complaint(self):
        complaint_id = self.create_complaint_as_citizen()

        self.client.credentials()
        self.login_token("oversight", "pass12345")

        res = self.client.post(
            f"/api/complaints/{complaint_id}/route/",
            {"authority_id": self.authority.id},
            format="json",
        )
        self.assertEqual(res.status_code, 200)

        # confirm DB updated
        c = Complaint.objects.get(id=complaint_id)
        self.assertIsNotNone(c.authority)
        self.assertEqual(c.authority.id, self.authority.id)