from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Profile, User


class ProfileAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="profile-user",
            email="profile@example.com",
            password="test-password",
        )
        self.url = reverse("my-profile")

    def test_profile_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_returns_authenticated_user(self):
        Profile.objects.create(user=self.user, bio="Original bio")
        self.client.force_authenticate(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["profile"]["bio"], "Original bio")

    def test_patch_updates_user_and_creates_missing_profile(self):
        self.client.force_authenticate(self.user)

        response = self.client.patch(
            self.url,
            {
                "first_name": "Updated",
                "profile": {"bio": "New bio", "address": "Kathmandu"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.bio, "New bio")
        self.assertEqual(profile.address, "Kathmandu")

    def test_put_is_not_allowed(self):
        self.client.force_authenticate(self.user)

        response = self.client.put(self.url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
