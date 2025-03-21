from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

class LoginView(APIView):
    # If you're using DRF's @api_view or class-based views, these can handle CSRF internally.
    # However, make sure that CSRF is handled appropriately if accessed from a non-Django frontend.
    authentication_classes = []  # This disables session and basic authentication
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # Using request.POST to correctly handle form-data
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        print('User : ',user)


        if user:
            return Response({'message': 'Login Successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
