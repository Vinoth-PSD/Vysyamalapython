from django.db import models ,connection
import os
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from rest_framework.views import status
from django.conf import settings
from .storages import AzureMediaStorage


class ProfileStatus(models.Model):
    status_code = models.IntegerField(primary_key=True)  
    status_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'masterprofilestatus'
        managed = False  

class ProfileSubStatus(models.Model):
    id = models.IntegerField(primary_key=True)  
    status_code = models.IntegerField()
    sub_status_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'masterprofilestatus_sub'
        managed = False  


class Mode(models.Model):
    mode = models.AutoField(db_column='Mode', primary_key=True)  # Field 'Mode' as the primary key
    mode_name = models.CharField(db_column='ModeName', max_length=50)  # Field 'ModeName'
    is_deleted = models.BooleanField(default=False)  # Soft delete flag

    def __str__(self):
        return self.mode_name

    class Meta:
        db_table = 'mastermode'  # Ensure this matches your actual table name



class Property(models.Model):
    property = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return self.property

    class Meta:
        db_table = 'masterpropertyworth'  # Change this to the actual SQL table name


class Gothram(models.Model):
    gothram_name = models.CharField(max_length=255)
    rishi = models.CharField(max_length=255)
    sanketha_namam = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return self.gothram_name

    class Meta:
        db_table = 'mastergothram'  # Replace this with the actual table name


class EducationLevel(models.Model):
    row_id = models.AutoField(db_column='RowId', primary_key=True)  # Map RowId to row_id and set as primary key
    EducationLevel = models.CharField(max_length=200, null=True, blank=True)  # Matches varchar(200) with NULL
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return self.row_id  
    class Meta:
        db_table = 'mastereducation'  # Ensure this matches your actual table name


class Profession(models.Model):
    row_id = models.AutoField(db_column='RowId', primary_key=True)  # Map RowId as primary key
    profession = models.CharField(max_length=200, null=True, blank=True)  # Matches varchar(200) with NULL
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return self.profession or 'No Profession'

    class Meta:
        db_table = 'masterprofession'  # Ensure this matches your actual table name



class Match(models.Model):
    gender = models.CharField(max_length=50)
    source_star_id = models.IntegerField()
    source_rasi_id = models.IntegerField()
    dest_star_id = models.IntegerField()
    dest_rasi_id = models.IntegerField()
    match_count = models.IntegerField()
    matching_porutham = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.gender} Match"  # Corrected string formatting

    class Meta:
        db_table = 'matching_stars_partner'


class MasterStatePref(models.Model):
    state = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)  # For soft delete
    

    def __str__(self):
        return self.state

    class Meta:
        db_table = 'masterstatepref'

