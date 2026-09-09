import os

from django.conf import settings
from django.test import SimpleTestCase
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


class DeployConfigTests(SimpleTestCase):
    def test_deployment_security_and_static_settings_are_ready_for_vercel(self):
        self.assertEqual(settings.STATIC_URL, "/static/")
        self.assertEqual(settings.STATIC_ROOT.name, "staticfiles")
        self.assertEqual(settings.SECURE_PROXY_SSL_HEADER, ("HTTP_X_FORWARDED_PROTO", "https"))
        self.assertTrue(settings.USE_X_FORWARDED_HOST)

        secure_redirect = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "false").lower() == "true"
        session_secure = os.getenv("DJANGO_SESSION_COOKIE_SECURE", "false").lower() == "true"
        csrf_secure = os.getenv("DJANGO_CSRF_COOKIE_SECURE", "false").lower() == "true"

        self.assertEqual(settings.SECURE_SSL_REDIRECT, secure_redirect)
        self.assertEqual(settings.SESSION_COOKIE_SECURE, session_secure)
        self.assertEqual(settings.CSRF_COOKIE_SECURE, csrf_secure)
        self.assertTrue(any("whatbytess.vercel.app" in origin for origin in settings.CSRF_TRUSTED_ORIGINS))
