# serializers.py
from rest_framework import serializers
from .models import BirthStar, ProfileHoroscope, ProfilePartnerPref, Rasi, Lagnam, DasaBalance, LoginDetailsTemp, FamilyType, FamilyStatus, FamilyValue, ProfileHolder, MaritalStatus, Height, Complexion, ParentsOccupation, HighestEducation, UgDegree, AnnualIncome, Country, State, District ,City, Mode , Property , Gothram , EducationLevel , Profession , Match , MasterStatePref , AdminUser , Role , Homepage ,ProfileStatus , MatchingStarPartner, Image_Upload, Profile_personal_notes, Registration1, Get_profiledata , Express_interests , Get_profiledata_Matching , ProfileSubStatus , PlanDetails , Profile_PlanFeatureLimit , ProfileVysAssistFollowup , VysAssistcomment ,ProfileSuggestedPref ,ProfileVisibility

from datetime import datetime, date

from .models import Profile
from datetime import datetime
from .models import SentFullProfileEmailLog
from .models import SentShortProfileEmailLog
from .models import SentFullProfilePrintPDFLog
from .models import SentShortProfilePrintPDFLog
from .models import CallType
from .models import CallStatus
from .models import CallAction
from .models import ProfileCallManagement
from .models import MarriageSettleDetails
from .models import PaymentTransaction
from .models import Invoice

class ProfileStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileStatus
        fields = ['status_code', 'status_name']


class PlandetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanDetails
        fields = ['id', 'plan_name','plan_price']


class ProfileSubStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileSubStatus
        fields = ['id','status_code', 'sub_status_name']


class ModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mode
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

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
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
    id = serializers.IntegerField(required=False)  # Include the id field, not required

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

from rest_framework import serializers
from .models import LoginDetails


class UpdateAdminComments_Serializer(serializers.ModelSerializer):
    class Meta:
        model = LoginDetails
        fields = ['Admin_comments', 'Admin_comment_date']



class LoginDetailsSerializer(serializers.ModelSerializer):
    LoginId = serializers.CharField(required=False, allow_null=True)
    ProfileId = serializers.CharField(required=False, allow_null=True)
    EmailId = serializers.EmailField(required=True)
    Password = serializers.CharField(required=True)
    Profile_name = serializers.CharField(required=True)
    Profile_marital_status = serializers.CharField(required=True)
    Profile_dob = serializers.DateField(required=True)
   
    Profile_complexion = serializers.CharField(required=True)
    Profile_address = serializers.CharField(required=True)
    Profile_country = serializers.CharField(required=True)
    Profile_state = serializers.CharField(required=True)
    Profile_city = serializers.CharField(required=True)
    Profile_district = serializers.CharField(required=True)
    Gender = serializers.CharField(required=True)
    Profile_pincode = serializers.CharField(required=True)
    
    Notifcation_enabled = serializers.CharField(required=False , allow_blank=True, allow_null=True)
    Addon_package = serializers.CharField(required=False , allow_blank=True, allow_null=True)
    Otp_verify = serializers.IntegerField(required=False ,allow_null=True) 
    Plan_id = serializers.CharField(required=False)
    Profile_idproof = serializers.FileField(required=False)  
    Profile_divorceproof = serializers.FileField(required=False)
    

    class Meta:
        model = LoginDetails
        fields = '__all__'

    def validate(self, data):
        # Initialize a dictionary to collect errors
        errors = {}

        # Get mobile number and email from the incoming data
        mobile_no = data.get('Mobile_no')
        email_id = data.get('EmailId')

        # Step 1: Validate if mobile number already exists
        if mobile_no and LoginDetails.objects.filter(Mobile_no=mobile_no).exists():
            errors['Mobile_no'] = ['This mobile number is already registered.']

        # Step 2: Validate if email already exists
        if email_id and LoginDetails.objects.filter(EmailId=email_id).exists():
            errors['EmailId'] = ['This email address is already registered.']

        # If any errors are collected, raise a ValidationError
        if errors:
            raise serializers.ValidationError(errors)

        # Return the validated data if no errors
        return data


