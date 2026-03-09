from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import get_object_or_404

signer = TimestampSigner()

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    # Optional fields
    first_name = request.data.get('first_name', '')
    phone = request.data.get('phone', '') # Not storing phone in default User, assuming Profile or ignore for now? 
    # Current Signup.js sends 'phone'. User model doesn't have phone. 
    # If the user wants to store phone, we need a Profile model or similar.
    # For now, I'll ignore phone or store it strictly if there is a place. 
    # The previous code didn't store phone/fullname properly except in kwargs which create_user might accept but User model only has first_name/last_name.
    
    if not username or not password or not email:
        return Response({'detail': 'Username, password, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(username=username).exists():
        return Response({'detail': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
    if User.objects.filter(email=email).exists():
        return Response({'detail': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
        # By default is_active is True for create_user, but we confirm just in case
        user.is_active = True
        user.save()
        
    except Exception as e:
        if 'user' in locals():
            user.delete()
        return Response({'detail': f'Error creating user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'detail': 'User created successfully.', 'id': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    token = request.data.get('token')
    if not token:
        return Response({'detail': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        username = signer.unsign(token, max_age=3600*24) # 24 hours
        user = get_object_or_404(User, username=username)
        if user.is_active:
             return Response({'detail': 'User already verified.', 'status': 'already_verified'}, status=status.HTTP_200_OK)
             
        user.is_active = True
        user.save()
        return Response({'detail': 'Email verified successfully. You can now login.', 'status': 'success'}, status=status.HTTP_200_OK)
        
    except (BadSignature, SignatureExpired):
        return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
