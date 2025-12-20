from rest_framework import serializers
from . import models
import random
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.hashers import make_password
from .encryption_utils import encrypt_password, decrypt_password , generate_key
from django.conf import settings
from .utils import send_email_notification
from .models import SentWithoutAddressEmailLog
from .models import SentWithoutAddressPrintPDFLog




class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuthUser
        fields = ['username', 'password']


# # serializers.py
# from rest_framework import serializers
# from .models import Registration

class ResendOtpSerializers(serializers.ModelSerializer):
    #mobile_no = serializers.CharField(write_only=True)  # Define mobile_no as write-only field

    class Meta:
        model = models.Basic_Registration
        fields = ['ProfileId']  # Include 'mobile_no' field in the fields list

    def validate(self, data):
        ProfileId = data.get('ProfileId')

        try:
            # Retrieve Basic_Registration instance based on ProfileId
            basic_registration_instance = models.Basic_Registration.objects.get(ProfileId=ProfileId)

            # Get the mobile number from the instance
            data['mobile_no'] = basic_registration_instance.Mobile_no

            # Generate a new OTP and add it to the data
            
            #data['Otp'] = random.randint(100000, 999999)
            data['Otp'] = random.randint(100000, 999999)
            # data['Otp'] = 123456

        except models.Basic_Registration.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'Invalid ProfileId'
            })

        return data



class OtpSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Basic_Registration
        fields = ['Otp', 'ProfileId']

    def validate(self, data):
        otp = data.get('Otp')
        ProfileId = data.get('ProfileId')                
        # Debugging print statement
        #print('Verify otp:', otp, 'for mobile number:', mobile_no)

        try:
            # Check if there is a record with the provided OTP and mobile number
            verify_otp=models.Basic_Registration.objects.get(Otp=otp, ProfileId=ProfileId)

            verify_otp.Otp_verify = 1 #set Otp verify as one thats show in the admin as well

            verify_otp.save()

        except models.Basic_Registration.DoesNotExist:
             raise serializers.ValidationError({
                'error': 'Invalid OTP number'
            })
                   
        return data


class Registration1Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Basic_Registration
        fields = ('Profile_for', 'Gender', 'Mobile_no', 'EmailId', 'Password')

    def validate_EmailId(self, EmailId):
        print('EmailId',EmailId)
        if models.Registration1.objects.filter(EmailId=EmailId,Status__in=[0, 1]).exists():
            raise serializers.ValidationError("This email is already registered.")
        return EmailId

    def validate_Mobile_no(self, Mobile_no):
        print('Mobile_no',Mobile_no)
        if models.Registration1.objects.filter(Mobile_no=Mobile_no,Status__in=[0, 1]).exists():
            raise serializers.ValidationError("This mobile number is already registered.")
        return Mobile_no
    def validate(self, data):
     
     #data['Otp']='142024'
    #  data['Password']=make_password(data['Password'])
     data['Password']=data['Password']
     #key = generate_key()
     #print('ferkey',key.decode())
     #data['Password']=encrypt_password(data['Password'])
     data['ProfileId']=''.join(random.choices('0123456789', k=6))
    #  data['Otp'] = random.randint(100000, 999999)
     otp =random.randint(100000, 999999)
    #  print('otp',otp)
     data['Otp'] = otp
     data['Status']=0

     return data


     
class Registration2Serializer(serializers.ModelSerializer):
    
    
    class Meta:
        model = models.Registration1
        fields = ('ProfileId','Profile_name', 'Profile_marital_status', 'Profile_dob', 'Profile_height', 'Profile_complexion')


class ContactSerializer(serializers.ModelSerializer):
    
    Profile_district = serializers.CharField(required=False, allow_blank=True)
    Profile_alternate_mobile = serializers.CharField(required=False, allow_blank=True)
    Profile_whatsapp= serializers.CharField(required=False, allow_blank=True)
    Profile_mobile_no= serializers.CharField(required=False, allow_blank=True)
    Profile_emailid= serializers.CharField(required=False, allow_blank=True)
    Profile_city= serializers.CharField(required=False, allow_blank=True)
    Profile_state= serializers.CharField(required=False, allow_blank=True)
    Profile_country= serializers.CharField(required=False, allow_blank=True)
    Profile_address= serializers.CharField(required=False, allow_blank=True)
    Profile_pincode= serializers.CharField(required=False, allow_blank=True)
    
    
    class Meta:
        model = models.Registration1
        fields = ('ProfileId','Profile_address','Profile_country','Profile_state','Profile_district','Profile_city','Profile_pincode','Profile_alternate_mobile','Profile_whatsapp','Profile_mobile_no','Profile_emailid')

    def validate(self, data):
        # Get the values of Profile_mobile_no and Profile_alternate_mobile
        alternate_mobile = data.get('Profile_alternate_mobile')
        ProfileId = data.get('ProfileId')

        # print(alternate_mobile, ProfileId)

        # Check if Profile_alternate_mobile is the same as Profile_mobile_no for the same ProfileId
        if alternate_mobile:
            # Query the database to check if the Profile_alternate_mobile exists as Profile_mobile_no within the same ProfileId
            existing_entry = models.Registration1.objects.filter(ProfileId=ProfileId, Mobile_no=alternate_mobile).exists()

            if existing_entry:
                # print("Existing entry found")
                raise serializers.ValidationError({
                    'Profile_alternate_mobile': 'This phone number already exists, plesae enter alternate mobile number'
                })

        return data

        
   
class Get_Profileholder(serializers.ModelSerializer):
    class Meta:
        model = models.Profileholder
        fields = '__all__'  # Include all fields of the model