class LoginEditSerializer(serializers.ModelSerializer):
    ProfileId = serializers.CharField(required=False, allow_null=True)
    EmailId = serializers.EmailField(required=True)
    Password = serializers.CharField(required=True)
    Profile_name = serializers.CharField(required=False,allow_null=True)
    Profile_marital_status = serializers.CharField(required=True)
    Profile_dob = serializers.DateField(required=True)
   
    Profile_complexion = serializers.CharField(required=True)
    Profile_address = serializers.CharField(required=True)
    Profile_country = serializers.CharField(required=True)
    Profile_state = serializers.CharField(required=True,allow_null=True, allow_blank=True)
    Profile_city = serializers.CharField(required=True)
    Profile_district = serializers.CharField(required=True,allow_null=True, allow_blank=True)
    Gender = serializers.CharField(required=False,allow_null=True)
    Profile_pincode = serializers.CharField(required=True)

    Notifcation_enabled = serializers.CharField(required=False ,allow_blank=True, allow_null=True)
    Addon_package = serializers.CharField(required=False ,allow_blank=True, allow_null=True)
    Plan_id = serializers.CharField(required=True)
    Profile_idproof = serializers.FileField(required=False)  
    Profile_divorceproof = serializers.FileField(required=False)  
    Otp_verify = serializers.IntegerField(required=False ,allow_null=True)  

    class Meta:
        model = LoginDetails
        fields = '__all__'
    def validate(self, data):
        profile_country = str(data.get('Profile_country')).strip()

        if profile_country == '1':
            if not data.get('Profile_state'):
                raise serializers.ValidationError({'Profile_state': 'This field is required when Profile_country is 1.'})
            if not data.get('Profile_district'):
                raise serializers.ValidationError({'Profile_district': 'This field is required when Profile_country is 1.'})
        else:
            data['Profile_state'] = None
            data['Profile_district'] = None

        return data

class ProfileFamilyDetailsSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True)
    father_name = serializers.CharField(required=True)
    mother_name = serializers.CharField(required=True)
    family_name = serializers.CharField(required=False , allow_null=True) 
    about_self = serializers.CharField(required=True)
    blood_group = serializers.CharField(required=True)
    Pysically_changed = serializers.CharField(required=True)
    father_occupation = serializers.CharField(required=True)
    mother_occupation = serializers.CharField(required=True)
    weight = serializers.CharField(required=False , allow_null=True)
    eye_wear = serializers.CharField(required=False , allow_null=True)
    suya_gothram = serializers.CharField(required=False , allow_null=True)
    uncle_gothram = serializers.CharField(required=False , allow_null=True)
    suya_gothram_admin = serializers.CharField(required=False , allow_null=True)
    uncle_gothram_admin = serializers.CharField(required=False , allow_null=True)
    father_alive = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_alive = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = ProfileFamilyDetails
        fields = '__all__'

class ProfileEduDetailsSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False, allow_null=True)
    work_state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_district = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ProfileEduDetails
        fields = '__all__'

    def validate(self, data):
        work_country = data.get('work_country')

        if work_country == '1':
            if not data.get('work_state'):
                raise serializers.ValidationError({'work_state': 'This field is required when work_country is 1.'})
            if not data.get('work_district'):
                raise serializers.ValidationError({'work_district': 'This field is required when work_country is 1.'})
        else:
            data['work_state'] = None
            data['work_district'] = None

        return data

class ProfilePartnerPrefSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True) 
    pref_porutham_star_rasi = serializers.CharField(required=False , allow_null=True)
    pref_porutham_star = serializers.CharField(required=False, allow_null=True)
    pref_height_to =  serializers.CharField(required=True)
    
    pref_family_status =  serializers.CharField(required=False, allow_null=True)
    pref_state =  serializers.CharField(required=False, allow_null=True)
    class Meta:
        model = ProfilePartnerPref
        fields = '__all__'
       
class ProfileSuggestedPrefSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True) 
    pref_porutham_star_rasi = serializers.CharField(required=False , allow_null=True)
    pref_porutham_star = serializers.CharField(required=False, allow_null=True)
    pref_height_to =  serializers.CharField(required=True)

    pref_family_status =  serializers.CharField(required=False, allow_null=True)
    pref_state =  serializers.CharField(required=False, allow_null=True)
    class Meta:
        model = ProfileSuggestedPref
        fields = '__all__'