class Country(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'mastercountry'


# class State(models.Model):
#     name = models.CharField(max_length=100)
#     country = models.ForeignKey(Country, related_name='states', on_delete=models.CASCADE)
#     is_active = models.BooleanField(default=True)
#     is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

#     def __str__(self):
#         return self.name

#     class Meta:
#         db_table = 'masterstate'

class State(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterstate'


class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, related_name='districts', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterdistrict'
        
class City(models.Model):
    district = models.ForeignKey(District, related_name='cities', on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.city_name

    class Meta:
        db_table = 'mastercity'  # Match the table name in your database



class ProfileHolder(models.Model):
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)  # daughter, son, friend, etc.

    def __str__(self):
        return f"{self.name} ({self.relation})"

    class Meta:
        db_table = 'masterprofileholder'

class MaritalStatus(models.Model):
    StatusId = models.AutoField(primary_key=True)  # StatusId as the primary key
    MaritalStatus = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.MaritalStatus

    class Meta:
        db_table = 'maritalstatusmaster'


class Height(models.Model):
    height_id = models.AutoField(primary_key=True)  # Use height_id as the primary key
    height_desc = models.CharField(max_length=200)
    height_value = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete field

    def __str__(self):
        return str(self.height_desc)

    class Meta:
        db_table = 'heightmaster'


class Complexion(models.Model):
    complexion_id = models.AutoField(primary_key=True)
    complexion_desc = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.complexion_desc

    class Meta:
        db_table = 'complexionmaster'


class ParentsOccupation(models.Model):
    occupation = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.occupation

    class Meta:
        db_table = 'masterparentsoccupation'


class HighestEducation(models.Model):
    degree = models.CharField(max_length=100)

    def __str__(self):
        return self.degree

    class Meta:
        db_table = 'masterhighesteducation'

class UgDegree(models.Model):
    id    = models.SmallIntegerField(primary_key=True)
    degree = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.degree

    class Meta:
        db_table = 'masterugdegree'


class AnnualIncome(models.Model):
    income = models.CharField(max_length=50)
    income_amount = models.CharField(max_length=50)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return str(self.income)

    class Meta:
        db_table = 'masterannualincome'



class BirthStar(models.Model):
    star = models.CharField(max_length=100) 
    tamil_series = models.CharField(max_length=200) 
    telugu_series = models.CharField(max_length=200) 
    kannada_series = models.CharField(max_length=200) 
    is_deleted = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.star

    class Meta:
        db_table = 'masterbirthstar'

class Rasi(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterrasi'

class Lagnam(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterlagnam'

class DasaBalance(models.Model):
    balance = models.CharField(max_length=100)

    def __str__(self):
        return self.balance

    class Meta:
        db_table = 'masterdasabalance'

class FamilyType(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterfamilytype'


class FamilyStatus(models.Model):
    status = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.status

    class Meta:
        db_table = 'masterfamilystatus'



class FamilyValue(models.Model):
    FamilyValueid = models.AutoField(primary_key=True)
    FamilyValue = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.FamilyValue

    class Meta:
        db_table = 'masterfamilyvalue'

        

class LoginDetailsTemp(models.Model):
    ContentId = models.AutoField(primary_key=True)
    ProfileId = models.CharField(max_length=50, null=True)
    LoginId = models.CharField(max_length=50, null=True)
    Profile_for = models.CharField(max_length=50, null=True)
    Gender = models.CharField(max_length=100, null=True)
    Mobile_no = models.CharField(max_length=50, null=True)
    EmailId = models.CharField(max_length=100, null=True)
    Password = models.CharField(max_length=20, null=True)
    Profile_name = models.CharField(max_length=250)
    Profile_marital_status = models.CharField(max_length=100, null=True)
    Profile_dob = models.DateField(null=True)
    Profile_height = models.CharField(max_length=250)
    Profile_complexion = models.CharField(max_length=100, null=True)
    Otp = models.IntegerField(null=True)
    Stage = models.PositiveSmallIntegerField(null=True)
    AdminPermission = models.PositiveSmallIntegerField(null=True)
    Payment = models.CharField(max_length=10, null=True)
    PaymentExpire = models.DateTimeField(null=True)
    PaymentType = models.CharField(max_length=255, null=True)
    status = models.IntegerField(null=True)
    DateOfJoin = models.DateField(null=True)



    class Meta:
        db_table = 'logindetails_temp'
        
        

from django.db import models

class Profile(models.Model):
    matrimonyProfile = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    mobileNumber = models.CharField(max_length=15)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    maritalStatus = models.CharField(max_length=50)
    dateOfBirth = models.DateField()
    name = models.CharField(max_length=100)
    complexion = models.CharField(max_length=50)
    address = models.TextField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    alternateMobileNumber = models.CharField(max_length=15)
    daughterMobileNumber = models.CharField(max_length=15)
    daughterEmail = models.EmailField()
    fatherName = models.CharField(max_length=100)
    fatherOccupation = models.CharField(max_length=100)
    motherName = models.CharField(max_length=100)
    motherOccupation = models.CharField(max_length=100)
    familyName = models.CharField(max_length=100)
    aboutMyself = models.TextField()
    hobbies = models.TextField()
    bloodGroup = models.CharField(max_length=10)
    physicallyChallenged = models.CharField(max_length=10)
    propertyDetails = models.TextField()
    propertyWorth = models.CharField(max_length=100)
    suyaGothram = models.CharField(max_length=100)
    uncleGothram = models.CharField(max_length=100)
    ancestorOrigin = models.TextField()
    aboutMyFamily = models.TextField()
    highestEducation = models.CharField(max_length=100)
    ugDegree = models.CharField(max_length=100)
    aboutEducation = models.TextField()
    annualIncome = models.CharField(max_length=100)
    actualIncome = models.CharField(max_length=100)
    workCountry = models.CharField(max_length=100)
    workState = models.CharField(max_length=100)
    workPincode = models.CharField(max_length=10)
    careerPlans = models.TextField()
    timeOfBirth = models.TimeField()
    placeOfBirth = models.CharField(max_length=100)
    birthStar = models.CharField(max_length=100)
    rasi = models.CharField(max_length=100)


# class LoginDetails(models.Model):
#     ContentId = models.AutoField(primary_key=True)
#     ProfileId = models.CharField(max_length=50, unique=True)
#     LoginId = models.CharField(max_length=50, null=True)
#     Profile_for = models.CharField(max_length=50, null=True)
#     Gender = models.CharField(max_length=100, null=True)
#     Mobile_no = models.CharField(max_length=50, null=True)
#     EmailId = models.EmailField()
#     Password = models.CharField(max_length=255)
#     Profile_name = models.CharField(max_length=250, null=True)
#     Profile_marital_status = models.CharField(max_length=100, null=True)
#     Profile_dob = models.DateField(null=True)
#     Profile_alternate_mobile = models.CharField(max_length=200, null=True)
#     Profile_complexion = models.CharField(max_length=100, null=True)
#     Profile_address = models.CharField(max_length=200, null=True)
#     Profile_country = models.CharField(max_length=200, null=True)
#     Profile_state = models.CharField(max_length=200, null=True)
#     Profile_city = models.CharField(max_length=200, null=True)
#     Profile_district = models.CharField(max_length=200, null=True)
#     Profile_pincode = models.CharField(max_length=200, null=True)

#     Profile_whatsapp = models.CharField(max_length=200, null=True)
#     Profile_mobile_no = models.CharField(max_length=200, null=True)
#     Video_url= models.CharField(max_length=255, null=True,blank=True)
#     Profile_idproof = models.CharField(max_length=255,null=True,blank=True)
#     quick_registration=models.CharField(max_length=6, blank=True, null=True)
#     Plan_id= models.CharField(max_length=100 , blank=True, null=True)
#     status= models.CharField(max_length=100 , blank=True, null=True)

#     class Meta:
#         db_table = 'logindetails'

def upload_to_profile_basic(instance, filename):
    return os.path.join('profile_{0}'.format(instance.ProfileId), filename)


def upload_to_profile(instance, filename):
    return os.path.join('profile_{0}'.format(instance.profile_id), filename)

class LoginDetails(models.Model):
    ContentId = models.AutoField(primary_key=True)
    ProfileId = models.CharField(max_length=50, unique=True,null=True,blank=True)
    LoginId = models.CharField(max_length=50,  null=True,blank=True)
    Profile_for = models.CharField(max_length=50, null=True)
    Gender = models.CharField(max_length=100, null=True,blank=True)
    Mobile_no = models.CharField(max_length=50, null=True)
    EmailId = models.EmailField()
    Password = models.CharField(max_length=255)
    Profile_name = models.CharField(max_length=250, null=True , blank=True)
    Profile_marital_status = models.CharField(max_length=100, null=True)
    Profile_dob = models.DateField(null=True)
    Profile_alternate_mobile = models.CharField(max_length=200, null=True)
    Profile_complexion = models.CharField(max_length=100, null=True)
    Profile_address = models.CharField(max_length=200, null=True)
    Profile_country = models.CharField(max_length=200, null=True)
    Profile_state = models.CharField(max_length=200, null=True)
    Profile_city = models.CharField(max_length=200, null=True)
    Profile_district = models.CharField(max_length=200, null=True)
    Profile_pincode = models.CharField(max_length=200, null=True)

    Profile_whatsapp = models.CharField(max_length=200, null=True)
    Profile_mobile_no = models.CharField(max_length=200, null=True)
    Video_url= models.CharField(max_length=255, null=True,blank=True)
    #DateOfJoin = models.DateField(null=True)
    DateOfJoin = models.CharField(max_length=100,null=True,blank=True)
    Last_login_date= models.CharField(max_length=100)  
    # Profile_idproof = models.CharField(max_length=255,null=True,blank=True)
    # Profile_divorceproof = models.CharField(max_length=255,null=True,blank=True)  # Add this field for file upload
    Profile_idproof = models.FileField(upload_to=upload_to_profile_basic,storage=AzureMediaStorage(),blank=True,null=True)
    Profile_divorceproof = models.FileField(upload_to=upload_to_profile_basic,storage=AzureMediaStorage(),blank=True,null=True)
    quick_registration=models.CharField(max_length=6, blank=True, null=True)
    Plan_id= models.CharField(max_length=100 , blank=True, null=True)
    status= models.CharField(max_length=100 , blank=True, null=True)
    Notifcation_enabled= models.CharField(max_length=100 , blank=True, null=True)
    Addon_package= models.CharField(max_length=100 , blank=True, null=True)
    Admin_comments= models.TextField(null=True)
    Admin_comment_date= models.DateTimeField(null=True, blank=True)
    PaymentExpire = models.DateTimeField(max_length=15,blank=True, null=True)  # Changed from CharField to TextField
    membership_startdate = models.DateField(max_length=15,blank=True, null=True)  # Changed from CharField to TextField
    membership_enddate = models.DateField(max_length=15,blank=True, null=True)  # Changed from CharField to TextField
    primary_status = models.IntegerField(blank=True, null=True)
    secondary_status =  models.IntegerField(blank=True, null=True)
    plan_status =  models.IntegerField(blank=True, null=True)
    PaymentType = models.CharField(max_length=255,blank=True, null=True)  # Changed from CharField to TextField
    Package_name= models.CharField(max_length=255,blank=True, null=True)  # Changed from CharField to TextField
    Video_url= models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'logindetails'


class Get_profiledata(models.Model):
   
    @staticmethod
    def get_edit_profile(profile_id):
        query = '''SELECT * FROM logindetails l LEFT JOIN profile_edudetails pe ON pe.profile_id=l.ProfileId LEFT JOIN profile_familydetails pf ON pf.profile_id=l.ProfileId LEFT JOIN profile_horoscope ph ON ph.profile_id=l.ProfileId LEFT JOIN profile_images pi ON pi.profile_id=l.ProfileId LEFT JOIN profile_partner_pref pp ON pp.profile_id=l.ProfileId WHERE ProfileId=%s '''
        with connection.cursor() as cursor:
            cursor.execute(query, [profile_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        #print("Query result:", result)
        return result


    def get_all_profiles(status=1):
        query = '''
        SELECT l.*, pe.*, pf.*, ph.*, pp.*, pi.image, ph.horoscope_file 
        FROM logindetails l  
        LEFT JOIN profile_edudetails pe ON pe.profile_id=l.ProfileId 
        LEFT JOIN profile_familydetails pf ON pf.profile_id=l.ProfileId 
        LEFT JOIN profile_horoscope ph ON ph.profile_id=l.ProfileId 
        LEFT JOIN profile_partner_pref pp ON pp.profile_id=l.ProfileId
        LEFT JOIN profile_images pi ON pi.profile_id=l.ProfileId
        WHERE l.status = %s  -- Filter by status
        '''
        with connection.cursor() as cursor:
            cursor.execute(query, [status])  # Pass status as a parameter to filter by it
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        return result

def upload_to_profile(instance, filename):
    return os.path.join('profile_{0}'.format(instance.profile_id), filename)

class Image_Upload(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    image = models.ImageField(upload_to=upload_to_profile,storage=AzureMediaStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # Assuming this model is managed externally
        db_table = 'profile_images'
        
# class LoginDetails_1(models.Model):
#     ContentId = models.AutoField(primary_key=True)
#     ProfileId = models.CharField(max_length=50, unique=True)
#     temp_profileid = models.CharField(max_length=100)
#     Gender = models.CharField(max_length=10)
#     Mobile_no = models.CharField(max_length=15)
#     EmailId = models.EmailField()
#     Password = models.CharField(max_length=100)
#     Profile_marital_status = models.CharField(max_length=50)
#     Profile_dob = models.DateField()
#     Profile_complexion = models.CharField(max_length=50)
#     Profile_address = models.TextField()
#     Profile_country = models.CharField(max_length=100)
#     Profile_state = models.CharField(max_length=100)
#     Profile_city = models.CharField(max_length=100)
#     Profile_pincode = models.CharField(max_length=10)  

#     class Meta:
#         db_table = 'logindetails'

class ProfileFamilyDetails(models.Model):
    profile_id = models.CharField(max_length=50, unique=True)
    father_name = models.CharField(max_length=100, null=True)
    father_occupation = models.CharField(max_length=100, null=True)
    mother_name = models.CharField(max_length=100, null=True)
    mother_occupation = models.CharField(max_length=100, null=True)
    family_name = models.CharField(max_length=100, null=True)
    weight = models.CharField(max_length=250, null=True, blank=True)
    eye_wear = models.CharField(max_length=100, null=True, blank=True)
    body_type = models.CharField(max_length=250, null=True)
    about_self = models.TextField(null=True)
    hobbies = models.TextField(null=True)
    blood_group = models.CharField(max_length=50, null=True)
    Pysically_changed = models.CharField(max_length=20, null=True)
    no_of_brother = models.CharField(max_length=20, null=True)
    no_of_sister = models.CharField(max_length=20, null=True)
    no_of_bro_married = models.CharField(max_length=20, null=True)
    no_of_sis_married = models.CharField(max_length=20, null=True)
    family_type = models.CharField(max_length=100, null=True)
    family_value = models.CharField(max_length=100, null=True)
    family_status = models.CharField(max_length=100, null=True)
    property_details = models.TextField(null=True)
    property_worth = models.CharField(max_length=100, null=True)
    suya_gothram = models.CharField(max_length=100, null=True)
    uncle_gothram = models.CharField(max_length=100, null=True)
    ancestor_origin = models.TextField(null=True , blank=True)
    about_family = models.TextField(null=True)

    class Meta:
        db_table = 'profile_familydetails'

class ProfileEduDetails(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True, null=False, blank=False)
    highest_education = models.CharField(max_length=100, null=False, blank=False)
    degree = models.CharField(max_length=100, null=False, blank=True)
    ug_degeree = models.CharField(max_length=100, null=False, blank=True)
    about_edu = models.TextField( null=False, blank=False)
    profession = models.CharField(max_length=100, null=False, blank=False)  # Added missing field
    anual_income = models.CharField(max_length=100, null=False, blank=False)
    actual_income = models.CharField(max_length=100, null=False, blank=False)  # Added missing field
    work_country = models.CharField(max_length=100, null=False, blank=False)
    work_state = models.CharField(max_length=100, null=True, blank=True)
    work_city = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    work_district = models.CharField(max_length=100, null=True, blank=True) 
    work_place = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    work_pincode = models.CharField(max_length=10,null=False, blank=True)
    career_plans = models.TextField( null=False, blank=False)
    currency = models.CharField(max_length=250,null=False, blank=True)
    company_name = models.CharField(max_length=250,null=False, blank=True)
    designation = models.CharField(max_length=250,null=False, blank=True)
    profession_details = models.CharField(max_length=250,null=False, blank=True)
    business_name = models.CharField(max_length=250,null=False, blank=True)
    business_address = models.CharField(max_length=250,null=False, blank=True)
    nature_of_business = models.CharField(max_length=250,null=False, blank=True)
    field_ofstudy = models.CharField(max_length=250,null=False, blank=True)
    other_degree = models.CharField(max_length=250,null=True, blank=True)
    
    class Meta:
        db_table = 'profile_edudetails'

class ProfilePartnerPref(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True)
    pref_age_differences = models.CharField(max_length=10)
    pref_height_from = models.CharField(max_length=10)
    pref_height_to = models.CharField(max_length=50, null=True, blank=True)  # Added missing field
    pref_marital_status = models.CharField(max_length=100, null=True, blank=True)
    pref_profession = models.CharField(max_length=100, null=True, blank=True)

    pref_education = models.CharField(max_length=100, null=True, blank=True)
    pref_anual_income = models.CharField(max_length=100, null=True, blank=True)
    pref_anual_income_max = models.CharField(max_length=100, null=True, blank=True)

    pref_chevvai = models.CharField(max_length=10)
    
    pref_ragukethu = models.CharField(max_length=10)
   
    pref_foreign_intrest = models.CharField(max_length=100)
   
    pref_porutham_star = models.CharField(max_length=1000, null=True, blank=True)
    pref_porutham_star_rasi	 = models.TextField(null=True, blank=True)
    
    # pref_education = models.CharField(max_length=100)
    # pref_profession = models.CharField(max_length=100)
    # pref_anual_income = models.CharField(max_length=100)
    # pref_marital_status = models.CharField(max_length=100)
    class Meta:
        db_table = 'profile_partner_pref'

class ProfileSuggestedPref(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True)
    pref_age_differences = models.CharField(max_length=10)
    pref_height_from = models.CharField(max_length=10)
    pref_height_to = models.CharField(max_length=50, null=True, blank=True)  # Added missing field
    pref_marital_status = models.CharField(max_length=100, null=True, blank=True)
    pref_profession = models.CharField(max_length=100, null=True, blank=True)

    pref_education = models.CharField(max_length=100, null=True, blank=True)
    pref_anual_income = models.CharField(max_length=100, null=True, blank=True)
    pref_anual_income_max = models.CharField(max_length=100, null=True, blank=True)

    pref_chevvai = models.CharField(max_length=10)
    
    pref_ragukethu = models.CharField(max_length=10)
   
    pref_foreign_intrest = models.CharField(max_length=100)
   
    pref_porutham_star = models.CharField(max_length=1000, null=True, blank=True)
    pref_porutham_star_rasi	 = models.TextField(null=True, blank=True)
    
    # pref_education = models.CharField(max_length=100)
    # pref_profession = models.CharField(max_length=100)
    # pref_anual_income = models.CharField(max_length=100)
    # pref_marital_status = models.CharField(max_length=100)
    class Meta:
        db_table = 'profile_suggested_pref'

from django.db import models
from ckeditor.fields import RichTextField

class PageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)  

class Page(models.Model):
    page_name = models.CharField(max_length=255)
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    content = RichTextField()  # Use RichTextField for CKEditor
    deleted = models.BooleanField(default=False)  # New column for soft delete
    objects = models.Manager()  # Default manager
    active_objects = PageManager()  # Custom manager for active pages

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'page'  # Name of the table in your database

    def __str__(self):
        return self.page_name
    
class AdminSettings(models.Model):
    site_name = models.CharField(max_length=100, primary_key=True)  # Set site_name as the primary key
    meta_title = models.CharField(max_length=100)
    meta_description = models.TextField()
    contact_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15)
    email_address = models.EmailField()
    location_address = models.CharField(max_length=200)



    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'adminsite'  # Name of the table in your database

    def __str__(self):
        return self.site_name
    

class ActiveAdminUserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)
    
# class AdminUser(models.Model):
#     username = models.CharField(max_length=255)
#     email = models.EmailField()
#     password = models.CharField(max_length=255)
#     full_name = models.CharField(max_length=255)
#     role = models.CharField(max_length=255)
#     phone_number = models.CharField(max_length=20)
#     status = models.CharField(max_length=255)
#     deleted = models.BooleanField(default=False)  # Assuming a 'deleted' field exists

#     objects = models.Manager()  # Default manager
#     active_objects = ActiveAdminUserManager()  # Custom manager for active users

#     class Meta:
#         managed = False  # This tells Django not to handle database table creation/migration for this model
#         db_table = 'admin_user'  # Name of the table in your database

#     def __str__(self):
#         return self.username


# class Role(models.Model):
#     id = models.BigIntegerField(primary_key=True)
#     role_name = models.CharField(max_length=255)
#     admin = models.BooleanField(default=False)
#     view_only = models.BooleanField(default=False)
#     sales = models.BooleanField(default=False)
#     support = models.BooleanField(default=False)
#     biz_dev = models.BooleanField(default=False)
#     franchise = models.BooleanField(default=False)

#     class Meta:
#         managed = False
#         db_table = 'role'

class Role(models.Model):
    id = models.BigIntegerField(primary_key=True)
    role_name = models.CharField(max_length=255)
    search_profile = models.BooleanField(default=False)
    add_profile = models.BooleanField(default=False)
    edit_profile_all_fields = models.BooleanField(default=False)
    edit_profile_admin_comments_and_partner_settings = models.BooleanField(default=False)
    membership_activation = models.BooleanField(default=False)
    new_photo_update = models.BooleanField(default=False)
    edit_horo_photo = models.BooleanField(default=False)
    add_users = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'role_permissions'

class AdminUser(models.Model):
    id = models.BigAutoField(primary_key=True)  # Set as primary key
    username = models.CharField(max_length=255)
    email = models.EmailField()
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255)
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    status = models.BooleanField(default=False)  
    deleted = models.BooleanField(default=False) 


    class Meta:
        managed = False
        db_table = 'admin_userr'


class Award(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='awards/images/',storage=AzureMediaStorage())
    description = models.TextField()
    status = models.IntegerField(default=1)
    deleted = models.BooleanField(default=False)

    
    class Meta:
        managed = False  
        db_table = 'award_gallery' 

    def __str__(self):
        return self.name


class SuccessStory(models.Model):
    couple_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='success_stories/photos/',storage=AzureMediaStorage())
    date_of_marriage = models.DateField()
    details = models.TextField()
    status = models.IntegerField(default=1)  
    deleted = models.BooleanField(default=False)  


    class Meta:
        managed = False  
        db_table = 'success_story' 

    def __str__(self):
        return self.couple_name


class Testimonial(models.Model):
    profile_id = models.CharField(max_length=50)
    rating = models.IntegerField()
    review_content = models.TextField()
    user_image = models.ImageField(upload_to='testimonials/',storage=AzureMediaStorage())
    status = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'profile_testimonials'  

    def __str__(self):
        return f"Testimonial by {self.profile_id} - Rating: {self.rating}"
    
    
    
        
class ProfileHoroscope(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True)  # Required field
    time_of_birth = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    place_of_birth = models.CharField(max_length=100, null=True, blank=True)  # Existing field
    birthstar_name = models.CharField(max_length=255, null=True, blank=True)  # Existing field
    birth_rasi_name = models.CharField(max_length=50, null=True, blank=True)  # Existing field
    lagnam_didi = models.CharField(max_length=50, null=True, blank=True)  # Existing field
    chevvai_dosaham = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    ragu_dosham = models.CharField(max_length=100, null=True, blank=True)  # Existing field
    nalikai = models.CharField(max_length=100, null=True, blank=True)  # Existing field
    dasa_name = models.CharField(max_length=100, null=True, blank=True)  # Existing field
    dasa_balance = models.CharField(max_length=100, null=True, blank=True)  # Existing field
    horoscope_hints = models.CharField(max_length=200, null=True, blank=True)  # Existing field
    rasi_kattam = models.CharField(max_length=1000, null=True, blank=True)  # Existing field
    amsa_kattam = models.CharField(max_length=1000, null=True, blank=True)  # Existing field
    # horoscope_file = models.TextField(null=True, blank=True)  # Added missing field
    #horo_file_updated = models.DateTimeField(null=True, blank=True)  # Added missing field
    horoscope_file = models.FileField(upload_to=upload_to_profile,storage=AzureMediaStorage())
    horo_file_updated = models.CharField(max_length=100 , null=True, blank=True)    
    calc_chevvai_dhosham = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    calc_raguketu_dhosham = models.CharField(max_length=100, null=True, blank=True)  # Added missing field

    class Meta:
        db_table = 'profile_horoscope'
    
    
class Homepage(models.Model):
    id = models.AutoField(primary_key=True)
    why_vysyamala = RichTextField()  
    youtube_links = models.TextField()  
    vysyamala_apps = models.TextField()  

    deleted = models.BooleanField(default=False)  
    objects = models.Manager()  
    active_objects = PageManager()  

    class Meta:
        managed = False  
        db_table = 'homepage'  

    def __str__(self):
        return f'Homepage {self.id}'



class Express_interests(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    to_express_message = models.CharField(max_length=1000)
    req_datetime = models.DateTimeField()
    response_datetime = models.TextField() 
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_express_interest'  # Name of the table in your database

    def __str__(self):
        return self.id


class PlanDetails(models.Model):
    # Define your model fields here
    id = models.IntegerField(primary_key=True)
    master_substatus = models.IntegerField()
    plan_name = models.CharField(max_length=50)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2)
    plan_renewal_cycle = models.IntegerField()
    plan_status = models.CharField(max_length=100)

    class Meta:
        managed = False 
        db_table = 'plan_master'





class Profile_PlanFeatureLimit(models.Model):
    id  = models.IntegerField(primary_key=True)
    profile_id = models.CharField(max_length=10, blank=True, null=True)
    plan_id = models.CharField(max_length=10, blank=True, null=True)
    basic_details = models.IntegerField(null=True, blank=True)
    personal_details = models.IntegerField(null=True, blank=True)
    family_details = models.IntegerField(null=True, blank=True)
    horoscope_details = models.IntegerField(null=True, blank=True)
    horoscope_grid_details = models.IntegerField(null=True, blank=True)
    contact_details = models.IntegerField(null=True, blank=True)
    attached_horoscope = models.IntegerField(null=True, blank=True)
    photo_viewing = models.IntegerField(null=True, blank=True)
    profile_permision_toview = models.IntegerField(null=True, blank=True, help_text='Profile to visit count per day')
    validity_period = models.IntegerField(null=True, blank=True)
    eng_print = models.IntegerField(null=True, blank=True)
    tamil_print = models.IntegerField(null=True, blank=True)
    express_int_count = models.IntegerField(null=True, blank=True, help_text='Express interests count per day')
    book_mark = models.IntegerField(null=True, blank=True)
    photo_req = models.IntegerField(null=True, blank=True)
    report_an_error = models.IntegerField(null=True, blank=True)
    private_notes = models.IntegerField(null=True, blank=True)
    whats_app_share = models.IntegerField(null=True, blank=True)
    compatability_report = models.IntegerField(null=True, blank=True)
    online_chat = models.IntegerField(null=True, blank=True)
    click_to_call = models.IntegerField(null=True, blank=True)
    who_can_see_profile = models.IntegerField(null=True, blank=True)
    featured_profile = models.IntegerField(null=True, blank=True)
    priority_circulation = models.IntegerField(null=True, blank=True)
    email_blast = models.IntegerField(null=True, blank=True)
    astro_service = models.IntegerField(null=True, blank=True)
    vys_assist = models.IntegerField(null=True, blank=True)
    exp_int_lock = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    
    membership_fromdate = models.DateTimeField(null=True, blank=True)
    membership_todate = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'profile_plan_feature_limits'
   
    def __str__(self):
        # return f"PlanFeatureLimit {self.id}"
        return self.id






class PlanFeatureLimit(models.Model):
    plan_id = models.CharField(max_length=10, blank=True, null=True)
    basic_details = models.IntegerField(null=True, blank=True)
    personal_details = models.IntegerField(null=True, blank=True)
    family_details = models.IntegerField(null=True, blank=True)
    horoscope_details = models.IntegerField(null=True, blank=True)
    horoscope_grid_details = models.IntegerField(null=True, blank=True)
    contact_details = models.IntegerField(null=True, blank=True)
    attached_horoscope = models.IntegerField(null=True, blank=True)
    photo_viewing = models.IntegerField(null=True, blank=True)
    profile_permision_toview = models.IntegerField(null=True, blank=True, help_text='Profile to visit count per day')
    validity_period = models.IntegerField(null=True, blank=True)
    eng_print = models.IntegerField(null=True, blank=True)
    tamil_print = models.IntegerField(null=True, blank=True)
    express_int_count = models.IntegerField(null=True, blank=True, help_text='Express interests count per day')
    book_mark = models.IntegerField(null=True, blank=True)
    photo_req = models.IntegerField(null=True, blank=True)
    report_an_error = models.IntegerField(null=True, blank=True)
    private_notes = models.IntegerField(null=True, blank=True)
    whats_app_share = models.IntegerField(null=True, blank=True)
    compatability_report = models.IntegerField(null=True, blank=True)
    online_chat = models.IntegerField(null=True, blank=True)
    click_to_call = models.IntegerField(null=True, blank=True)
    who_can_see_profile = models.IntegerField(null=True, blank=True)
    featured_profile = models.IntegerField(null=True, blank=True)
    priority_circulation = models.IntegerField(null=True, blank=True)
    email_blast = models.IntegerField(null=True, blank=True)
    astro_service = models.IntegerField(null=True, blank=True)
    vys_assist = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'plan_feature_limits'
   
    def __str__(self):
        # return f"PlanFeatureLimit {self.id}"
        return self.id



class Profile_wishlists(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    marked_datetime = models.DateTimeField()
    status = models.CharField(max_length=50)  


    class Meta:
        managed = False 
        db_table = 'profile_wishlists' 

    def __str__(self):
        return self.id

class Photo_request(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    req_datetime = models.TextField()
    response_datetime = models.TextField() 
    response_message = models.TextField() 
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_photo_request'  # Name of the table in your database

    def __str__(self):
        return self.id
      


class Profile_visitors(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=100)
    viewed_profile = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    status = models.CharField(max_length=15)  #if status is 1 requestsent 2 is accepted 3 is rejected


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_visit_logs'  # Name of the table in your database

    def __str__(self):
        return self.id


class Registration1(models.Model):
    ContentId  = models.AutoField(primary_key=True)
    temp_profileid = models.CharField(max_length=200)
    ProfileId = models.CharField(max_length=50)
    LoginId = models.CharField(max_length=50)
    Profile_for = models.CharField(max_length=50)
    Gender = models.TextField(max_length=100)  # Changed from CharField to TextField
    Mobile_no = models.CharField(max_length=50)
    EmailId = models.CharField(max_length=100)
    Password = models.CharField(max_length=20)  # Changed from CharField to TextField
    Otp = models.CharField(max_length=10)
    Stage = models.SmallIntegerField()
    AdminPermission = models.SmallIntegerField()  # Changed from CharField to TextField
    Payment = models.CharField(max_length=10)  # Changed from CharField to TextField
    PaymentExpire = models.DateTimeField(max_length=15)  # Changed from CharField to TextField
    PaymentType = models.CharField(max_length=255)  # Changed from CharField to TextField


    Profile_name = models.CharField(max_length=255) 
    Profile_marital_status = models.CharField(max_length=255) 
    Profile_dob = models.CharField(max_length=255) 
    Profile_height = models.CharField(max_length=255) 
    Profile_complexion = models.CharField(max_length=255)

    Profile_address = models.CharField(max_length=200) 
    Profile_country = models.CharField(max_length=200) 
    Profile_state = models.CharField(max_length=200) 
    Profile_city = models.CharField(max_length=200) 
    Profile_district = models.CharField(max_length=200) 
    Profile_pincode = models.CharField(max_length=200)
    Profile_alternate_mobile= models.CharField(max_length=20)
    Profile_whatsapp= models.CharField(max_length=20)
    Profile_mobile_no= models.CharField(max_length=20)
    # Profile_idproof = models.FileField(upload_to=upload_to_profile_basic)
    # Profile_divorceproof = models.FileField(upload_to=upload_to_profile_basic)
    Profile_gothras = models.CharField(max_length=255)
    Photo_password = models.CharField(max_length=255)
    Photo_protection = models.SmallIntegerField(default=0)
    Video_url= models.CharField(max_length=255)
    Plan_id= models.CharField(max_length=100)
    Addon_package= models.CharField(max_length=100)
    Last_login_date= models.CharField(max_length=100)  
    Notifcation_enabled= models.CharField(max_length=100)
    Featured_profile= models.CharField(max_length=100)
    DateOfJoin= models.CharField(max_length=100) #models.DateTimeField()
    Reset_OTP = models.CharField(max_length=6, blank=True, null=True)
    quick_registration=models.CharField(max_length=6, blank=True, null=True)
    Reset_OTP_Time = models.DateTimeField(null=True, blank=True)
    Profile_verified = models.SmallIntegerField(default=0)
    device_id=models.TextField(null=True, blank=True)

    #Profile_idproof= models.TextField()
    

    status = models.IntegerField() 


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'logindetails'  # Name of the table in your database

    def __str__(self):
        return self.ProfileId
    


class Get_profiledata_Matching(models.Model):

    ContentId  = models.AutoField(primary_key=True)
    temp_profileid = models.CharField(max_length=200)
    profile_id = models.CharField(max_length=50)
    LoginId = models.CharField(max_length=50)
    Profile_for = models.CharField(max_length=50)
    Gender = models.TextField(max_length=100)  # Changed from CharField to TextField
    Mobile_no = models.CharField(max_length=50)

    #updated by vinoth 1908-2024

    @staticmethod
    def get_profile_list(gender,profile_id,start, per_page , search_profile_id , order_by,search_profession,search_age,search_location):

        # print

        #return [], 0, {}
        print('inside count')
        try:
            print('inside count2')

            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences
            pref_annual_income = partner_pref.pref_anual_income

            # print('pref_anual_income',pref_annual_income)
            
            
            
            pref_marital_status = partner_pref.pref_marital_status

           
            partner_pref_education = partner_pref.pref_education
            # print('pref_annual_income',pref_annual_income)
            # print('partner_pref_education',partner_pref_education)

            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi= partner_pref.pref_porutham_star_rasi



            partner_pref_porutham_star_rasi= partner_pref.pref_porutham_star_rasi


            min_max_query = """
                SELECT MIN(income_amount) AS min_income, 
                    MAX(income_amount) AS max_income
                FROM masterannualincome
                WHERE FIND_IN_SET(id, %s) > 0  """


        
            with connection.cursor() as cursor:
                cursor.execute(min_max_query, [pref_annual_income])
                min_max_income = cursor.fetchone()
            
            if min_max_income:
                min_income, max_income = min_max_income
                # print('min_income', min_income)
                # print('max_income', max_income)
            #else:
                # print('No income data found for the provided IDs.')


            print('partner_pref_porutham_star_rasi',partner_pref_porutham_star_rasi)

            try:
                age_difference = int(age_difference_str)
            except ValueError:
                
                #return JsonResponse({'status': 'failure', 'message': 'Invalid age difference value.'}, status=status.HTTP_400_BAD_REQUEST)
                return [], 0, {}           
            
                #exit
            print('inside count3')
            if search_age:
                age_difference=int(search_age)

            if gender.upper() == "MALE":
                matching_age = current_age - age_difference
                age_condition_operator = "<"
            else:
                # print('female age cond')
                matching_age = current_age + age_difference
                age_condition_operator = ">"

            try:
                    
                    # print('34i7678sdd')
                    # base_query = """
                    # SELECT a.*,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    # f.highest_education, g.EducationLevel, d.star, h.income
                    # FROM logindetails a 
                    # JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    # JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    # JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    # JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    # JOIN mastereducation g ON f.highest_education = g.RowId 
                    # JOIN masterannualincome h ON h.id = f.anual_income
                    # WHERE a.gender != %s AND a.ProfileId != %s
                    # AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s
                    # AND h.income_amount BETWEEN %s AND %s
                    # AND FIND_IN_SET(g.RowId,  %s) > 0
                    # AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0
                    # """
                    base_query = """
                    SELECT DISTINCT a.ProfileId,a.*,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income
                    FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.status=1 AND a.gender != %s AND a.ProfileId != %s 
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s
                    """

                   

                    # query_params = [gender, profile_id, matching_age, min_income,max_income, partner_pref_education,partner_pref_porutham_star_rasi]
                    query_params = [gender, profile_id, matching_age]

                    if min_income and max_income:
                        base_query += " AND h.income_amount BETWEEN %s AND %s"
                        query_params.extend([min_income, max_income])

                    if partner_pref_education:
                        base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                        query_params.append(partner_pref_education)

                    # Append porutham star-rasi condition only if partner_pref_porutham_star_rasi exists
                    if partner_pref_porutham_star_rasi:
                        base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                        query_params.append(partner_pref_porutham_star_rasi)

                    # Append marital status condition only if pref_marital_status exists
                    if pref_marital_status:
                        base_query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                        query_params.append(pref_marital_status)

                    height_conditions = ""

                    if partner_pref_height_from and partner_pref_height_to:
                        height_conditions = " AND a.Profile_height BETWEEN  %s AND  %s "
                        query_params.extend([partner_pref_height_from, partner_pref_height_to])
                    elif partner_pref_height_from:
                        height_conditions = " AND a.Profile_height >= %s"
                        query_params.append(partner_pref_height_from)
                    elif partner_pref_height_to:
                        height_conditions = " AND a.Profile_height <= %s"
                        query_params.append(partner_pref_height_to)

                    
                    search_profile_id_cond = ''
                    if search_profile_id:
                        # Condition to check both ProfileId and Profile_name fields
                        search_profile_id_cond = " AND (a.ProfileId = %s OR a.Profile_name LIKE %s)"
                        # Append search_profile_id twice as individual entries for both placeholders
                        query_params.append(search_profile_id)
                        query_params.append(f"%{search_profile_id}%")
                        # query_params.append(search_profile_id)


                        # Add profession filter
                    search_profession_cond=''
                    if search_profession:
                        search_profession_cond = " AND f.profession = %s"
                        query_params.append(search_profession)

                    search_location_cond=''
                    if search_location:
                        search_location_cond = " AND a.Profile_state = %s"
                        query_params.append(search_location)
                        #print('search_location',search_location)


                    # orderby_cond ='ORDER BY a.DateOfJoin DESC'
                    # if order_by:
                    #     orderby_cond = "ORDER BY a.DateOfJoin " + order_by
                    # print('order_by',order_by)
                    try:
                        order_by = int(order_by)  # Convert order_by to integer
                    except (ValueError, TypeError):
                        order_by = None  # Handle invalid cases
                    
                    if order_by == 1:
                            # print('order by 123456',order_by)
                            
                            orderby_cond = " ORDER BY a.DateOfJoin ASC "
                    elif order_by == 2:
                            # print('order by 123456',order_by)
                            orderby_cond = " ORDER BY a.DateOfJoin DESC "
                    else:
                            # print('esg')
                            orderby_cond = ""  # Default case if no valid order_by is provided

                       
                    # query = base_query.format(operator=age_condition_operator) + height_conditions
                    query = base_query.format(operator=age_condition_operator) + height_conditions + search_profile_id_cond + search_profession_cond+search_location_cond+orderby_cond
                    count_query_params = query_params.copy()

                  
                    
                    #count_query = f"SELECT COUNT(*) FROM ({query}) AS count_query"

                   
                    # Execute the COUNT query to get the total number of records
                    
                    #try:
                    # print('query',query)
                    
                    with connection.cursor() as cursor1:
                        cursor1.execute(query, query_params)
                        all_profile_ids = [row1[0] for row1 in cursor1.fetchall()]

                        total_count = len(all_profile_ids)

                        profile_with_indices={str(i + 1): profile_id for i, profile_id in enumerate(all_profile_ids)}

                    # Format the query for logging/debugging

                    # print('all_profile_ids',all_profile_ids)
                    
                    query += " LIMIT %s, %s"

                    #print(query)

                   
                    
                    query_params.extend([start, per_page])     

                    cleaned_query = query.replace('\n', ' ').replace('  ', ' ').strip()
                    formatted_query = query % tuple(query_params)
                    
                    print('formatted_query')

                    print('formatted_query',formatted_query)

                    cleaned_query1 = formatted_query.replace('\n', ' ').replace('  ', ' ').strip()

                    with connection.cursor() as cursor:
                        cursor.execute(query, query_params)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [col[0] for col in cursor.description]
                            results = [dict(zip(columns, row)) for row in rows]

                            # print('results',results)
                            # print('total_count',total_count)
                            # print('profile_with_indices',profile_with_indices)

                            return results , total_count , profile_with_indices
                            #return [], 0, {}
                        else:
                            print('123')
                            # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': cleaned_query}, status=status.HTTP_404_NOT_FOUND)
                            # return None , 0 , None
                            return [], 0, {}

                    # except Exception as e:
                    #     # Log the exception
                    #     #print(f"An error occurred: {str(e)}")
                    #     return None ,0 ,None # Return 0 as the total count in case of an error

            except Exception as e:
                print(str(e),'weegger')
                print('5678900')
                # return JsonResponse({'status': 'failure1', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # return None , 0 , None
                return [], 0, {}

        except Exception as e:
                print('12357576')

                # print(str(e))

                # return JsonResponse({'status': 'failure2', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # return None , 0 , None
                return [], 0, {}
        
    @staticmethod
    def get_suggest_profile_list(gender,profile_id,start, per_page , search_profile_id , order_by,search_profession,search_age,search_location):
        
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(ProfileSuggestedPref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences
            pref_annual_income = partner_pref.pref_anual_income
            pref_marital_status = partner_pref.pref_marital_status

           
            partner_pref_education = partner_pref.pref_education
            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi= partner_pref.pref_porutham_star_rasi


            partner_pref_porutham_star_rasi= partner_pref.pref_porutham_star_rasi


            min_max_query = """
                SELECT MIN(income_amount) AS min_income, 
                    MAX(income_amount) AS max_income
                FROM masterannualincome
                WHERE FIND_IN_SET(id, %s) > 0  """


        
            with connection.cursor() as cursor:
                cursor.execute(min_max_query, [pref_annual_income])
                min_max_income = cursor.fetchone()
            
            if min_max_income:
                min_income, max_income = min_max_income

            try:
                age_difference = int(age_difference_str)
            except ValueError:
                return JsonResponse({'status': 'failure', 'message': 'Invalid age difference value.'}, status=status.HTTP_400_BAD_REQUEST)

           
            if search_age:
                age_difference=int(search_age)

            if gender.upper() == "MALE":
                matching_age = current_age - age_difference
                age_condition_operator = "<"
            else:
                # print('female age cond')
                matching_age = current_age + age_difference
                age_condition_operator = ">"

            try:
                    
                    base_query = """
                    SELECT a.*,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income
                    FROM logindetails a 
                    JOIN profile_suggested_pref s ON a.ProfileId = s.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.gender != %s AND a.ProfileId != %s
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s
                    """
                    query_params = [gender, profile_id, matching_age]

                    if min_income and max_income:
                        base_query += " AND h.income_amount BETWEEN %s AND %s"
                        query_params.extend([min_income, max_income])

                    if partner_pref_education:
                        base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                        query_params.append(partner_pref_education)

                    # Append porutham star-rasi condition only if partner_pref_porutham_star_rasi exists
                    if partner_pref_porutham_star_rasi:
                        base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                        query_params.append(partner_pref_porutham_star_rasi)

                    # Append marital status condition only if pref_marital_status exists
                    if pref_marital_status:
                        base_query += " AND a.Profile_marital_status = %s"
                        query_params.append(pref_marital_status)

                    height_conditions = ""

                    if partner_pref_height_from and partner_pref_height_to:
                        height_conditions = "AND a.Profile_height BETWEEN %s AND %s"
                        query_params.extend([partner_pref_height_from, partner_pref_height_to])
                    elif partner_pref_height_from:
                        height_conditions = "AND a.Profile_height >= %s"
                        query_params.append(partner_pref_height_from)
                    elif partner_pref_height_to:
                        height_conditions = "AND a.Profile_height <= %s"
                        query_params.append(partner_pref_height_to)

                    
                    search_profile_id_cond=''
                    if search_profile_id:
                        search_profile_id_cond = "AND a.ProfileId = %s "
                        query_params.append(search_profile_id)

                    search_profession_cond=''
                    if search_profession:
                        search_profession_cond = " AND f.profession = %s"
                        query_params.append(search_profession)

                    search_location_cond=''
                    if search_location:
                        search_location_cond = " AND a.Profile_state = %s"
                        query_params.append(search_location)

                    try:
                        order_by = int(order_by)  # Convert order_by to integer
                    except (ValueError, TypeError):
                        order_by = None  # Handle invalid cases
                    
                    if order_by == 1:
                            # print('order by 123456',order_by)
                            
                            orderby_cond = " ORDER BY a.DateOfJoin ASC "
                    elif order_by == 2:
                            # print('order by 123456',order_by)
                            orderby_cond = " ORDER BY a.DateOfJoin DESC "
                    else:
                            # print('esg')
                            orderby_cond = ""  # Default case if no valid order_by is provided

                        
                    # query = base_query.format(operator=age_condition_operator) + height_conditions
                    query = base_query.format(operator=age_condition_operator) + height_conditions + search_profile_id_cond + search_profession_cond+search_location_cond+orderby_cond
                    count_query_params = query_params.copy()
                    
                    #try:
                    with connection.cursor() as cursor1:
                        cursor1.execute(query, query_params)
                        all_profile_ids = [row1[1] for row1 in cursor1.fetchall()]

                        total_count = len(all_profile_ids)

                        profile_with_indices={str(i + 1): profile_id for i, profile_id in enumerate(all_profile_ids)}

                    # Format the query for logging/debugging
                    
                    query += " LIMIT %s, %s"
                    query_params.extend([start, per_page])     

                    cleaned_query = query.replace('\n', ' ').replace('  ', ' ').strip()
                    formatted_query = query % tuple(query_params)
                    
                    # print('formatted_query',formatted_query)

                    cleaned_query1 = formatted_query.replace('\n', ' ').replace('  ', ' ').strip()

                    with connection.cursor() as cursor:
                        cursor.execute(query, query_params)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [col[0] for col in cursor.description]
                            results = [dict(zip(columns, row)) for row in rows]

                            return results , total_count , profile_with_indices
                        else:

                            return None , 0 , None

            except Exception as e:

                return None , 0 , None

        except Exception as e:

                return None , 0 , None
        
    @staticmethod
    def get_profile_match_count(gender,profile_id):

        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences
            pref_annual_income = partner_pref.pref_anual_income
            pref_marital_status = partner_pref.pref_marital_status

           
            partner_pref_education = partner_pref.pref_education

            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi= partner_pref.pref_porutham_star_rasi

            min_max_query = """
                SELECT MIN(income_amount) AS min_income, 
                    MAX(income_amount) AS max_income
                FROM masterannualincome
                WHERE FIND_IN_SET(id, %s) > 0  """


        
            with connection.cursor() as cursor:
                cursor.execute(min_max_query, [pref_annual_income])
                min_max_income = cursor.fetchone()
            
            if min_max_income:
                min_income, max_income = min_max_income
            else:
                min_income=0
                max_income=0




            try:
                age_difference = int(age_difference_str)
            except ValueError:
                return JsonResponse({'status': 'failure', 'message': 'Invalid age difference value.'}, status=status.HTTP_400_BAD_REQUEST)

            if gender.upper() == "MALE":
                matching_age = current_age - age_difference
                age_condition_operator = "<"
            else:
                matching_age = current_age + age_difference
                age_condition_operator = ">"

            try:
                    base_query = """
                    SELECT a.*,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income
                    FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.gender != %s AND a.ProfileId != %s
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s """

                   
                    query_params = [gender, profile_id, matching_age]

                    if min_income and max_income:
                        base_query += " AND h.income_amount BETWEEN %s AND %s"
                        query_params.extend([min_income, max_income])

                    if partner_pref_education:
                        base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                        query_params.append(partner_pref_education)

                    # Append porutham star-rasi condition only if partner_pref_porutham_star_rasi exists
                    if partner_pref_porutham_star_rasi:
                        base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                        query_params.append(partner_pref_porutham_star_rasi)

                    # Append marital status condition only if pref_marital_status exists
                    if pref_marital_status:
                        base_query += " AND a.Profile_marital_status = %s"
                        query_params.append(pref_marital_status)
                    
                    
                    height_conditions = ""
                    
                    if partner_pref_height_from and partner_pref_height_to:
                        height_conditions = "AND a.Profile_height BETWEEN %s AND %s"
                        query_params.extend([partner_pref_height_from, partner_pref_height_to])
                    elif partner_pref_height_from:
                        height_conditions = "AND a.Profile_height >= %s"
                        query_params.append(partner_pref_height_from)
                    elif partner_pref_height_to:
                        height_conditions = "AND a.Profile_height <= %s"
                        query_params.append(partner_pref_height_to)

                    # query = base_query.format(operator=age_condition_operator) + height_conditions
                    query = base_query.format(operator=age_condition_operator) + height_conditions
                    
                   
                   
                    # Format the query for logging/debugging
                    cleaned_query = query.replace('\n', ' ').replace('  ', ' ').strip()
                    formatted_query = query % tuple(query_params)
                    
                    # print('formatted_query',formatted_query)

                    cleaned_query1 = formatted_query.replace('\n', ' ').replace('  ', ' ').strip()

                    with connection.cursor() as cursor:
                        cursor.execute(query, query_params)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [col[0] for col in cursor.description]
                            results = [dict(zip(columns, row)) for row in rows]

                            return results
                        else:
                            return None

            except Exception as e:
                return None

        except Exception as e:
                # print('12357576')

                # print(str(e))

                # return JsonResponse({'status': 'failure2', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                 return None
        
    @staticmethod
    def get_suggest_match_count(gender,profile_id):

        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            suggest_pref = get_object_or_404(ProfileSuggestedPref, profile_id=profile_id)
            age_difference_str = suggest_pref.pref_age_differences
            pref_annual_income = suggest_pref.pref_anual_income
            pref_marital_status = suggest_pref.pref_marital_status

           
            partner_pref_education = suggest_pref.pref_education

            partner_pref_height_from = suggest_pref.pref_height_from
            partner_pref_height_to = suggest_pref.pref_height_to
            partner_pref_porutham_star_rasi= suggest_pref.pref_porutham_star_rasi

            min_max_query = """
                SELECT MIN(income_amount) AS min_income, 
                    MAX(income_amount) AS max_income
                FROM masterannualincome
                WHERE FIND_IN_SET(id, %s) > 0  """


        
            with connection.cursor() as cursor:
                cursor.execute(min_max_query, [pref_annual_income])
                min_max_income = cursor.fetchone()
            
            if min_max_income:
                min_income, max_income = min_max_income
            else:
                min_income=0
                max_income=0




            try:
                age_difference = int(age_difference_str)
            except ValueError:
                return JsonResponse({'status': 'failure', 'message': 'Invalid age difference value.'}, status=status.HTTP_400_BAD_REQUEST)

            if gender.upper() == "MALE":
                matching_age = current_age - age_difference
                age_condition_operator = "<"
            else:
                matching_age = current_age + age_difference
                age_condition_operator = ">"

            try:
                    base_query = """
                    SELECT a.*,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income
                    FROM logindetails a 
                    JOIN profile_suggested_pref s ON a.ProfileId = s.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.gender != %s AND a.ProfileId != %s
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s """

                   
                    query_params = [gender, profile_id, matching_age]

                    if min_income and max_income:
                        base_query += " AND h.income_amount BETWEEN %s AND %s"
                        query_params.extend([min_income, max_income])

                    if partner_pref_education:
                        base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                        query_params.append(partner_pref_education)

                    # Append porutham star-rasi condition only if partner_pref_porutham_star_rasi exists
                    if partner_pref_porutham_star_rasi:
                        base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                        query_params.append(partner_pref_porutham_star_rasi)

                    # Append marital status condition only if pref_marital_status exists
                    if pref_marital_status:
                        base_query += " AND a.Profile_marital_status = %s"
                        query_params.append(pref_marital_status)
                    
                    
                    height_conditions = ""
                    
                    if partner_pref_height_from and partner_pref_height_to:
                        height_conditions = "AND a.Profile_height BETWEEN %s AND %s"
                        query_params.extend([partner_pref_height_from, partner_pref_height_to])
                    elif partner_pref_height_from:
                        height_conditions = "AND a.Profile_height >= %s"
                        query_params.append(partner_pref_height_from)
                    elif partner_pref_height_to:
                        height_conditions = "AND a.Profile_height <= %s"
                        query_params.append(partner_pref_height_to)

                    # query = base_query.format(operator=age_condition_operator) + height_conditions
                    query = base_query.format(operator=age_condition_operator) + height_conditions
                    
                   
                   
                    # Format the query for logging/debugging
                    cleaned_query = query.replace('\n', ' ').replace('  ', ' ').strip()
                    formatted_query = query % tuple(query_params)
                    
                    # print('formatted_query',formatted_query)

                    cleaned_query1 = formatted_query.replace('\n', ' ').replace('  ', ' ').strip()

                    with connection.cursor() as cursor:
                        cursor.execute(query, query_params)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [col[0] for col in cursor.description]
                            results = [dict(zip(columns, row)) for row in rows]

                            return results
                        else:
                            return None

            except Exception as e:
                return None

        except Exception as e:
                # print('12357576')

                # print(str(e))

                # return JsonResponse({'status': 'failure2', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                 return None



    @staticmethod
    def get_profile_details(profile_ids):
        
        query = '''SELECT l.*, pp.*, pf.*, ph.*, pe.*,mr.name as rasi_name,mb.star as star_name , mp.Profession as profession_name
            FROM logindetails l 
            LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
            LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
            LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
            LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
            LEFT JOIN masterrasi mr ON mr.id = ph.birth_rasi_name 
            LEFT JOIN masterbirthstar mb ON mb.id = ph.birthstar_name
            LEFT JOIN masterprofession mp ON mp.RowId = pe.profession
            WHERE l.ProfileId IN %s  '''


        with connection.cursor() as cursor:
            cursor.execute(query,[tuple(profile_ids)])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        #print("Query result:", result)
        return result



class MatchingStarPartner(models.Model):
    # Define your model fields here
    id = models.IntegerField(primary_key=True)
    gender = models.CharField(max_length=50)
    source_star_id = models.IntegerField()
    source_rasi_id = models.IntegerField()
    dest_star_id = models.IntegerField()
    dest_rasi_id = models.IntegerField()
    match_count = models.IntegerField()
    matching_porutham = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'matching_stars_partner'  # Name of the table in your database

    @staticmethod
    def get_matching_stars(birth_star_id, gender):
        query = '''
        SELECT 
            sp.id,
            sp.source_star_id,
            sp.matching_porutham,
            sp.dest_rasi_id,
            sp.dest_star_id,
            sp.match_count,
            sd.star as matching_starname, 
            rd.name as matching_rasiname,  
            GROUP_CONCAT(pn.protham_name) AS protham_names 
        FROM 
            matching_stars_partner sp 
            LEFT JOIN 
            masterbirthstar sd ON sd.id = sp.dest_star_id 
            LEFT JOIN 
            masterrasi rd ON rd.id = sp.dest_rasi_id
        LEFT JOIN 
            matching_porutham_names pn ON FIND_IN_SET(pn.id, sp.matching_porutham) 
        WHERE 
            sp.gender = %s 
            AND sp.source_star_id = %s 
        GROUP BY 
            sp.id, sp.gender, sp.source_star_id
        '''
        with connection.cursor() as cursor:
            cursor.execute(query, [gender, birth_star_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        #print("Query result:", result)
        return result
    


class Partnerpref(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    pref_age_differences = models.CharField(max_length=50)
    pref_height_from = models.CharField(max_length=50)
    pref_height_to = models.CharField(max_length=50)
    pref_marital_status = models.CharField(max_length=50)
    pref_profession = models.CharField(max_length=50)  # Changed from CharField to TextField
    pref_education = models.CharField(max_length=50)
    pref_anual_income = models.CharField(max_length=50)
    pref_chevvai = models.CharField(max_length=20)  # Changed from CharField to TextField
    pref_ragukethu = models.CharField(max_length=20)
    pref_foreign_intrest = models.CharField(max_length=20)
    pref_porutham_star = models.TextField(max_length=200)
    pref_porutham_star_rasi = models.TextField(max_length=200)
    status = models.IntegerField()   # Changed from CharField to TextField
    
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_partner_pref'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Profespref(models.Model):

    RowId    = models.SmallIntegerField(primary_key=True)
    profession  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterprofession'  # Name of the table in your database

    def __str__(self):
        return self.RowId

class Profile_personal_notes(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=100)
    profile_to = models.CharField(max_length=100)
    notes = models.TextField()
    datetime = models.DateTimeField()
    status = models.CharField(max_length=15)  #if status is 1 requestsent 2 is accepted 3 is rejected


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_personal_notes'  # Name of the table in your database

    def __str__(self):
        return self.id
    
def calculate_age(dob):
    """
    Calculate age based on date of birth.
    
    Args:
    dob (datetime.date): The date of birth.
    
    Returns:
    int or None: The calculated age or None if dob is not provided.
    """
    if dob:
        today = datetime.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age
    return None


class Profile_vysassist(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    req_datetime = models.TextField()
    response_datetime = models.TextField() 
    to_message = models.TextField() 
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_vys_assist'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Profile_callogs(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    req_datetime = models.TextField()
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_call_logs'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class ProfileLoginLogs(models.Model):
    id = models.IntegerField(primary_key=True)
    profile_id = models.CharField(max_length=250, null=True)
    user_token = models.CharField(max_length=500, null=True)
    login_datetime = models.DateTimeField()
    logout_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'profile_loginLogs'

class ProfileSendFromAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=25, null=True, blank=True)
    profile_to = models.CharField(max_length=25, null=True, blank=True)
    send_date = models.DateField(null=True)
    comments = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = 'profile_sendfrom_admin'

class ProfileVysAssistFollowup(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key with auto-increment
    assist_id = models.IntegerField()
    owner_id = models.IntegerField()
    owner_name= models.CharField(max_length=200)
    comments = models.TextField()
    admin_comments = models.TextField(null=True, blank=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_vys_assist_followups'

    def __str__(self):
        return f"Follow-up {self.id} (Assist ID: {self.assist_id})"
    
class VysAssistcomment(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key with auto-increment
    comment_text = models.TextField()
    status = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'vysast_admin_definedtext'

    def __str__(self):
        return self.id
    
class c(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    req_datetime = models.TextField()
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_call_logs'  # Name of the table in your database

    def __str__(self):
        return self.id