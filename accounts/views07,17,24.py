from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer, ProfileEduDetailsSerializer, ProfileFamilyDetailsSerializer, ProfilePartnerPrefSerializer
from rest_framework import viewsets
from .models import Country, ProfileEduDetails, ProfileFamilyDetails, ProfilePartnerPref, State, District, Religion, Caste, ProfileHolder, MaritalStatus, Height, Complexion, ParentsOccupation, HighestEducation, UgDegree, AnnualIncome, PlaceOfBirth, BirthStar, Rasi, Lagnam, DasaBalance, FamilyType, FamilyStatus, FamilyValue, LoginDetailsTemp
from .serializers import CountrySerializer, StateSerializer, DistrictSerializer, ReligionSerializer, CasteSerializer, ProfileHolderSerializer, MaritalStatusSerializer, HeightSerializer, ComplexionSerializer, ParentsOccupationSerializer, HighestEducationSerializer, UgDegreeSerializer, AnnualIncomeSerializer, PlaceOfBirthSerializer, BirthStarSerializer, RasiSerializer, LagnamSerializer, DasaBalanceSerializer, FamilyTypeSerializer, FamilyStatusSerializer, FamilyValueSerializer, LoginDetailsTempSerializer
from rest_framework.decorators import action

class SignInView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            return Response({'message': 'Success'}, status=status.HTTP_200_OK)
        return Response({'message': 'Failed'}, status=status.HTTP_401_UNAUTHORIZED)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password successfully changed'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

class ReligionViewSet(viewsets.ModelViewSet):
    queryset = Religion.objects.all()
    serializer_class = ReligionSerializer

class CasteViewSet(viewsets.ModelViewSet):
    queryset = Caste.objects.all()
    serializer_class = CasteSerializer

class ProfileHolderViewSet(viewsets.ModelViewSet):
    queryset = ProfileHolder.objects.all()
    serializer_class = ProfileHolderSerializer

class MaritalStatusViewSet(viewsets.ModelViewSet):
    queryset = MaritalStatus.objects.all()
    serializer_class = MaritalStatusSerializer

class HeightViewSet(viewsets.ModelViewSet):
    queryset = Height.objects.all()
    serializer_class = HeightSerializer

class ComplexionViewSet(viewsets.ModelViewSet):
    queryset = Complexion.objects.all()
    serializer_class = ComplexionSerializer

class ParentsOccupationViewSet(viewsets.ModelViewSet):
    queryset = ParentsOccupation.objects.all()
    serializer_class = ParentsOccupationSerializer

class HighestEducationViewSet(viewsets.ModelViewSet):
    queryset = HighestEducation.objects.all()
    serializer_class = HighestEducationSerializer

class UgDegreeViewSet(viewsets.ModelViewSet):
    queryset = UgDegree.objects.all()
    serializer_class = UgDegreeSerializer

class AnnualIncomeViewSet(viewsets.ModelViewSet):
    queryset = AnnualIncome.objects.all()
    serializer_class = AnnualIncomeSerializer

class PlaceOfBirthViewSet(viewsets.ModelViewSet):
    queryset = PlaceOfBirth.objects.all()
    serializer_class = PlaceOfBirthSerializer

class BirthStarViewSet(viewsets.ModelViewSet):
    queryset = BirthStar.objects.all()
    serializer_class = BirthStarSerializer

class RasiViewSet(viewsets.ModelViewSet):
    queryset = Rasi.objects.all()
    serializer_class = RasiSerializer

class LagnamViewSet(viewsets.ModelViewSet):
    queryset = Lagnam.objects.all()
    serializer_class = LagnamSerializer

class DasaBalanceViewSet(viewsets.ModelViewSet):
    queryset = DasaBalance.objects.all()
    serializer_class = DasaBalanceSerializer

class FamilyTypeViewSet(viewsets.ModelViewSet):
    queryset = FamilyType.objects.all()
    serializer_class = FamilyTypeSerializer

class FamilyStatusViewSet(viewsets.ModelViewSet):
    queryset = FamilyStatus.objects.all()
    serializer_class = FamilyStatusSerializer

class FamilyValueViewSet(viewsets.ModelViewSet):
    queryset = FamilyValue.objects.all()
    serializer_class = FamilyValueSerializer
# views.py
from rest_framework import viewsets
from .models import LoginDetailsTemp
from .serializers import LoginDetailsTempSerializer

class LoginDetailsTempViewSet(viewsets.ModelViewSet):
    queryset = LoginDetailsTemp.objects.all()
    serializer_class = LoginDetailsTempSerializer

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        login_detail = self.get_object()
        login_detail.status = 1
        last_profile = LoginDetailsTemp.objects.filter(ProfileId__regex=r'^vy\d{3}$').order_by('ProfileId').last()
        if last_profile:
            last_serial_number = int(last_profile.ProfileId[2:])
            new_serial_number = last_serial_number + 1
        else:
            new_serial_number = 1
        login_detail.ProfileId = f'vy{new_serial_number:03}'
        login_detail.save()
        return Response({'status': 'accepted', 'ProfileId': login_detail.ProfileId})

    @action(detail=True, methods=['patch'])
    def disapprove(self, request, pk=None):
        login_detail = self.get_object()
        login_detail.status = 0
        login_detail.save()
        return Response({'status': 'disapproved'})
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer

@api_view(['POST'])
def basic_details(request):
    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import LoginDetails
from .serializers import LoginDetailsSerializer
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class LoginDetailsViewSet(viewsets.ModelViewSet):
    queryset = LoginDetails.objects.all()
    serializer_class = LoginDetailsSerializer

    def generate_unique_profile_id(self):
        last_profile = LoginDetails.objects.filter(ProfileId__regex=r'^vy240\d{3}$').order_by('ProfileId').last()
        if last_profile:
            last_serial_number = int(last_profile.ProfileId[5:])
            new_serial_number = last_serial_number + 1
        else:
            new_serial_number = 1
        return f'vy240{new_serial_number:03}'

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        retries = 5  # Number of retries to find a unique ProfileId
        for attempt in range(retries):
            profile_id = self.generate_unique_profile_id()
            if not LoginDetails.objects.filter(ProfileId=profile_id).exists():
                request.data['ProfileId'] = profile_id
                serializer = self.get_serializer(data=request.data)
                try:
                    serializer.is_valid(raise_exception=True)
                    self.perform_create(serializer)
                    headers = self.get_success_headers(serializer.data)
                    return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                except Exception as e:
                    logger.error(f"Error creating login details: {e}")
            logger.warning(f"Attempt {attempt + 1}: ProfileId {profile_id} already exists. Retrying...")
        logger.error("Could not generate a unique ProfileId after multiple attempts.")
        return Response({'error': 'Could not generate a unique ProfileId'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileFamilyDetailsViewSet(viewsets.ModelViewSet):
    queryset = ProfileFamilyDetails.objects.all()
    serializer_class = ProfileFamilyDetailsSerializer

class ProfileEduDetailsViewSet(viewsets.ModelViewSet):
    queryset = ProfileEduDetails.objects.all()
    serializer_class = ProfileEduDetailsSerializer

class ProfilePartnerPrefViewSet(viewsets.ModelViewSet):
    queryset = ProfilePartnerPref.objects.all()
    serializer_class = ProfilePartnerPrefSerializer