class ProfileVisibilitySerializer(serializers.ModelSerializer):
    visibility_age_from = serializers.CharField(required=False , allow_null=True)
    visibility_age_to = serializers.CharField(required=False , allow_null=True)
    visibility_height_from = serializers.CharField(required=False , allow_null=True)
    visibility_height_to = serializers.CharField(required=False , allow_null=True)

    visibility_profession = serializers.CharField(required=False , allow_null=True)
    visibility_education = serializers.CharField(required=False , allow_null=True)
    visibility_anual_income = serializers.CharField(required=False , allow_null=True)
    visibility_family_status = serializers.CharField(required=False , allow_null=True)
    visibility_chevvai = serializers.CharField(required=False , allow_null=True)
    visibility_ragukethu = serializers.CharField(required=False , allow_null=True)
    visibility_foreign_interest = serializers.CharField(required=False , allow_null=True)
    status = serializers.CharField(required=False , allow_null=True)
   
    
    class Meta:
        model = ProfileVisibility
        fields = ('profile_id', 'visibility_age_from', 'visibility_age_to' ,'visibility_height_from', 'visibility_height_to', 
                  'visibility_profession', 'visibility_education', 'visibility_anual_income', 'visibility_family_status','visibility_chevvai',
                  'visibility_ragukethu', 'visibility_foreign_interest','status')

class ProfileplanSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False , allow_null=True) 
    profile_id = serializers.CharField(required=False , allow_null=True)
    exp_int_lock = serializers.CharField(required=False , allow_null=True)
    exp_int_count = serializers.CharField(required=False , allow_null=True)
    visit_count= serializers.CharField(required=False , allow_null=True)

    class Meta:
        model = Profile_PlanFeatureLimit
        fields = '__all__'



class Getnewprofiledata(serializers.ModelSerializer):
    class Meta:
        model = LoginDetails
        fields = '__all__' 

# class Getnewprofiledata_new(serializers.Serializer):
#     ProfileId = serializers.CharField()
#     Gender = serializers.CharField()
#     EmailId = serializers.EmailField()
#     Profile_dob = serializers.DateField()
#     Profile_city = serializers.CharField()
#     # Add the joined table fields
#     MaritalStatus = serializers.CharField()
#     complexion_desc = serializers.CharField()
#     state_name = serializers.CharField()
#     district_name = serializers.CharField()
#     city_name = serializers.CharField()
#     country_name = serializers.CharField()
        
class Getnewprofiledata_new(serializers.Serializer):
    ContentId = serializers.IntegerField()
    ProfileId = serializers.CharField()
    Profile_name = serializers.CharField()
    Gender = serializers.CharField()
    Mobile_no = serializers.CharField()
    Profile_whatsapp = serializers.CharField()
    Profile_alternate_mobile =serializers.CharField()
    EmailId = serializers.EmailField()
    Profile_dob = serializers.DateField()
    Profile_city = serializers.CharField()
    Plan_id = serializers.CharField()
    status = serializers.CharField()
    
    # Custom field to handle datetime to date conversion for DateOfJoin
    DateOfJoin = serializers.SerializerMethodField()
    birthstar_name = serializers.SerializerMethodField()


    # Add the joined table fields
    MaritalStatus = serializers.CharField()
    complexion_desc = serializers.CharField()
    state_name = serializers.CharField()
    district_name = serializers.CharField()
    city_name = serializers.CharField()
    country_name = serializers.CharField()

    # Add family and education details
    family_status = serializers.SerializerMethodField()
    Profile_for = serializers.SerializerMethodField()
    highest_education = serializers.SerializerMethodField()  # Changed to SerializerMethodField
    profession = serializers.CharField()
    anual_income = serializers.SerializerMethodField()
    Last_login_date= serializers.CharField()  
    years = serializers.SerializerMethodField()

    # Method to calculate age from Profile_dob
    def get_years(self, obj):
        dob = obj.get('Profile_dob')
        if dob:
            return calculate_age(dob)
        return None
    
    def get_family_status(self, obj):
     family_status_value = obj.get('family_status')
 
     if family_status_value:
         try:
             family_status_id = int(family_status_value)
             
             family_status = FamilyStatus.objects.get(id=family_status_id, is_deleted=False)
             return family_status.status  
         except (ValueError, FamilyStatus.DoesNotExist):
             return family_status_value
    
         return None

    
    def get_highest_education(self, obj):
        education_value = obj.get('highest_education')
        
        if education_value:
            try:
                education_id = int(education_value)
                education = EducationLevel.objects.get(row_id=education_id, is_deleted=False)
                return education.EducationLevel 
            except (ValueError, EducationLevel.DoesNotExist):
                return education_value
        return None
    
    def get_anual_income(self, obj):
        anual_income_value = obj.get('anual_income')
    
        if anual_income_value:
            try:
                anual_income_id = int(anual_income_value)
                
                anual_income = AnnualIncome.objects.get(id=anual_income_id, is_deleted=False)
                return anual_income.income  
            except (ValueError, AnnualIncome.DoesNotExist):
                return anual_income_value
        
        return None
    
    def get_Profile_for(self, obj):
        profile_for_input = obj.get('Profile_for')
        if profile_for_input:
            try:
                mode = Mode.objects.get(mode=profile_for_input, is_deleted=False)
                return mode.mode_name  
            except (ValueError, Mode.DoesNotExist):
                return profile_for_input
        return None
    
    def get_profession(self, obj):
        profession_value = obj.get('profession')
        print(profession_value,'profession_value')
        if profession_value:
            try:
                profession_id = int(profession_value)
                
                profession = Profession.objects.get(RowId=profession_id, is_deleted=False)
                return profession.Profession  
            except (ValueError, Profession.DoesNotExist):
                return profession_value
        
        return None
    
    def get_birthstar_name(self, obj):
        birthstar_input = obj.get('birthstar_name')
        if birthstar_input:
            try:
                birthstar = BirthStar.objects.get(pk=int(birthstar_input), is_deleted=False)
                return birthstar.star  
            except (ValueError, BirthStar.DoesNotExist):
                return birthstar_input
        return None


    def get_DateOfJoin(self, obj):
        # Convert datetime to date if it's a datetime field
        return obj['DateOfJoin'].date() if obj.get('DateOfJoin') else None
    # The calculate_age function
