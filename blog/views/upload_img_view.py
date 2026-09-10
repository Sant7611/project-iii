from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.conf import settings
from utils.response_helper import success_response, error_response
import uuid
import os

class ImageUploadView(APIView):
    """
    Upload an image and return its public URL.
    Used by the rich text editor for inline images.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image = request.FILES.get('image')

        if not image:
            return error_response(message="No image provided", status=400)

        # Optional: basic validation
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if image.content_type not in allowed_types:
            return error_response(
                message="Only JPEG, PNG, WebP and GIF images are allowed",
                status=400
            )

        # Limit size (e.g. 5 MB)
        if image.size > 5 * 1024 * 1024:
            return error_response(message="Image size should be less than 5MB", status=400)

 
        # Save the file
        import cloudinary.uploader

        upload_result = cloudinary.uploader.upload(
            image,
            folder="uploads",
            public_id=uuid.uuid4().hex,
            resource_type="image",
            secure=True,
        )

        image_url = upload_result["secure_url"]

        return success_response(
            message="Image uploaded successfully",
            data={"url": image_url},
            status=201
        )