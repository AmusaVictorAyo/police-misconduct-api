from rest_framework.test import APITestCase


class AuthTests(APITestCase):

    def test_register_and_login(self):
        res = self.client.post("/api/auth/register/", {
            "username": "victor",
            "email": "victor@test.com",
            "password": "pass12345"
        }, format="json")

        self.assertEqual(res.status_code, 201)

        res2 = self.client.post("/api/auth/login/", {
            "username": "victor",
            "password": "pass12345"
        }, format="json")

        self.assertEqual(res2.status_code, 200)
        self.assertIn("token", res2.data)