# def calculate_age(dob):
#     """
#     Calculate age based on date of birth.
    
#     Args:
#     dob (datetime.date): The date of birth.
    
#     Returns:
#     int or None: The calculated age or None if dob is not provided.
#     """
#     if dob:
#         today = datetime.today()
#         age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
#         return age
#     return None

def calculate_age(dob):
    """
    Calculate age based on date of birth.

    Args:
    dob (str or datetime.date): The date of birth in string format (YYYY-MM-DD) or as a date object.

    Returns:
    int or None: The calculated age or None if dob is invalid.
    """
    if isinstance(dob, str):
        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date()  # Convert string to date
        except ValueError:
            return None  # Return None if the format is invalid

    if not isinstance(dob, date):  # Ensures dob is a valid date object
        return None

    today = date.today()

    if dob > today:  # Prevent future dates
        raise ValueError("Date of birth cannot be in the future")

    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age
      
        
from rest_framework import viewsets
from .models import ProfilePartnerPref , Homepage
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


# class RoleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Role
#         fields = ['id', 'role_name', 'admin', 'view_only', 'sales', 'support', 'biz_dev', 'franchise']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            'id', 'role_name', 'search_profile', 'add_profile',
            'edit_profile_all_fields', 'edit_profile_admin_comments_and_partner_settings',
            'membership_activation', 'new_photo_update', 'edit_horo_photo', 'add_users'
        ]

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
    image = serializers.ImageField(required=False, allow_null=True)  
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

        
class VysassistSerializer(serializers.ModelSerializer):
    class Meta:
        model = VysAssistcomment
        fields = ['id', 'comment_text']
        

class ProfileHoroscopeSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True) 
    horoscope_hints = serializers.CharField(required=False ,allow_blank=True , allow_null=True) 
    dasa_name = serializers.CharField(required=False , allow_null=True) 
    amsa_kattam = serializers.CharField(required=False, allow_null=True)
    rasi_kattam = serializers.CharField(required=False ,allow_null=True)
    horoscope_file = serializers.FileField(required=False)
    star_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProfileHoroscope
        fields = '__all__'

    def get_star_name(self, obj):
        if not obj.birthstar_name:
            return None  # Or return '' if you prefer blank
        try:
            birthstar = BirthStar.objects.get(id=obj.birthstar_name, is_deleted=False)
            return birthstar.star
        except BirthStar.DoesNotExist:
            return None


class HomepageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Homepage
        fields = ['id', 'why_vysyamala', 'youtube_links', 'vysyamala_apps']




# class QuickUploadSerializer(serializers.ModelSerializer):
#     horoscope_file = serializers.SerializerMethodField()

#     class Meta:
#         model = LoginDetails
#         fields = ['ProfileId', 'Profile_for', 'Gender', 'Mobile_no', 'Profile_name', 'Profile_marital_status', 'Profile_idproof', 'horoscope_file']

