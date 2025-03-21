from rest_framework import serializers
from . import models
import random
from django.utils import timezone
from datetime import datetime


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

            # verify_otp.status = 1

            # verify_otp.save()

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
        if models.Registration1.objects.filter(EmailId=EmailId,status=1).exists():
            raise serializers.ValidationError("This email is already registered.")
        return EmailId

    def validate_Mobile_no(self, Mobile_no):
        print('Mobile_no',Mobile_no)
        if models.Registration1.objects.filter(Mobile_no=Mobile_no,status=1).exists():
            raise serializers.ValidationError("This mobile number is already registered.")
        return Mobile_no
    def validate(self, data):
     
     #data['Otp']='142024'
     data['ProfileId']=''.join(random.choices('0123456789', k=6))
     data['Otp'] = random.randint(100000, 999999)
     #data['Otp'] = 123456
     data['status']=0

     return data


     
class Registration2Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1
        fields = ('ProfileId','Profile_name', 'Profile_marital_status', 'Profile_dob', 'Profile_height', 'Profile_complexion')


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1
        fields = ('ProfileId','Profile_address','Profile_country', 'Profile_state', 'Profile_city','Profile_pincode','Profile_alternate_mobile','Profile_whatsapp','Profile_mobile_no')
        
    
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

    class Meta:
        model = models.Profilecountry
        fields = ['country_id', 'country_name']

    def get_country_id(self, obj):
        return obj.id
    
    def get_country_name(self, obj):
        return obj.name
    

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
        model = models.Profilestate
        fields = ['city_id', 'city_name']

    #def validate(self, data):
        
    def get_city_id(self, obj):
        return obj.id
    
    def get_city_name(self, obj):
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
    birth_star_id = serializers.IntegerField()
    gender = serializers.CharField(max_length=10)

class MatchingStarSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    #gender = serializers.CharField(max_length=10)
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
    
    rasi_kattam = serializers.CharField(required=False, allow_blank=True)
    amsa_kattam = serializers.CharField(required=False, allow_blank=True)
    chevvai_dosaham = serializers.CharField(required=False, allow_blank=True)
    ragu_dosham = serializers.CharField(required=False, allow_blank=True)


    
    class Meta:
        model = models.Horoscope
        fields = ('profile_id','time_of_birth','place_of_birth', 'birthstar_name', 'birth_rasi_name','lagnam_didi','chevvai_dosaham','ragu_dosham','nalikai','dasa_name','dasa_balance','horoscope_hints','rasi_kattam','amsa_kattam')
        
class FamilydetaiSerializer(serializers.ModelSerializer):

    property_details = serializers.CharField(required=False, allow_blank=True)
    property_worth = serializers.CharField(required=False, allow_blank=True)
    suya_gothram = serializers.CharField(required=False, allow_blank=True)
    uncle_gothram = serializers.CharField(required=False, allow_blank=True)
    ancestor_origin = serializers.CharField(required=False, allow_blank=True)
    about_family = serializers.CharField(required=False, allow_blank=True)



    class Meta:
        model = models.Familydetails
        fields = ('profile_id','father_name', 'father_occupation', 'mother_name','mother_occupation','family_name','about_self','hobbies','blood_group','Pysically_changed','no_of_brother','no_of_sister','no_of_bro_married','no_of_sis_married','family_type','family_value','family_status','property_details','property_worth','suya_gothram','uncle_gothram','ancestor_origin','about_family')
               
class EdudetailSerializer(serializers.ModelSerializer):

    career_plans = serializers.CharField(required=False, allow_blank=True)
    ug_degeree = serializers.CharField(required=False, allow_blank=True)


    class Meta:
        model = models.Edudetails
        fields = ('profile_id','highest_education', 'ug_degeree', 'about_edu','profession','anual_income','actual_income','work_country','work_state','work_city','work_pincode','career_plans','status')

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


    class Meta:
        model = models.Partnerpref
        fields = ('profile_id','pref_age_differences','pref_height_from', 'pref_height_to', 'pref_marital_status','pref_profession','pref_education','pref_anual_income','pref_chevvai','pref_ragukethu','pref_foreign_intrest','pref_porutham_star','pref_porutham_star_rasi','status')


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
        print('profile_from',validated_data['profile_from'])
        validated_data['status'] = '1'  # Default status to '1' (request sent)
        validated_data['req_datetime'] = timezone.now()   # No accept time by default
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

            status=validated_data.get('status')

            #if the status is 3 the request is rejected if the status is 2 the request is accepted

            if(status==3):
        
                   int_mesage='Your express interests was rejected from profile ID '+validated_data.get('profile_from')
                   cta='NULL'
                   message_titile=' has rejected your express intrest'
            if(status==2):
        
                   int_mesage='Your express interests was Accepted from profile ID '+validated_data.get('profile_from')
                   cta='Message'
                   message_titile=' has accepted your express intrest'
            

            models.Profile_notification.objects.create(
                    profile_id=validated_data.get('profile_from'),
                    from_profile_id=validated_data.get('profile_id'),
                    notification_type='express_interests',
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

    class Meta:
        model = models.Registration1
        fields = ['Profile_name', 'Gender', 'Profile_dob', 'Profile_height', 'Profile_marital_status', 'Profile_complexion', 'Profile_for', 'age']

    def get_age(self, obj):
        if obj.Profile_dob:
            today = datetime.today()
            age = today.year - obj.Profile_dob.year - ((today.month, today.day) < (obj.Profile_dob.month, obj.Profile_dob.day))
            return age
        return ""


class PersonalHoroscopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Horoscope
        fields = ['place_of_birth', 'time_of_birth']

class PersonalFamilydetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Familydetails
        fields = ['blood_group', 'about_self', 'hobbies', 'Pysically_changed']


class PersHoroscopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Horoscope
        fields = [ 'birthstar_name', 'birth_rasi_name', 'lagnam_didi', 'chevvai_dosaham', 'ragu_dosham', 'nalikai', 'dasa_name', 'dasa_balance', 'rasi_kattam', 'amsa_kattam']


class PersonalFamilySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Familydetails
        fields = ['father_name','father_occupation','mother_name','mother_occupation','family_status','no_of_sister','no_of_sis_married','no_of_brother','no_of_bro_married','property_details','about_family']

class FamilyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Familystatus
        fields = ['status']



class PersonalFamSerilizer(serializers.ModelSerializer):
    class Meta:
        model = models.Familydetails
        fields =['suya_gothram']


class PersonalEdudetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Edudetails
        fields = ['highest_education', 'about_edu', 'profession', 'anual_income', 'actual_income', 'work_country', 'work_state', 'work_city', 'work_pincode', 'career_plans']

class Registration1ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Registration1
        fields = ['Profile_address', 'Profile_city', 'Profile_state', 'Profile_country', 'Profile_pincode', 'Profile_alternate_mobile', 'Profile_mobile_no', 'Profile_whatsapp', 'EmailId']



class ParPrefSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Partnerpref
        fields = ['pref_age_differences', 'pref_height_from', 'pref_height_to', 'pref_profession', 'pref_education', 'pref_anual_income', 'pref_chevvai', 'pref_ragukethu', 'pref_foreign_intrest']



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
    otp = serializers.CharField(max_length=6)
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





class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Room
        fields = ['id']