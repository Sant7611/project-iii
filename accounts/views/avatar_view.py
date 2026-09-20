from django.core.files.storage import default_storage
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from accounts.models import Profile
from utils.response_helper import error_response, success_response


class ProfileAvatarView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    max_size = 5 * 1024 * 1024

    def patch(self, request):
        image = request.FILES.get("avatar")
        if not image:
            return error_response(message="No avatar provided", status=400)

        if image.content_type not in self.allowed_types:
            return error_response(
                message="Only JPEG, PNG and WebP profile images are allowed",
                status=400,
            )

        if image.size > self.max_size:
            return error_response(
                message="Profile image size should be less than 5MB",
                status=400,
            )

        profile, _ = Profile.objects.get_or_create(user=request.user)
        old_name = profile.avatar.name if profile.avatar else ""

        profile.avatar = image
        profile.save(update_fields=["avatar"])

        if old_name and old_name != profile.avatar.name:
            try:
                default_storage.delete(old_name)
            except Exception:
                pass

        return success_response(
            message="Profile image updated",
            data={"avatar": profile.avatar.url if profile.avatar else None},
            status=200,
        )

    def delete(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        old_name = profile.avatar.name if profile.avatar else ""

        profile.avatar = ""
        profile.save(update_fields=["avatar"])

        if old_name:
            try:
                default_storage.delete(old_name)
            except Exception:
                pass

        return success_response(
            message="Profile image removed",
            data={"avatar": None},
            status=200,
        )
