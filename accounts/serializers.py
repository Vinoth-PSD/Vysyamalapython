# serializers.py
from rest_framework import serializers
from .models import BirthStar, ProfileHoroscope, ProfilePartnerPref, Rasi, Lagnam, DasaBalance, LoginDetailsTemp, FamilyType, FamilyStatus, FamilyValue, ProfileHolder, MaritalStatus, Height, Complexion, ParentsOccupation, HighestEducation, UgDegree, AnnualIncome, Country, State, District ,City, Mode , Property , Gothram , EducationLevel , Profession , Match , MasterStatePref , AdminUser , Role , Homepage ,ProfileStatus , MatchingStarPartner, Image_Upload, Profile_personal_notes, Registration1, Get_profiledata , Express_interests , Get_profiledata_Matching , ProfileSubStatus , PlanDetails , Profile_PlanFeatureLimit , ProfileVysAssistFollowup , VysAssistcomment ,ProfileSuggestedPref

from datetime import datetime, date

from .models import Profile
from datetime import datetime


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
    
    Notifcation_enabled = serializers.CharField(required=True)
    Addon_package = serializers.CharField(required=True)
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
    Profile_state = serializers.CharField(required=True)
    Profile_city = serializers.CharField(required=True)
    Profile_district = serializers.CharField(required=True)
    Gender = serializers.CharField(required=False,allow_null=True)
    Profile_pincode = serializers.CharField(required=True)

    Notifcation_enabled = serializers.CharField(required=True)
    Addon_package = serializers.CharField(required=True)
    Plan_id = serializers.CharField(required=True)
    Profile_idproof = serializers.FileField(required=False)  
    Profile_divorceproof = serializers.FileField(required=False)  

    class Meta:
        model = LoginDetails
        fields = '__all__'


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
    class Meta:
        model = ProfileFamilyDetails
        fields = '__all__'

class ProfileEduDetailsSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True)
    work_state = serializers.CharField(required=False , allow_null=True) 
    work_city = serializers.CharField(required=False , allow_null=True)
    work_district = serializers.CharField(required=False , allow_null=True)
    #ug_degeree = serializers.CharField(required=False , allow_null=True) 
    class Meta:
        model = ProfileEduDetails
        fields = '__all__'

class ProfilePartnerPrefSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True) 
    pref_porutham_star_rasi = serializers.CharField(required=False , allow_null=True)
    pref_porutham_star = serializers.CharField(required=False, allow_null=True)
    pref_height_to =  serializers.CharField(required=True)
    class Meta:
        model = ProfilePartnerPref
        fields = '__all__'
       
class ProfileSuggestedPrefSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(required=False , allow_null=True) 
    pref_porutham_star_rasi = serializers.CharField(required=False , allow_null=True)
    pref_porutham_star = serializers.CharField(required=False, allow_null=True)
    pref_height_to =  serializers.CharField(required=True)
    class Meta:
        model = ProfileSuggestedPref
        fields = '__all__'

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
    horoscope_hints = serializers.CharField(required=False , allow_null=True) 
    dasa_name = serializers.CharField(required=False , allow_null=True) 
    amsa_kattam = serializers.CharField(required=False, allow_null=True)
    rasi_kattam = serializers.CharField(required=False ,allow_null=True)
    horoscope_file = serializers.FileField(required=False)  
    class Meta:
        model = ProfileHoroscope
        fields = '__all__'


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