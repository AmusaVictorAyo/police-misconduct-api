from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()

class ComplaintTests(APITestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass12345")
        self.u2 = User.objects.create_user(username="u2", password="pass12345")

    def login(self, username, password):
        res = self.client.post("/api/auth/login/", {"username": username, "password": password}, format="json")
        token = res.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_citizen_can_create_complaint(self):
        self.login("u1", "pass12345")
        res = self.client.post("/api/complaints/", {
            "title": "Checkpoint issue",
            "description": "Officer demanded money.",
            "incident_date": "2026-02-28",
            "incident_location": "Lagos",
            "category": "EXTORTION"
        }, format="json")
        self.assertEqual(res.status_code, 201)

    def test_citizen_sees_only_own_complaints(self):
        self.login("u1", "pass12345")
        self.client.post("/api/complaints/", {
            "title": "Case 1",
            "description": "desc",
            "incident_date": "2026-02-28",
            "incident_location": "Lagos",
            "category": "OTHER"
        }, format="json")

        self.client.credentials()  # clear auth
        self.login("u2", "pass12345")
        res = self.client.get("/api/complaints/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)