#     def get_horoscope_file(self, obj):
#         try:
#             # Assuming ProfileId is used to match with Horoscope model's profile_id
#             horoscope = ProfileHoroscope.objects.get(profile_id=obj.ProfileId)
#             return horoscope.horoscope_file if horoscope.horoscope_file else None
#         except ProfileHoroscope.DoesNotExist:
#             return None



class QuickUploadSerializer(serializers.ModelSerializer):
    horoscope_file = serializers.SerializerMethodField()
    Profile_for = serializers.SerializerMethodField()  # Fetch human-readable name for Profile_for
    Profile_marital_status = serializers.SerializerMethodField()  # Fetch human-readable name for Profile_marital_status

    class Meta:
        model = LoginDetails
        fields = ['ProfileId', 'Profile_for', 'Gender', 'Mobile_no', 'Profile_name', 'Profile_marital_status', 'Profile_idproof', 'horoscope_file']

    def get_horoscope_file(self, obj):
        try:
            horoscope = ProfileHoroscope.objects.get(profile_id=obj.ProfileId)

            if isinstance(horoscope.horoscope_file, str):
                return horoscope.horoscope_file  
            elif horoscope.horoscope_file:
                return horoscope.horoscope_file.url  
            else:
                return None

        except ProfileHoroscope.DoesNotExist:
            return None

    def get_Profile_for(self, obj):
        # Fetch the mode name based on the Profile_for field
        try:
            mode = Mode.objects.get(mode=obj.Profile_for)
            return mode.mode_name  
        except Mode.DoesNotExist:
            return None  

    def get_Profile_marital_status(self, obj):
        # Fetch the marital status name based on the Profile_marital_status field
        try:
            marital_status = MaritalStatus.objects.get(StatusId=obj.Profile_marital_status)
            return marital_status.MaritalStatus  
        except MaritalStatus.DoesNotExist:
            return None  


class MatchingscoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingStarPartner
        fields = ['id', 'gender', 'source_star_id', 'source_rasi_id', 'dest_star_id', 'dest_rasi_id', 'match_count','matching_porutham']


class PersonalnotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile_personal_notes
        fields = ['id', 'profile_id', 'profile_to', 'notes', 'datetime', 'status']
    

class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image_Upload
        fields = ['id', 'profile_id', 'image', 'uploaded_at']

class ExpressInterestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Express_interests
        fields = ['id', 'profile_from', 'profile_to', 'req_datetime', 'response_datetime', 'status']

class GetproflistSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True)
    profile_id_out = serializers.SerializerMethodField()

    class Meta:
        model = Get_profiledata
        fields = ('profile_id', 'profile_id_out')

    # def validate_profile_id(self, value):
    #     if not models.Registration1.objects.filter(ProfileId=value).exists():
    #         raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
    #     return value

    # the below code is to check the ProfileId id field against the profile_id
    def get_profile_id_out(self, obj):
        return obj.ProfileId

    def validate_profile_id(self, value):
            #profile_id = data.get('profile_id')
            if not Registration1.objects.filter(ProfileId=value).exists():
                raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
            return value

class Profile_idValidationSerializer(serializers.Serializer):
    profile_id = serializers.CharField(max_length=20)

    def validate_profile_id(self, value):
        if not Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value

class ProfileVysAssistFollowupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileVysAssistFollowup
        fields = '__all__'

    def validate(self, data):
        required_fields = ['assist_id', 'owner_id', 'comments','owner_name']
        for field in required_fields:
            if field not in data or data[field] in [None, '']:
                raise serializers.ValidationError({field: f"{field} is required."})
        return data
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    
class SentFullProfileEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentFullProfileEmailLog
        fields = '__all__'  # Include all fields

class SentShortProfileEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentShortProfileEmailLog
        fields = '__all__'

class SentFullProfilePrintPDFLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentFullProfilePrintPDFLog
        fields = '__all__'  # Serializes all fields

class SentShortProfilePrintPDFLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentShortProfilePrintPDFLog
        fields = '__all__'  # Include all model fields

class CallTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallType
        fields = '__all__'

class CallStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallStatus
        fields = '__all__'

class CallActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallAction
        fields = '__all__'
# class ProfileCallManagementSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProfileCallManagement
#         fields = '__all__'

