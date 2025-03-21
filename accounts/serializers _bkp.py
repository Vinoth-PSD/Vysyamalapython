# serializers.py
from rest_framework import serializers

from accounts.models import ProfileHoroscope
from .models import BirthStar, ProfilePartnerPref, Rasi, Lagnam, DasaBalance, LoginDetailsTemp, FamilyType, FamilyStatus, FamilyValue, ProfileHolder, MaritalStatus, Height, Complexion, ParentsOccupation, HighestEducation, UgDegree, AnnualIncome, Country, State, District , Mode , Property , Gothram , EducationLevel , Profession , Match , MasterStatePref , AdminUser , Role , ProfileHoroscope
from .models import Profile



class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
        fields = '__all__'

class ProfileHoroscopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileHoroscope
        fields = '__all__'

    
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'  # Or list specific fields



class GothramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gothram
        fields = '__all__'  # You can customize which fields you want to expose


class EducationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationLevel
        fields = '__all__'  # Expose all fields or customize to your needs


class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class MasterStatePrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterStatePref
        fields = ['id', 'state', 'is_deleted']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New password and confirm password do not match")
        return data

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class ProfileHolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileHolder
        fields = '__all__'

class MaritalStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaritalStatus
        fields = '__all__'

class HeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Height
        fields = '__all__'

class ComplexionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complexion
        fields = '__all__'

class ParentsOccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentsOccupation
        fields = '__all__'

class HighestEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HighestEducation
        fields = '__all__'

class UgDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UgDegree
        fields = '__all__'

class AnnualIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnualIncome
        fields = '__all__'

class BirthStarSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthStar
        fields = '__all__'

class RasiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rasi
        fields = '__all__'

class LagnamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lagnam
        fields = '__all__'

class DasaBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DasaBalance
        fields = '__all__'

class FamilyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyType
        fields = '__all__'

class FamilyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyStatus
        fields = '__all__'

class FamilyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyValue
        fields = '__all__'

class LoginDetailsTempSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginDetailsTemp
        fields = '__all__'
from rest_framework import serializers


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

from .models import LoginDetails, ProfileFamilyDetails, ProfileEduDetails

class LoginDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginDetails
        fields = '__all__'

class ProfileFamilyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileFamilyDetails
        fields = '__all__'

class ProfileEduDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileEduDetails
        fields = '__all__'

class ProfilePartnerPrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePartnerPref
        fields = '__all__'

class Getnewprofiledata(serializers.ModelSerializer):
    class Meta:
        model = LoginDetails
        fields = '__all__' 
        
        
        
from rest_framework import viewsets
from .models import ProfilePartnerPref
from .serializers import ProfilePartnerPrefSerializer

class ProfilePartnerPrefViewSet(viewsets.ModelViewSet):
    queryset = ProfilePartnerPref.objects.all()
    serializer_class = ProfilePartnerPrefSerializer

        
from rest_framework import serializers
from .models import Page
from .models import AdminSettings,AdminUser, Role , Award , SuccessStory , Testimonial



class PageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Page
        fields = '__all__'

class PageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'page_name', 'meta_title', 'meta_description', 'meta_keywords', 'status', 'content']


class AdminSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminSettings
        fields = '__all__'

# class AdminUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AdminUser
#         fields = '__all__'

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'password', 'full_name', 'role', 'phone_number', 'status']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'role_name', 'admin', 'view_only', 'sales', 'support', 'biz_dev', 'franchise']

class AdminUserSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())  

    class Meta:
        model = AdminUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role_id']



class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = '__all__'

class SuccessStoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = ['id', 'couple_name', 'photo', 'details','date_of_marriage', 'status']


class AwardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ['id', 'name', 'image', 'description', 'status']

class AwardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Award
        fields = ['id', 'name', 'image', 'description', 'status']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'profile_id', 'rating', 'review_content', 'user_image', 'status', 'date']

class TestimonialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['profile_id', 'rating', 'review_content', 'user_image', 'date']