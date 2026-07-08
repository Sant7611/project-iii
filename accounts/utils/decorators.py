from django.contrib.auth import get_user_model
from accounts.models import APIToken
from django.http import JsonResponse

User = get_user_model()


def token_required(func):
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != "Token":
            return JsonResponse({"error": "token required"}, status=401)
        token = parts[1]
        try:
            token_obj = APIToken.objects.select_related("user").get(token=token)
            request.user = token_obj.user
        except APIToken.DoesNotExist:
            return JsonResponse({"error": "Invalid Token Unauthorized"}, status=401)

        return func(request, *args, **kwargs)

    return wrapper