class CustomProfileholderSerializer(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()
    owner_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Profileholder
        fields = ['owner_id', 'owner_description']

    def get_owner_id(self, obj):
        return obj.Mode

    def get_owner_description(self, obj):
        return obj.ModeName
    

class CustomHeightSerializer(serializers.ModelSerializer):
    height_id = serializers.SerializerMethodField()
    height_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Profileheights
        fields = ['height_id', 'height_description']

    def get_height_id(self, obj):
        return obj.height_value

    def get_height_description(self, obj):
        return obj.height_desc
    

class CustomComplexionSerializer(serializers.ModelSerializer):
    complexion_id = serializers.SerializerMethodField()
    complexion_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Profilecomplexion
        fields = ['complexion_id', 'complexion_description']

    def get_complexion_id(self, obj):
        return obj.complexion_id

    def get_complexion_description(self, obj):
        return obj.complexion_desc
    

class CustomCountrySerializer(serializers.ModelSerializer):
    country_id = serializers.SerializerMethodField()
    country_name = serializers.SerializerMethodField()
    most_pref = serializers.SerializerMethodField()

    class Meta:
        model = models.Profilecountry
        fields = ['country_id', 'country_name','most_pref']

    def get_country_id(self, obj):
        return obj.id
    
    def get_country_name(self, obj):
        return obj.name
        
    def get_most_pref(self, obj):
        return obj.most_pref
    

class CustomStateSerializer(serializers.ModelSerializer):
    state_id = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Profilestate
        fields = ['state_id', 'state_name']

    def get_state_id(self, obj):
        return obj.id
    
    def get_state_name(self, obj):
        return obj.name
    

class CustomCitySerializer(serializers.ModelSerializer):
    city_id = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Profilecity
        fields = ['city_id', 'city_name']

    #def validate(self, data):
        
    def get_city_id(self, obj):
        return obj.id
    
    def get_city_name(self, obj):
        return obj.city_name

class CustomDistictSerializer(serializers.ModelSerializer):
    disctict_id = serializers.SerializerMethodField()
    disctict_name = serializers.SerializerMethodField()
    
    class Meta:
        model = models.Profiledistrict
        fields = ['disctict_id', 'disctict_name']

    #def validate(self, data):
        
    def get_disctict_id(self, obj):
        return obj.id
    
    def get_disctict_name(self, obj):
        return obj.name
    
class CustomMaritalSerializer(serializers.ModelSerializer):
    marital_sts_id = serializers.SerializerMethodField()
    marital_sts_name = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ProfileMaritalstatus
        fields = ['marital_sts_id', 'marital_sts_name']

    #def validate(self, data):
        
    def get_marital_sts_id(self, obj):
        return obj.StatusId 
    
    def get_marital_sts_name(self, obj):
        return obj.MaritalStatus
    



class CustomParentOccupSerializer(serializers.ModelSerializer):
    occupation_id = serializers.SerializerMethodField()
    occupation_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Parentoccupation
        fields = ['occupation_id', 'occupation_description']

    def get_occupation_id(self, obj):
        return obj.id

    def get_occupation_description(self, obj):
        return obj.occupation
    

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image_Upload  # Use correct model name here
        fields = ['id', 'profile_id', 'image', 'uploaded_at']


class HorosuploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Horoscope  # Use correct model name here
        fields = ['profile_id', 'horoscope_file', 'horo_file_updated']

class IdproofuploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1  # Use correct model name here
        fields = ['ProfileId', 'Profile_idproof']

class divorcecertiuploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1  # Use correct model name here
        fields = ['ProfileId', 'Profile_divorceproof']


class CustomPropertyWorthSerializer(serializers.ModelSerializer):
    property_id = serializers.SerializerMethodField()
    property_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Propertyworth
        fields = ['property_id', 'property_description']

    def get_property_id(self, obj):
        return obj.id

    def get_property_description(self, obj):
        return obj.property
    
# class CustomHighestEduSerializer(serializers.ModelSerializer):
#     education_id = serializers.SerializerMethodField()
#     education_description = serializers.SerializerMethodField()

#     class Meta:
#         model = models.Highesteducation
#         fields = ['education_id', 'education_description']

#     def get_education_id(self, obj):
#         return obj.id

#     def get_education_description(self, obj):
#         return obj.degree


class CustomHighestEduSerializer(serializers.ModelSerializer):
    education_id = serializers.SerializerMethodField()
    education_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Edupref
        fields = ['education_id', 'education_description']

    def get_education_id(self, obj):
        return obj.RowId

    def get_education_description(self, obj):
        return obj.EducationLevel



    
class CustomUgDegreeSerializer(serializers.ModelSerializer):
    degree_id = serializers.SerializerMethodField()
    degree_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Ugdegree
        fields = ['degree_id', 'degree_description']

    def get_degree_id(self, obj):
        return obj.id

    def get_degree_description (self, obj):
        return obj.degree

class CustomField_study(serializers.ModelSerializer):
    study_id = serializers.SerializerMethodField()
    study_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Profilefieldstudy
        fields = ['study_id', 'study_description']

    def get_study_id(self, obj):
        return obj.id

    def get_study_description (self, obj):
        return obj.field_of_study


class CustomField_degree(serializers.ModelSerializer):
    degeree_id = serializers.SerializerMethodField()
    degeree_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Profileedu_degree
        fields = ['degeree_id', 'degeree_description']

    def get_degeree_id(self, obj):
        return obj.id

    def get_degeree_description (self, obj):
        return obj.degeree_name


class CustomAnnualIncSerializer(serializers.ModelSerializer):
    income_id = serializers.SerializerMethodField()
    income_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Annualincome
        fields = ['income_id', 'income_description']

    def get_income_id(self, obj):
        return obj.id

    def get_income_description(self, obj):
        return obj.income    

class CustomPlaceOfBirSerializer(serializers.ModelSerializer):
    birth_id = serializers.SerializerMethodField()
    birth_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Placeofbirth
        fields = ['birth_id', 'birth_description']

    def get_birth_id(self, obj):
        return obj.id

    def get_birth_description(self, obj):
        return obj.place
    

class CustomLagnamDidiSerializer(serializers.ModelSerializer):
    didi_id = serializers.SerializerMethodField()
    didi_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Lagnamdidi
        fields = ['didi_id', 'didi_description']

    def get_didi_id (self, obj):
        return obj.id

    def get_didi_description(self, obj):
        return obj.name

class CustomDasaNameSerializer(serializers.ModelSerializer):
    dasa_id = serializers.SerializerMethodField()
    dasa_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Dasaname
        fields = ['dasa_id', 'dasa_description']

    def get_dasa_id (self, obj):
        return obj.id

    def get_dasa_description(self, obj):
        return obj.name
    
class CustomBirthStarSerializer(serializers.ModelSerializer):
    birth_id = serializers.SerializerMethodField()
    birth_star = serializers.SerializerMethodField()

    class Meta:
        model = models.Birthstar
        fields = ['birth_id', 'birth_star']

    def get_birth_id(self, obj):
        return obj.id
    
    def get_birth_star(self, obj):
       #return obj.star
        state_id = self.context.get('state_id')
        
        if state_id=='570':
        
            return obj.tamil_series 
        if state_id=='571':
        
            return obj.kannada_series 
        if (state_id=='572' or state_id=='573'):
        
            return obj.kannada_series 
        else:
             return obj.tamil_series

class CustomRasiSerializer(serializers.ModelSerializer):
    rasi_id = serializers.SerializerMethodField()
    rasi_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Rasi
        fields = ['rasi_id', 'rasi_name']

    def get_rasi_id(self, obj):
        return obj.id
    
    def get_rasi_name(self, obj):

        state_id = self.context.get('state_id')
        
        
        if state_id=='570':
        
            return obj.tamil_series 
        if state_id=='571':
        
            return obj.kannada_series 
        if (state_id=='572' or state_id=='573'):
        
            return obj.kannada_series 
        else:
             return obj.tamil_series
    
    
class CustomFamilyTypeSerializer(serializers.ModelSerializer):
    family_id = serializers.SerializerMethodField()
    family_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Familytype
        fields = ['family_id', 'family_description']

    def get_family_id(self, obj):
        return obj.id

    def get_family_description(self, obj):
        return obj.name
    
class CustomFamilyStatSerializer(serializers.ModelSerializer):
    family_status_id = serializers.SerializerMethodField()
    family_status_name = serializers.SerializerMethodField()
    family_status_description = serializers.SerializerMethodField()

    class Meta:
        model = models.Familystatus
        fields = ['family_status_id', 'family_status_name', 'family_status_description']

    def get_family_status_id(self, obj):
        return obj.id

    def get_family_status_name(self, obj):
        return obj.status

    def get_family_status_description(self, obj):
        return obj.description

class CustomFamilyValSerializer(serializers.ModelSerializer):
    family_value_id = serializers.SerializerMethodField()
    family_value_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Familyvalue
        fields = ['family_value_id', 'family_value_name']

    def get_family_value_id(self, obj):
        return obj.FamilyValueid

    def get_family_value_name(self, obj):
        return obj.FamilyValue

    
class MatchingStarInputSerializer(serializers.Serializer):
    birth_rasi_id = serializers.IntegerField()
    birth_star_id = serializers.IntegerField()
    gender = serializers.CharField(max_length=10)

class MatchingStarSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    gender = serializers.CharField(max_length=10)
    source_rasi_id = serializers.IntegerField()
    source_star_id = serializers.IntegerField()
    matching_porutham = serializers.CharField(max_length=255)
    dest_rasi_id = serializers.IntegerField()
    dest_star_id = serializers.IntegerField()
    matching_starname = serializers.CharField(max_length=255)
    matching_rasiname = serializers.CharField(max_length=255)
    match_count = serializers.CharField(max_length=255)
    protham_names = serializers.CharField(max_length=255)


class CustomStatePrefSerializer(serializers.ModelSerializer):
    State_Pref_id = serializers.SerializerMethodField()
    State_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Statepref
        fields = ['State_Pref_id', 'State_name']

    def get_State_Pref_id(self, obj):
        return obj.id

    def get_State_name(self, obj):
        return obj.state

class CustomEduPrefSerializer(serializers.ModelSerializer):
    Edu_Pref_id = serializers.SerializerMethodField()
    Edu_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Edupref
        fields = ['Edu_Pref_id', 'Edu_name']

    def get_Edu_Pref_id(self, obj):
        return obj.RowId

    def get_Edu_name(self, obj):
        return obj.EducationLevel
    
class CustomProfesPrefSerializer(serializers.ModelSerializer):
    Profes_Pref_id = serializers.SerializerMethodField()
    Profes_name = serializers.SerializerMethodField()

    class Meta:
        model = models.Profespref
        fields = ['Profes_Pref_id', 'Profes_name']

    def get_Profes_Pref_id(self, obj):
        return obj. RowId

    def get_Profes_name(self, obj):
        return obj.profession
    
class HoroscopeSerializer(serializers.ModelSerializer):
    
    rasi_kattam = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    amsa_kattam = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    chevvai_dosaham = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ragu_dosham = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    horoscope_hints = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    didi = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    #place_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nalikai = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dasa_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    lagnam_didi = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    calc_chevvai_dhosham = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    calc_raguketu_dhosham = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    time_of_birth = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = models.Horoscope
        fields = ('profile_id','time_of_birth','place_of_birth', 'birthstar_name', 'birth_rasi_name','lagnam_didi','chevvai_dosaham','ragu_dosham','nalikai','dasa_name','dasa_balance','horoscope_hints','rasi_kattam','amsa_kattam','didi','calc_chevvai_dhosham','calc_raguketu_dhosham')
        
class FamilydetaiSerializer(serializers.ModelSerializer):

    property_details = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    property_worth = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    #suya_gothram = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    uncle_gothram = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    ancestor_origin = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about_family = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    weight = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    eye_wear = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    body_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_value = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_status = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    father_occupation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_occupation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about_self = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    hobbies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blood_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    Pysically_changed = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    no_of_brother = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    no_of_sister = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    no_of_bro_married = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    no_of_sis_married = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    family_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    no_of_children = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    father_alive = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_alive = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    Physically_challenged_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = models.Familydetails
        fields = ('profile_id','father_name', 'father_occupation', 'mother_name','mother_occupation','family_name','about_self','hobbies','blood_group','Pysically_changed','no_of_brother','no_of_sister','no_of_bro_married','no_of_sis_married','family_type','family_value','family_status','property_details','property_worth','suya_gothram','uncle_gothram','ancestor_origin','about_family','weight','eye_wear','body_type','no_of_children','madulamn','father_alive','mother_alive','Physically_challenged_details')
               
class EdudetailSerializer(serializers.ModelSerializer):

    career_plans = serializers.CharField(required=False, allow_blank=True ,allow_null=True)
    degree = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    ug_degeree = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    work_place = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_pincode = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_district = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about_edu   = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    anual_income = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    actual_income = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    work_country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    field_ofstudy = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    currency = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    company_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    designation = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    profession_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    business_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    business_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nature_of_business = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    other_degree = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = models.Edudetails
        fields = ('profile_id','highest_education','field_ofstudy','degree','ug_degeree', 'about_edu','profession','anual_income','actual_income','work_country','work_state','work_city','work_district','work_pincode','work_place','career_plans','currency','company_name', 'designation', 'profession_details', 'business_name','business_address', 'nature_of_business','other_degree')

class PartnerprefSerializer(serializers.ModelSerializer):

    pref_marital_status = serializers.CharField(required=False, allow_blank=True)
    pref_profession = serializers.CharField(required=False, allow_blank=True)
    pref_education = serializers.CharField(required=False, allow_blank=True)
    pref_anual_income = serializers.CharField(required=False, allow_blank=True)
    pref_chevvai = serializers.CharField(required=False, allow_blank=True)
    pref_ragukethu = serializers.CharField(required=False, allow_blank=True)
    pref_foreign_intrest = serializers.CharField(required=False, allow_blank=True)
    pref_porutham_star = serializers.CharField(required=False, allow_blank=True)
    pref_porutham_star_rasi = serializers.CharField(required=False, allow_blank=True)
    pref_height_from = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pref_height_to = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pref_anual_income_max  = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pref_fieldof_study = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = models.Partnerpref
        fields = ('profile_id','pref_age_differences','pref_height_from', 'pref_height_to', 'pref_marital_status','pref_profession','pref_education','pref_anual_income','pref_chevvai','pref_ragukethu','pref_foreign_intrest','pref_porutham_star','pref_porutham_star_rasi','pref_anual_income_max','status','pref_fieldof_study')


class PlanSerializer(serializers.Serializer):    
    id = serializers.IntegerField()
    plan_name = serializers.CharField(max_length=200)
    plan_price = serializers.DecimalField(max_digits=10, decimal_places=2)  
    plan_renewal_cycle = serializers.CharField(max_length=100)
    plan_status = serializers.IntegerField()



class SavedetailsSerializer(serializers.Serializer):
    
    profile_id = serializers.CharField(required=True, allow_blank=False)
    page_id = serializers.CharField(required=True, allow_blank=False)


class LoginWithMobileSerializer(serializers.Serializer):
    Mobile_no = serializers.CharField(max_length=50)

class VerifyOtpSerializer(serializers.Serializer):
    Mobile_no = serializers.CharField(max_length=50)
    Otp = serializers.CharField(max_length=10)


 
class ExpressintrSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 
    to_express_message = serializers.CharField(allow_blank=True, required=False) 

    class Meta:
        model = models.Express_interests
        fields = ('profile_id','profile_to','status','to_express_message')

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        # print('profile_from',validated_data['profile_from'])
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        validated_data['req_datetime'] = timezone.now()   # No accept time by default
        print('savetime',timezone.now())
        print('date',timezone.now().date())
        # current_date = current_time.date()
        return super().create(validated_data)
    
class Update_ExpressintrSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 

    class Meta:
        model = models.Express_interests
        fields = ('profile_id','profile_from','status')

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        validated_data['response_datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)

    def update(self, instance, validated_data):
            instance.profile_from = validated_data.get('profile_from', instance.profile_from)
            instance.status = validated_data.get('status', instance.status)
            instance.response_datetime = timezone.now()  # Set the response_datetime to the current time
            instance.save()
            int_mesage=''
            cta=''
            message_titile=''

            status=int(validated_data.get('status'))
            print('status12345',status)

            #if the status is 3 the request is rejected if the status is 2 the request is accepted

            if(status==3):
        
                   int_mesage='Your express interests was rejected from profile ID '+validated_data.get('profile_from')
                   cta='NULL'
                   message_titile=validated_data.get('profile_from')+' has rejected your express intrest'
            if(status==2):
        
                   int_mesage='Your express interests was Accepted from profile ID '+validated_data.get('profile_from')
                   cta='Message'
                   message_titile=validated_data.get('profile_from')+' has accepted your express intrest'

            print(message_titile,'message_titile')
            profile_from=validated_data.get('profile_from')
            profile_to=validated_data.get('profile_id')

            to_profile=models.Registration1.objects.get(ProfileId=profile_from)
            to_profile_name=to_profile.Profile_name
            to_profile_email=to_profile.EmailId
                    
            from_profile=models.Registration1.objects.get(ProfileId=profile_to)
            from_profile_name=from_profile.Profile_name
                    
            choosen_medium=from_profile.Notifcation_enabled
                                
                                
            if(choosen_medium):
                                                            
                        chosen_alert_types = [int(alert_type) for alert_type in choosen_medium.split(',')]
                                        
                        # Fetch alert settings based on chosen_alert_types
                        alert_settings = models.ProfileAlertSettings.objects.filter(id__in=chosen_alert_types,notification_type='express_interests' , status=1)
                        
                        # print(alert_settings)
                        
                        send_email = False
                        send_sms = False
                        notification_type='express_interests_update'

                        for alert_setting in alert_settings:
                            if alert_setting.alert_type == 1:  # Assuming '1' is for email
                                send_email = True
                            # elif alert_setting.alert_type == 2:  # Assuming '2' is for SMS
                            #     send_sms = True

                        # print('send_email',send_email)
                        # print('send_sms',send_sms)

                        if send_email:
                            send_email_notification(profile_from,from_profile_name,to_profile_name,to_profile_email, message_titile, int_mesage,notification_type)

                        print('send email success')

                        models.Profile_notification.objects.create(
                                profile_id=validated_data.get('profile_from'),
                                from_profile_id=validated_data.get('profile_id'),
                                notification_type='express_interests_accept',
                                message_titile=message_titile,
                                to_message=int_mesage,
                                is_read=0,
                                created_at=timezone.now()
                            )


            return instance


class PhotorequestSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 

    class Meta:
        model = models.Photo_request
        fields = ('profile_id','profile_to','status')

    def validate_profile_id(self, value):

        print("validate erro messages ")
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        print('profile_from',validated_data['profile_from'])
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        validated_data['req_datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)
    

class Update_PhotorequestSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(write_only=True)
    response_message = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = models.Photo_request
        fields = ('profile_id', 'profile_from', 'status', 'response_message')

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def validate(self, attrs):
        status = attrs.get('status')
        response_message = attrs.get('response_message')

        if status == 3 and not response_message:
            raise serializers.ValidationError({
                'response_message': 'This field is required when status is 3.'
            })

        return attrs
    
    def create(self, validated_data):
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        validated_data['response_datetime'] = timezone.now()  # Set current time as response_datetime
        return super().create(validated_data)

    def update(self, instance, validated_data):

        instance.profile_from = validated_data.get('profile_from', instance.profile_from)
        instance.status = validated_data.get('status', instance.status)
        instance.response_datetime = timezone.now()  # Set the response_datetime to the current time
        instance.response_message = validated_data.get('response_message', instance.response_message)
        int_mesage=''
        message_titile=''
        status=validated_data.get('status')

        print('status',status)
        instance.save()
        

        if(status=='3'):
        
            int_mesage='Your Photo request was rejected from profile ID '+validated_data.get('profile_from')
            message_titile='Rejected the photo request'
        if(status=='2'):
        
            int_mesage='Your Photo request was Accepted from profile ID '+validated_data.get('profile_from')
            message_titile='Accepted the photo request'
            

        models.Profile_notification.objects.create(
                    profile_id=validated_data.get('profile_from'),
                    from_profile_id=validated_data.get('profile_id'),
                    notification_type='photo_request',
                    message_titile=message_titile,
                    to_message=int_mesage,
                    is_read=0,
                    created_at=timezone.now()
                )




       
        return instance
            





# class Profile_idValidationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Registration1
#         fields = ('profile_id')
#     def validate_profile_id(self, value):
#         if not models.Registration1.objects.filter(ProfileId=value).exists():
#             raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
#         return value

class Profile_idValidationSerializer(serializers.Serializer):
    profile_id = serializers.CharField(max_length=20)

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
class Profile_toValidationSerializer(serializers.Serializer):
    profile_to = serializers.CharField(max_length=20)
    profile_id = serializers.CharField(max_length=20)

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    def validate_profile_to(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value



class ProfileDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1
        fields = '__all__'


class ProfileWishlistSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 

    class Meta:
        model = models.Profile_wishlists
        fields = ('profile_id','profile_to','status')

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        print('profile_from',validated_data['profile_from'])
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        validated_data['marked_datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)
    
class CreatevistsSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 

    class Meta:
        model = models.Profile_visitors
        fields = ('profile_id','viewed_profile')

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        #validated_data['datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)
    


class CreatepnotesSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 

    class Meta:
        model = models.Profile_personal_notes
        fields = ('profile_id','profile_to','notes')

    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        #validated_data['datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)

class GetproflistSerializer(serializers.ModelSerializer):

    print("Execution time before loop ",datetime.now())
    
    profile_id = serializers.CharField(write_only=True)
    profile_id_out = serializers.SerializerMethodField()

    class Meta:
        model = models.Get_profiledata
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
            if not models.Registration1.objects.filter(ProfileId=value).exists():
                raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
            return value
    

class GetproflistSerializer_details(serializers.ModelSerializer):
  
    profile_id = serializers.CharField(write_only=True)
    profile_id_out = serializers.SerializerMethodField()
    user_profile_id = serializers.CharField(write_only=True)

    class Meta:
        model = models.Get_profiledata
        fields = ('profile_id', 'profile_id_out','user_profile_id')

    # def validate_profile_id(self, value):
    #     if not models.Registration1.objects.filter(ProfileId=value).exists():
    #         raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
    #     return value

    # the below code is to check the ProfileId id field against the profile_id
    def get_profile_id_out(self, obj):
        return obj.ProfileId
    
    def validate_profile_id(self, value):
            #profile_id = data.get('profile_id')
            if not models.Registration1.objects.filter(ProfileId=value).exists():
                raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
            return value

    def validate_user_profile_id(self, value):
            #profile_id = data.get('profile_id')
            if not models.Registration1.objects.filter(ProfileId=value).exists():
                raise serializers.ValidationError(f"View Profile with ID {value} does not exist.")
            return value
    

class PhotobypasswordSerializer(serializers.ModelSerializer):
    profile_id = serializers.CharField(write_only=True)  # Your own profile ID
    profile_to = serializers.CharField(write_only=True)  # Opposite gender profile ID
    photo_password = serializers.CharField(write_only=True)

    class Meta:
        model = models.Registration1
        fields = ('profile_id', 'profile_to', 'photo_password')
    
    def validate_profile_id(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value

    def validate_profile_to(self, value):
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value

    def validate(self, data):
        profile_to = data.get('profile_to')
        photo_password = data.get('photo_password')
        
        # Validate that the profile_to exists with the correct photo_password
        if not models.Registration1.objects.filter(ProfileId=profile_to, Photo_password=photo_password).exists():
            raise serializers.ValidationError("Invalid photo password for the given profile ID.")
        
        return data



class ExpressInterestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Express_interests
        fields = ['id', 'profile_from', 'profile_to', 'req_datetime', 'response_datetime', 'status']

class PersonalnotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile_personal_notes
        fields = ['id', 'profile_id', 'profile_to', 'notes', 'datetime', 'status']



class MatchingscoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MatchingStarPartner
        fields = ['id', 'gender', 'source_star_id', 'source_rasi_id', 'dest_star_id', 'dest_rasi_id', 'match_count','matching_porutham']


    

class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image_Upload
        fields = ['id', 'profile_id', 'image', 'uploaded_at']

class ReadNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile_notification
        fields = ['profile_id']



class ChangePasswordSerializer(serializers.Serializer):
    ProfileId = serializers.CharField(max_length=50)
    old_password = serializers.CharField(max_length=20)
    new_password = serializers.CharField(max_length=20)
    Re_enter_new_password = serializers.CharField(max_length=20)

    def validate(self, data):
        # Ensure new passwords match
        if data['new_password'] != data.get('Re_enter_new_password'):
            raise serializers.ValidationError({
                'Re_enter_new_password': 'New passwords and re-enter new password do not match.'
            })
        
        # Optional: Add additional validations for password requirements (length, complexity, etc.)
        return data
    


class CustomAddOnPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Addonpackages
        fields = '__all__'  



class PersonalRegistrationSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    #Profile_for=serializers.CharField(required=False, allow_blank=True , allow_null=True)
    
    class Meta:
        model = models.Registration1
        fields = ['ProfileId','Profile_name', 'Gender', 'Profile_dob', 'Profile_height', 'Profile_marital_status', 'Profile_complexion','age','Profile_verified','PaymentExpire','Plan_id','DateOfJoin','Profile_gothras','Video_url','Mobile_no']

    def get_age(self, obj):
        if obj.Profile_dob:
            today = datetime.today()
            age = today.year - obj.Profile_dob.year - ((today.month, today.day) < (obj.Profile_dob.month, obj.Profile_dob.day))
            return age
        return ""


class PersonalHoroscopeSerializer(serializers.ModelSerializer):
    time_of_birth = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    class Meta:
        model = models.Horoscope
        fields = ['place_of_birth', 'time_of_birth','birth_rasi_name','birthstar_name']

class PersonalFamilydetailsSerializer(serializers.ModelSerializer):
    weight = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    eye_wear = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    body_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    blood_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    hobbies = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    about_self = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    Pysically_changed = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    uncle_gothram = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    father_alive = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    mother_alive = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = models.Familydetails
        fields = ['blood_group', 'about_self', 'hobbies', 'Pysically_changed','weight','eye_wear','body_type','suya_gothram','uncle_gothram', 'father_alive', 'mother_alive']


class PersHoroscopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Horoscope
        fields = [ 'birthstar_name', 'birth_rasi_name', 'lagnam_didi', 'chevvai_dosaham', 'ragu_dosham', 'nalikai', 'dasa_name', 'dasa_balance', 'rasi_kattam', 'amsa_kattam']


class PersonalFamilySerializer(serializers.ModelSerializer):
    
    father_name = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    father_occupation = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    mother_name = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    mother_occupation = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    family_status = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    no_of_sister = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    no_of_sis_married = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    no_of_brother = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    no_of_bro_married = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    property_details = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    property_worth = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    about_family = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    ancestor_origin = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    uncle_gothram = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    family_type = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    family_value = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    no_of_children = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    father_alive = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    mother_alive = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    Physically_challenged_details = serializers.CharField(required=False, allow_blank=True , allow_null=True)
    class Meta:
        model = models.Familydetails
        fields = ['father_name','father_occupation','mother_name','mother_occupation','family_status','no_of_sister','no_of_sis_married','no_of_brother','no_of_bro_married','property_details','property_worth','about_family','ancestor_origin','uncle_gothram','family_type','family_value','no_of_children','father_alive','mother_alive','Physically_challenged_details']

class FamilyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Familystatus
        fields = ['status']



class PersonalFamSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.Familydetails
        fields =['suya_gothram','madulamn']


class PersonalEdudetailsSerializer(serializers.ModelSerializer):
    
    about_edu = serializers.CharField(required=False, allow_blank=True)
    work_country = serializers.CharField(required=False, allow_blank=True)
    work_state = serializers.CharField(required=False, allow_blank=True)
    work_city = serializers.CharField(required=False, allow_blank=True)
    work_district = serializers.CharField(required=False, allow_blank=True)
    work_pincode = serializers.CharField(required=False, allow_blank=True)
    career_plans = serializers.CharField(required=False, allow_blank=True)
    work_place = serializers.CharField(required=False, allow_blank=True)

    currency = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    designation = serializers.CharField(required=False, allow_blank=True)
    profession_details = serializers.CharField(required=False, allow_blank=True)
    business_name = serializers.CharField(required=False, allow_blank=True)
    business_address = serializers.CharField(required=False, allow_blank=True)
    nature_of_business = serializers.CharField(required=False, allow_blank=True)
    other_degree = serializers.CharField(required=False, allow_blank=True)
    field_ofstudy = serializers.CharField(required=False, allow_blank=True)
    degree = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = models.Edudetails
        fields = ['highest_education', 'about_edu', 'profession', 'anual_income', 'actual_income', 'work_country', 'work_state', 'work_district','work_city', 'work_pincode', 'career_plans','work_place','currency','company_name','designation','profession_details','business_name','business_address','nature_of_business','other_degree','field_ofstudy','degree']

class Registration1ContactSerializer(serializers.ModelSerializer):
    
    Profile_district= serializers.CharField(required=False, allow_blank=True ,allow_null=True)
    Profile_address= serializers.CharField(required=False, allow_blank=True ,allow_null=True)
    Profile_city= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    Profile_state= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    Profile_pincode= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    Profile_alternate_mobile= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    Profile_mobile_no= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    Profile_whatsapp= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    Profile_emailid= serializers.CharField(required=False, allow_blank=True,allow_null=True)
    class Meta:
        model = models.Registration1
        fields = ['Profile_address','Profile_district','Profile_city', 'Profile_state', 'Profile_country', 'Profile_pincode', 'Profile_alternate_mobile', 'Profile_mobile_no', 'Profile_whatsapp', 'EmailId','Profile_emailid']



class ParPrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Partnerpref
        fields = ['pref_age_differences', 'pref_height_from', 'pref_height_to', 'pref_profession', 'pref_education', 'pref_anual_income', 'pref_chevvai', 'pref_ragukethu', 'pref_foreign_intrest','pref_porutham_star_rasi','pref_porutham_star','pref_marital_status','pref_anual_income_max','pref_fieldof_study']



class UpdatePhotoPasswordSerializer(serializers.Serializer):
    profile_id = serializers.CharField(max_length=50)
    photo_password = serializers.CharField(max_length=255 ,required=False, allow_blank=True)
    photo_protection = serializers.BooleanField(required=True)  


class PhotoProtectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1
        fields = ['Photo_protection']


class CustomProfessionSerializer(serializers.ModelSerializer):
    profession_id = serializers.SerializerMethodField()
    profession_name = serializers.SerializerMethodField()

    class Meta:
        model = models.MasterProfession
        fields = ['profession_id', 'profession_name']

    def get_profession_id(self, obj):
        return obj.id

    def get_profession_name(self, obj):
        return obj.profession
    






class CustomProfessionSerializer(serializers.ModelSerializer):
    profession_id = serializers.SerializerMethodField()
    profession_name = serializers.SerializerMethodField()

    class Meta:
        model = models.MasterProfession
        fields = ['profession_id', 'profession_name']

    def get_profession_id(self, obj):
        return obj.id

    def get_profession_name(self, obj):
        return obj.profession
    


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    profile_id = serializers.CharField(max_length=50, required=False)

    def validate(self, data):
        email = data.get('email')
        profile_id = data.get('profile_id')

        if not email and not profile_id:
            raise serializers.ValidationError("Either email or profile_id must be provided.")
        
        if email:
            if not models.Registration1.objects.filter(EmailId=email).exists():
                raise serializers.ValidationError("Invalid email.")
        if profile_id:
            if not models.Registration1.objects.filter(ProfileId=profile_id).exists():
                raise serializers.ValidationError("Invalid profile_id.")
        
        return data


class ResetPasswordSerializer(serializers.Serializer):
    profile_id = serializers.CharField(max_length=50)
    #otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError("The new password and confirm password do not match.")
        
        return data
    


class VysassistrequestSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 
    to_message = serializers.CharField(allow_blank=True, required=False) 

    class Meta:
        model = models.Profile_vysassist
        fields = ('profile_id','profile_to','status','to_message')

    def validate_profile_id(self, value):

        print("validate erro messages ")
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        #print('profile_from',validated_data['profile_from'])
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        validated_data['req_datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)

class CallactionSerializer(serializers.ModelSerializer):
    
    profile_id = serializers.CharField(write_only=True) 

    class Meta:
        model = models.Profile_callogs
        fields = ('profile_id','profile_to')

    def validate_profile_id(self, value):

        print("validate erro messages ")
        if not models.Registration1.objects.filter(ProfileId=value).exists():
            raise serializers.ValidationError(f"Profile with ID {value} does not exist.")
        return value
    
    def create(self, validated_data):
        # Automatically set the default values for status and accept_datetime
        #validated_data['profile_from'] = validate_profile_id
        profile_id = validated_data.pop('profile_id')
        validated_data['profile_from'] = profile_id 
        #print('profile_from',validated_data['profile_from'])
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        validated_data['req_datetime'] = timezone.now()   # No accept time by default
        return super().create(validated_data)
    
class SuccessStoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SuccessStory
        fields = ['couple_name', 'photo','details']


class AwardListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Award
        fields = ['name', 'image', 'description']






class TestimonialListSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    class Meta:
        model = models.Testimonial
        fields = ['profile_id', 'rating', 'review_content', 'user_image', 'date']

    def get_date(self, obj):
        return obj.date.strftime('%b %d, %Y')


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Page
        fields = ['id', 'page_name', 'meta_title', 'meta_description', 'meta_keywords', 'status', 'content']


class AdminSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AdminSettings
        fields = '__all__'


class ProfileImagesSerializer(serializers.Serializer):
    horoscope_file = serializers.SerializerMethodField()
    Profile_divorceproof = serializers.SerializerMethodField()
    Profile_idproof = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    Video_url = serializers.SerializerMethodField()
    Photo_protection = serializers.SerializerMethodField()
    Photo_password = serializers.SerializerMethodField()
    
    base_url =settings.MEDIA_URL

    class Meta:
        fields = ['horoscope_file', 'Profile_idproof', 'Profile_divorceproof','images','Video_url','Photo_protection','Photo_password']

    def get_horoscope_file(self, obj):
        try:
            # Fetch the horoscope image for the given profile
            horoscope = models.Horoscope.objects.get(profile_id=obj)
            # return horoscope.horoscope_file.url if horoscope.horoscope_file else None
            return f"{horoscope.horoscope_file.url}" if horoscope.horoscope_file else None
        except models.Horoscope.DoesNotExist:
            return None

    def get_Profile_idproof(self, obj):
        try:
            # Fetch the profile image from LoginDetails for the given profile
            login_details = models.Registration1.objects.get(ProfileId=obj)
            # return login_details.Profile_idproof.url if login_details.Profile_idproof else None
            # return f"{self.base_url}{login_details.Profile_idproof.url}" if login_details.Profile_idproof else None
            return f"{login_details.Profile_idproof.url}" if login_details.Profile_idproof else None
        except models.LoginDetails.DoesNotExist:
            return None
    
    def get_Profile_divorceproof(self, obj):
        try:
            # Fetch the Profile_divorceproof from LoginDetails for the given profile
            login_details = models.Registration1.objects.get(ProfileId=obj)
            # return login_details.Profile_divorceproof.url if login_details.Profile_divorceproof else None
            # return f"{self.base_url}{login_details.Profile_divorceproof.url}" if login_details.Profile_divorceproof else None
            return f"{login_details.Profile_divorceproof.url}" if login_details.Profile_divorceproof else None
        except models.LoginDetails.DoesNotExist:
            return None
    
    def get_Photo_protection(self, obj):
        try:
            profile_details = models.Registration1.objects.get(ProfileId=obj)
            return f"{profile_details.Photo_protection}"
        except models.Registration1.DoesNotExist:
            return None
        
    def get_Photo_password(self, obj):
        try:
            profile_details = models.Registration1.objects.get(ProfileId=obj)
            return f"{profile_details.Photo_password}"
        except Exception:
            return None
    
    def get_Video_url(self, obj):
        try:
            profile_details = models.Registration1.objects.get(ProfileId=obj)
            return f"{profile_details.Video_url}"
        except models.Registration1.DoesNotExist:
            return None
    
    def get_images(self, obj):
        # print('435345')
        try:
            # Fetch all images related to the profile from the Images table
            images = models.Image_Upload.objects.filter(profile_id=obj)
            
            #print(images) 
            
            #return [{"image_file": img.image} for img in images if img.image]
            # return [{"image_file": img.image.url} for img in images if img.image]
            # return [{"image_file": f"{self.base_url}{img.image.url}","image_name": f"{img.image.url}","image_id": f"{img.id}"} for img in images if img.image]
            return [{"image_file": f"{img.image.url}","image_name": f"{img.image.url}","image_id": f"{img.id}"} for img in images if img.image]
        except models.Image_Upload.DoesNotExist:
            
            # print('1234')
            return None


class HomepageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Homepage
        fields = ['id', 'why_vysyamala', 'youtube_links', 'vysyamala_apps']


class PlanFeatureLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlanFeatureLimit
        fields = '__all__'

class DistrictprefSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Districtpref
        fields = ['id', 'district', 'is_deleted']

class ProfileVisibilityListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProfileVisibility
        fields = '__all__'

class ProfileVisibilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ProfileVisibility
        fields = ('profile_id', 'visibility_age_from', 'visibility_age_to' ,'visibility_height_from', 'visibility_height_to', 
                  'visibility_profession', 'visibility_education', 'visibility_anual_income', 'visibility_chevvai',
                  'visibility_ragukethu', 'visibility_foreign_interest','status','visibility_anual_income_max','degree','visibility_field_of_study','visibility_family_status')
        
class ProfileVysAssistFollowupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProfileVysAssistFollowup
        fields = ['comments', 'update_at']

class WithoutAddressEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentWithoutAddressEmailLog
        fields = '__all__'


class SentWithoutAddressPrintPDFLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentWithoutAddressPrintPDFLog
        fields = '__all__'  # Includes all fields