from django.contrib.auth.models import User  # Import the User model
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .models import AuthUser  # Assuming AuthUser is your user model
from rest_framework import status

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            auth_user = AuthUser.objects.get(username=username, password=password)
            user, created = User.objects.get_or_create(username=auth_user.username)
            if created:
                # Handle user creation logic if needed
                pass
            
            # Authentication successful, create token
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'status': 1,'token':token.key ,'message': 'Login Successful'}, status=200)
        except AuthUser.DoesNotExist:
            return JsonResponse({'status': 0, 'message': 'Invalid credentials'}, status=401)
        

class LogoutView(APIView):
    def post(self, request):
        # Get the token key from the request header or data
        token_key = request.POST.get('token_key', None)

        if token_key:
            # Retrieve the token object based on the token key
            try:
                token = Token.objects.get(key=token_key)
            except Token.DoesNotExist:
                return JsonResponse({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            # Delete the token from the database
            token.delete()
            return JsonResponse({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'message': 'Token key not provided'}, status=status.HTTP_400_BAD_REQUEST)