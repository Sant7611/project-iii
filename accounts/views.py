from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .utils.decorators import token_required
from django.contrib.auth import login, logout
from accounts.models import APIToken
from rest_framework import viewsets

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
        
        exist = User.objects.filter(email__iexact=email).exists()
        if exist:
            return JsonResponse({'error':'user with email already exists..'},status=400)
        
        exist = User.objects.filter(username__iexact=username).exists()
        if exist:
            return JsonResponse({'error':'user with username already exists..'},status=400)
        

        user = User.objects.create_user(username=username, email=email, password =password)
        user.bio = bio
        user.save()
        token = APIToken.objects.create(user=user)
        
        return JsonResponse({'user':{
            'is_authenticated':user.is_authenticated,
            "username":user.username,
            'email':user.email,
            'bio':user.bio,
            'token':f'Token {token.token}'
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

@csrf_exempt
@token_required
def test_decorator(request):
    if request.method == 'GET':
        return JsonResponse({'message': 'test decorator succeeded.' , 'user':request.user.username})

@csrf_exempt
@token_required
def user_logout(request):
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization', '')
        parts = auth_header.split()
        if len(parts) != 2:
            return JsonResponse({'error': 'Invalid authorization header'}, status=401) 
        token_str = parts[1]
        APIToken.objects.filter(token=token_str).delete()
        return JsonResponse({'message':f'{request.user.username} logged out'})
    return JsonResponse({'error':'method not allowed'}, status=401)

# class RegisterView(viewsets.ModelViewSet):
#     queryset = User.objects.all()