class ProfileCallManagementSerializer(serializers.ModelSerializer):
    call_status_value = serializers.SerializerMethodField()
    call_type_value = serializers.SerializerMethodField()
    callaction_today_value = serializers.SerializerMethodField()
    future_actiontaken_value = serializers.SerializerMethodField()
    work_asigned_value = serializers.SerializerMethodField()
    owner_value = serializers.SerializerMethodField()

    class Meta:
        model = ProfileCallManagement
        fields = '__all__'  # all original DB fields
        # Add the extra value fields to the response
        extra_fields = ['call_status_value', 'call_type_value', 'callaction_today_value', 'future_actiontaken_value', 'work_asigned_value', 'owner_value']

    def get_call_status_value(self, obj):
        from .models import CallStatus
        if obj.call_status_id:
            try:
                return CallStatus.objects.get(id=obj.call_status_id).call_status
            except CallStatus.DoesNotExist:
                return None
        return None

    def get_call_type_value(self, obj):
        from .models import CallType
        if obj.call_type_id:
            try:
                return CallType.objects.get(id=obj.call_type_id).call_type
            except CallType.DoesNotExist:
                return None
        return None

    def get_callaction_today_value(self, obj):
        from .models import CallAction
        if obj.callaction_today_id:
            try:
                return CallAction.objects.get(id=obj.callaction_today_id).call_action_name
            except CallAction.DoesNotExist:
                return None
        return None

    def get_future_actiontaken_value(self, obj):
        from .models import CallAction
        if obj.future_actiontaken_id:
            try:
                return CallAction.objects.get(id=obj.future_actiontaken_id).call_action_name
            except CallAction.DoesNotExist:
                return None
        return None
    
    def get_work_asigned_value(self, obj):
        from .models import AdminUser
        if obj.work_asignid:
            try:
                user = AdminUser.objects.get(id=obj.work_asignid)
                return user.first_name or user.username
            except AdminUser.DoesNotExist:
                return None
        return None

    def get_owner_value(self, obj):
        from .models import AdminUser
        if obj.owner_id:
            try:
                user = AdminUser.objects.get(id=obj.owner_id)
                return user.first_name or user.username
            except AdminUser.DoesNotExist:
                return None
        return None
    
    def validate(self, data):
        required_fields = ['profile_id', 'profile_status_id', 'owner_id']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise serializers.ValidationError({field: "This field is required."})
        return data
        

class MarriageSettleDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarriageSettleDetails
        fields = '__all__'

    def validate(self, data):
        required_fields = ['profile_id', 'owner_id']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "This field is required."})
        return data

class PaymentTransactionSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField(required=False)
    order_id = serializers.CharField(required=False)
    payment_id = serializers.CharField(required=False)
    amount = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    status = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(required=False)
    discount_amont = serializers.DecimalField(required=False, max_digits=10, decimal_places=2)
    payment_refno = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    owner_id = serializers.IntegerField(required=False)

    class Meta:
        model = PaymentTransaction
        fields = '__all__'

    def validate(self, data):
        required_fields = ['profile_id', 'payment_type']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "This field is required."})
        return data
    
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class AdminUserDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ['id', 'username']
        
class CommonProfileSearchSerializer(serializers.Serializer):
    search_profile_id = serializers.CharField(required=False, allow_blank=True)
    profile_name = serializers.CharField(required=False, allow_blank=True)
    search_profession = serializers.CharField(required=False, allow_blank=True)
    chevvai_dosham = serializers.CharField(required=False, allow_blank=True)
    ragu_dosham = serializers.CharField(required=False, allow_blank=True)
    age_from = serializers.IntegerField(required=False, min_value=18, max_value=100)
    age_to = serializers.IntegerField(required=False, min_value=18, max_value=100)
    search_location = serializers.CharField(required=False, allow_blank=True)
    complexion = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    education = serializers.CharField(required=False, allow_blank=True)
    foreign_intrest = serializers.CharField(required=False, allow_blank=True)
    has_photos = serializers.CharField(required=False, allow_blank=True)
    height_from = serializers.IntegerField(required=False)
    height_to = serializers.IntegerField(required=False)
    matching_stars = serializers.CharField(required=False, allow_blank=True)
    min_anual_income = serializers.IntegerField(required=False)
    max_anual_income = serializers.IntegerField(required=False)
    membership = serializers.IntegerField(required=False)
    per_page = serializers.IntegerField(default=10)
    page_number = serializers.IntegerField(default=1)

