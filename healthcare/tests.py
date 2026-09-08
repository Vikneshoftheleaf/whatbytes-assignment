from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User


class AuthenticationTests(APITestCase):
    def test_user_can_register_and_login(self):
        response = self.client.post(reverse("register"), {"name": "Test User", "email": "test@example.com", "password": "strong-password-123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse("token_obtain_pair"), {"email": "test@example.com", "password": "strong-password-123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class PatientAccessTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", name="Owner", password="strong-password-123")
        self.client.force_authenticate(self.user)

    def test_authenticated_user_can_create_and_list_own_patients(self):
        payload = {"name": "Jane Doe", "date_of_birth": "1990-01-01", "gender": "female", "contact": "555-0100", "address": "1 Main St"}
        response = self.client.post("/api/patients/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
