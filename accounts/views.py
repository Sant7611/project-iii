from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()
# Create your views here.
@csrf_exempt
def register(request, uname=None):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        email = data.get('email', '')
        password = data.get('password', '')
        bio = data.get('bio', '').strip()
        if not username or not email or not password:
            return JsonResponse({'error':'selected fields cannot be empty'}, status=400)

        try:
            validate_password(password)
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({'error': list(e.messages)}, status=400)
        
        exist = User.objects.filter(email=email).exists()
        if exist:
            return JsonResponse({'error':'user with email already exists..'},status=400)
        
        exist = User.objects.filter(username=username).exists()
        if exist:
            return JsonResponse({'error':'user with username already exists..'},status=400)

        user = User.objects.create_user(username=username, email=email, password =password)
        user.bio = bio
        user.save()
        return JsonResponse({'user':{
            "username":user.username,
            'email':user.email,
            'bio':user.bio
        }}, status=201)
    
    elif request.method =='GET':
        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            return JsonResponse({'error':'User not found'}, status=404)
        
        user_detail = {
            'id':user.id,
            'username':user.username,
            'email':user.email,
            'bio':user.bio
        }
        
        return JsonResponse({'user':user_detail})
    return JsonResponse({'error':'method not allowed'}, status=405)