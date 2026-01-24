from django.db import models ,connection
import os
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from rest_framework.views import status
from django.conf import settings
from .storages import AzureMediaStorage
from django.core.mail import EmailMessage
from datetime import date, timedelta
from collections import defaultdict
from authentication.models import Get_profiledata as gpt
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager



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
#

class State(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
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

class MasterhighestEducation(models.Model):
    id    = models.SmallIntegerField(primary_key=True)
    edu_level = models.CharField(max_length=100)
    fieldof_study = models.CharField(max_length=100)
    degeree_name  = models.CharField(max_length=100) 
    is_active  = models.BooleanField(default=False) 
    is_deleted  = models.BooleanField(default=False) 

    def __str__(self):
        return self.degree

    class Meta:
        db_table = 'masteredu_degeree'

class UgDegree(models.Model):
    id    = models.SmallIntegerField(primary_key=True)
    degree = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)  # Add the is_deleted field

    def __str__(self):
        return self.degree

    class Meta:
        db_table = 'masterugdegree'


class AnnualIncome(models.Model):
    id    = models.SmallIntegerField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
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
    # return os.path.join('profile_{0}'.format(instance.ProfileId), filename)
    return f"profile_idproof/IDProof/{filename}"

class PlanSubscription(models.Model):
 
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255,null=True,blank=True)
    plan_id = models.IntegerField(max_length=50,null=True,blank=True)
    addon_package = models.CharField(max_length=100,null=True,blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    payment_mode= models.CharField(max_length=75,null=True,blank=True)
    payment_for= models.CharField(max_length=100,null=True,blank=True)
    status =  models.IntegerField(max_length=10,null=True,blank=True)  
    payment_date = models.DateTimeField(null=True,blank=True)
    validity_startdate = models.DateTimeField(null=True,blank=True)
    validity_enddate = models.DateTimeField(null=True,blank=True)
    payment_by= models.CharField(max_length=150,null=True,blank=True)
    admin_user= models.CharField(max_length=150,null=True,blank=True)
    order_id= models.CharField(max_length=150,null=True,blank=True)
    payment_id= models.CharField(max_length=150,null=True,blank=True)
    gpay_no= models.CharField(max_length=150,null=True,blank=True)
    trans_id= models.IntegerField(max_length=10,null=True,blank=True)
    offer = models.CharField(max_length=255,null=True,blank=True)
    notes = models.CharField(max_length=255,null=True,blank=True)
    package_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    is_sent_email = models.BooleanField(default=False)
 
    class Meta:
        managed = False  
        db_table = 'plan_subscription'  
 
    def __str__(self):
        return self.id

def upload_to_profile(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.profile_id), filename)
    return f"profile_images/{filename}"

class LoginDetails(models.Model):
    ContentId = models.AutoField(primary_key=True)
    ProfileId = models.CharField(max_length=50, unique=True,null=True,blank=True)
    LoginId = models.CharField(max_length=50,  null=True,blank=True)
    Profile_for = models.CharField(max_length=50, null=True)
    Gender = models.CharField(max_length=100, null=True,blank=True)
    Mobile_no = models.CharField(max_length=50, null=True)
    EmailId = models.EmailField( null=True , blank=True)
    Password = models.CharField(max_length=255)
    Profile_name = models.CharField(max_length=250, null=True , blank=True)
    Profile_marital_status = models.CharField(max_length=100, null=True)
    Profile_dob = models.DateField(null=True)
    Profile_alternate_mobile = models.CharField(max_length=200, null=True, blank=True)
    Profile_complexion = models.CharField(max_length=100, null=True)
    Profile_address = models.CharField(max_length=200, null=True)
    Profile_country = models.CharField(max_length=200, null=True)
    Profile_state = models.CharField(max_length=200, null=True)
    Profile_city = models.CharField(max_length=200, null=True)
    Profile_district = models.CharField(max_length=200, null=True,blank=True)
    Profile_pincode = models.CharField(max_length=200, null=True)

    Profile_whatsapp = models.CharField(max_length=200, null=True, blank=True)
    Profile_mobile_no = models.CharField(max_length=200, null=True)
    Video_url= models.CharField(max_length=255, null=True,blank=True)
    #DateOfJoin = models.DateField(null=True)
    DateOfJoin = models.CharField(max_length=100,null=True,blank=True)
    Last_login_date= models.CharField(max_length=100,null=True,blank=True)  
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
    membership_startdate = models.DateTimeField(max_length=15,blank=True, null=True)  # Changed from CharField to TextField
    membership_enddate = models.DateTimeField(max_length=15,blank=True, null=True)  # Changed from CharField to TextField
    primary_status = models.IntegerField(blank=True, null=True)
    secondary_status =  models.IntegerField(blank=True, null=True)
    plan_status =  models.IntegerField(blank=True, null=True)
    PaymentType = models.CharField(max_length=255,blank=True, null=True)  # Changed from CharField to TextField
    Package_name= models.CharField(max_length=255,blank=True, null=True)  # Changed from CharField to TextField
    Video_url= models.TextField(blank=True, null=True)
    Plan_id= models.CharField(max_length=100,blank=True, null=True)
    Otp = models.CharField(max_length=10,blank=True, null=True)
    Otp_verify = models.SmallIntegerField(max_length=10,blank=True, null=True)    
    Profile_height = models.CharField(max_length=250,blank=True, null=True)
    Photo_password = models.CharField(max_length=255,blank=True, null=True)
    Photo_protection = models.BooleanField(default=False)
    Owner_id = models.CharField(max_length=50, blank=True, null=True)
    Profile_emailid= models.CharField(max_length=50, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    linkedin = models.CharField(max_length=255, blank=True, null=True)
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
    # return os.path.join('profile_{0}'.format(instance.profile_id), filename)
    return f"profile_images/{filename}"

class Image_Upload(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    image = models.ImageField(upload_to=upload_to_profile,storage=AzureMediaStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)
    image_approved = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = False  # Assuming this model is managed externally
        db_table = 'profile_images'
        
    def get_image_status(profile_id):
        approved_images_exist = Image_Upload.objects.filter(
            profile_id=profile_id,
            image_approved=1,
            is_deleted__in=[None, 0]
        ).exists()
    
        return "Yes" if approved_images_exist else "No"
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
    hobbies = models.TextField(null=True, blank=True)
    blood_group = models.CharField(max_length=50, null=True)
    Pysically_changed = models.CharField(max_length=20, null=True)
    no_of_brother = models.CharField(max_length=20,null=True, blank=True)
    no_of_sister = models.CharField(max_length=20, null=True, blank=True)
    no_of_bro_married = models.CharField(max_length=20, null=True, blank=True)
    no_of_sis_married = models.CharField(max_length=20, null=True, blank=True)
    family_type = models.CharField(max_length=100, null=True, blank=True)
    family_value = models.CharField(max_length=100, null=True, blank=True)
    family_status = models.CharField(max_length=100, null=True, blank=True)
    property_details = models.TextField(null=True,  blank=True)
    property_worth = models.CharField(max_length=100, null=True, blank=True)
    suya_gothram = models.CharField(max_length=100, null=True)
    uncle_gothram = models.CharField(max_length=100, null=True)
    suya_gothram_admin = models.CharField(max_length=200, null=True)
    uncle_gothram_admin = models.CharField(max_length=200, null=True)
    ancestor_origin = models.TextField(null=True , blank=True)
    about_family = models.TextField( null=True, blank=True)
    no_of_children = models.IntegerField(max_length=10 , null=True)
    madulamn = models.CharField(max_length=10 ,null=True,blank=True)
    father_alive = models.CharField(max_length=10 ,null=True,blank=True)
    mother_alive = models.CharField(max_length=10 ,null=True,blank=True)
    Physically_challenged_details = models.TextField(null=True,blank=True)
    
    class Meta:
        db_table = 'profile_familydetails'

class ProfileEduDetails(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True, null=False, blank=False)
    highest_education = models.CharField(max_length=100, null=False, blank=False)
    degree = models.CharField(max_length=100, null=False, blank=True)
    ug_degeree = models.CharField(max_length=100, null=False, blank=True)
    about_edu = models.TextField( null=True, blank=True)
    profession = models.CharField(max_length=100, null=False, blank=False)  # Added missing field
    anual_income = models.CharField(max_length=100, null=True, blank=True)
    actual_income = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    work_country = models.CharField(max_length=100, null=True, blank=True)
    work_state = models.CharField(max_length=100, null=True, blank=True)
    work_city = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    work_district = models.CharField(max_length=100, null=True, blank=True) 
    work_place = models.CharField(max_length=100, null=True, blank=True)  # Added missing field
    work_pincode = models.CharField(max_length=10,null=False, blank=True)
    career_plans = models.TextField( null=False, blank=True)
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

    pref_chevvai = models.CharField(max_length=10, null=True, blank=True)
    
    pref_ragukethu = models.CharField(max_length=10, null=True, blank=True)
   
    pref_foreign_intrest = models.CharField(max_length=100, null=True, blank=True)
   
    pref_porutham_star = models.CharField(max_length=1000, null=True, blank=True)
    pref_porutham_star_rasi	 = models.TextField(null=True, blank=True)
    pref_family_status  = models.CharField(max_length=100,null=True, blank=True)
    pref_state  = models.CharField(max_length=100,null=True, blank=True)
    degree = models.CharField(max_length=255, blank=True, null=True) 
    pref_fieldof_study= models.CharField(max_length=255, blank=True, null=True) 
    # pref_education = models.CharField(max_length=100)
    # pref_profession = models.CharField(max_length=100)
    # pref_anual_income = models.CharField(max_length=100)
    # pref_marital_status = models.CharField(max_length=100)
    class Meta:
        db_table = 'profile_partner_pref'

class ProfileSuggestedPref(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True)
    pref_age_differences = models.CharField(max_length=10, null=True, blank=True)
    pref_height_from = models.CharField(max_length=10, null=True, blank=True)
    pref_height_to = models.CharField(max_length=50, null=True, blank=True)  # Added missing field
    pref_marital_status = models.CharField(max_length=100, null=True, blank=True)
    pref_profession = models.CharField(max_length=100, null=True, blank=True)

    pref_education = models.CharField(max_length=100, null=True, blank=True)
    pref_anual_income = models.CharField(max_length=100, null=True, blank=True)
    pref_anual_income_max = models.CharField(max_length=100, null=True, blank=True)

    pref_chevvai = models.CharField(max_length=10, null=True, blank=True)
    
    pref_ragukethu = models.CharField(max_length=10, null=True, blank=True)
   
    pref_foreign_intrest = models.CharField(max_length=100, null=True, blank=True)
   
    pref_porutham_star = models.CharField(max_length=1000, null=True, blank=True)
    pref_porutham_star_rasi	 = models.TextField(null=True, blank=True)

    pref_family_status  = models.CharField(max_length=100,null=True, blank=True)
    pref_state  = models.CharField(max_length=100,null=True, blank=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    pref_fieldof_study = models.CharField(max_length=255, blank=True, null=True)
    # pref_education = models.CharField(max_length=100)
    # pref_profession = models.CharField(max_length=100)
    # pref_anual_income = models.CharField(max_length=100)
    # pref_marital_status = models.CharField(max_length=100)
    class Meta:
        managed = False
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
    id = models.AutoField(primary_key=True)
    couple_name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='success_stories/photos/',storage=AzureMediaStorage())
    date_of_marriage = models.DateField()
    details = models.TextField(blank=True, null=True)
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
    
def upload_to_profile_horoscope_admin(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.ProfileId), filename)
    return f"profile_horoscope/horoscope/{filename}"

    
        
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
    horoscope_file_admin = models.FileField(upload_to=upload_to_profile_horoscope_admin,storage=AzureMediaStorage(),null=True, blank=True)
    didi = models.CharField(max_length=50, null=True, blank=True)
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
    vys_assist_count  = models.IntegerField(null=True, blank=True)
    exp_int_lock = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    
    membership_fromdate = models.DateTimeField(null=True, blank=True)
    membership_todate = models.DateTimeField(null=True, blank=True)
    boosted_date = models.DateField(null=True, blank=True)
    boosted_enddate = models.DateField(null=True, blank=True)

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
    vys_assist_count  = models.IntegerField(null=True, blank=True)

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
    Otp_verify = models.SmallIntegerField(max_length=10,blank=True, null=True)
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
    Addon_package= models.CharField(max_length=100 , blank=True, null=True)
    Last_login_date= models.CharField(max_length=100)  
    Notifcation_enabled= models.CharField(max_length=100 , blank=True, null=True)
    Featured_profile= models.CharField(max_length=100)
    DateOfJoin= models.CharField(max_length=100) #models.DateTimeField()
    Reset_OTP = models.CharField(max_length=6, blank=True, null=True)
    quick_registration=models.CharField(max_length=6, blank=True, null=True)
    Reset_OTP_Time = models.DateTimeField(null=True, blank=True)
    Profile_verified = models.SmallIntegerField(default=0)
    device_id=models.TextField(null=True, blank=True)

    #Profile_idproof= models.TextField()
    Status = models.IntegerField() 


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'logindetails'  # Name of the table in your database

    def __str__(self):
        return self.ProfileId
    

class Addonpackages(models.Model):
    package_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    amount = models.IntegerField(null=True)

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masteradonpackages'  # Name of the table in your database

    def __str__(self):
        return f"{self.name} ({self.description})"



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
    def get_profile_list(
        gender, profile_id, start, per_page,
        search_profile_id=None, order_by=None,
        search_profession=None, search_age=None, search_location=None, complexion=None,
        city=None, state=None, education=None, foreign_intrest=None, has_photos=None,
        height_from=None, height_to=None,
        matching_stars=None, min_anual_income=None, max_anual_income=None, membership=None,ragu=None, chev=None,
        father_alive=None, mother_alive=None,marital_status=None,family_status=None,whatsapp_field=None,field_of_study=None,
        degree=None,from_date=None,to_date=None ,action_type=None , status=None,search=None ,except_viewed=None , except_visitor=None
    ):

        # print('action_type 123',action_type,'status 123',status)
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            current_age = calculate_age(profile.Profile_dob)
           
            # Load preferences
            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            my_family= get_object_or_404(ProfileFamilyDetails, profile_id=profile_id)
            my_suya_gothram=my_family.suya_gothram
            my_suya_gothram_admin=my_family.suya_gothram_admin
            if search_age and search_age.strip().isdigit() and int(search_age) > 0:
                age_diff = int(search_age)
            else:
                try:
                    pref_age_diff = int(partner_pref.pref_age_differences)
                    age_diff = pref_age_diff if pref_age_diff > 0 else 5
                except (ValueError, TypeError):
                    age_diff = 5

            if gender.upper() == "MALE":
                max_dob  = profile.Profile_dob + relativedelta(years=age_diff)  # older partner limit
                min_dob = profile.Profile_dob                                  # same age
            elif gender.upper() == "FEMALE":
                max_dob = profile.Profile_dob                                  # same age
                min_dob = profile.Profile_dob - relativedelta(years=age_diff)
            if education:
                pref_education = education 
            else:
                pref_education = partner_pref.pref_education
            if marital_status:
                marital_status = marital_status
            else:
                marital_status = partner_pref.pref_marital_status
            porutham_star_rasi = matching_stars or partner_pref.pref_porutham_star_rasi
            # print("pporutham",porutham_star_rasi)
            pref_foreign = foreign_intrest or partner_pref.pref_foreign_intrest
            ragukethu = ragu or partner_pref.pref_ragukethu
            chevvai = chev or partner_pref.pref_chevvai
            partner_pref_familysts = family_status or partner_pref.pref_family_status
            partner_pref_state = state or partner_pref.pref_state
            field_of_study = field_of_study or partner_pref.pref_fieldof_study
            degree = degree or partner_pref.degree

            annual_income_min = partner_pref.pref_anual_income
            annual_income_max = partner_pref.pref_anual_income_max

            # Base query
            base_query = """
                SELECT DISTINCT 
                        a.ProfileId, a.Plan_id, a.DateOfJoin, a.Photo_protection,
                        a.Profile_city,a.Profile_state,a.Profile_country, a.Profile_verified, a.Profile_name, a.Profile_dob,
                        c.family_status,c.father_occupation,c.suya_gothram,e.calc_chevvai_dhosham,e.calc_raguketu_dhosham,
                        a.Profile_height, a.Status ,e.birthstar_name, e.birth_rasi_name, f.degree,f.other_degree,
                        f.profession, f.highest_education,f.actual_income,f.anual_income,f.work_city,
                        f.work_state,f.work_country,f.designation,f.company_name,f.business_name,f.nature_of_business,g.EducationLevel, d.star, h.income,
                        v.viewed_profile,
                        pi.first_image_id AS has_image ,pi.image as profile_image ,TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) AS profile_age ,
                        (SELECT sp.sent_date 
                        FROM admin_sentprofiles sp 
                        WHERE sp.profile_id = %s AND sp.sentprofile_id = a.ProfileId 
                        LIMIT 1) AS sent_date
                    FROM logindetails a
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id
                    JOIN masterbirthstar d ON d.id = e.birthstar_name
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id
                    LEFT JOIN mastereducation g ON f.highest_education = g.RowId
                    LEFT JOIN masterannualincome h ON h.id = f.anual_income
                    JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                    LEFT JOIN masterprofession prof ON f.profession = prof.RowId
                    LEFT JOIN vw_profile_images pi ON a.ProfileId = pi.profile_id
                    LEFT JOIN profile_visibility pv ON pv.profile_id = a.ProfileId
                    LEFT JOIN profile_visit_logs v
                        ON v.viewed_profile = a.ProfileId AND v.profile_id = %s

                    JOIN profile_edudetails f_from ON f_from.profile_id = %s
                    JOIN profile_familydetails f1_from ON f1_from.profile_id = %s
                    JOIN profile_horoscope h1_from ON h1_from.profile_id = %s
                    JOIN logindetails l1_from ON l1_from.ProfileId = %s
                    LEFT JOIN masterannualincome h_from ON h_from.id = f_from.anual_income
                    


                    WHERE a.gender != %s 

                    AND (
                        -- If the opposite profile is Platinum, apply pv only when set
                        (
                            a.Plan_id IN (3,17)
                        AND (
                            (%s = 'male' 
                                AND (pv.visibility_age_from IS NULL OR pv.visibility_age_from = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= pv.visibility_age_from)
                                AND (pv.visibility_age_to IS NULL OR pv.visibility_age_to = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= pv.visibility_age_to)
                                AND a.Profile_dob > %s -- viewer must be older than candidate
                            )
                            OR
                            (%s = 'female' 
                                AND (pv.visibility_age_from IS NULL OR pv.visibility_age_from = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= pv.visibility_age_from)
                                AND (pv.visibility_age_to IS NULL OR pv.visibility_age_to = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= pv.visibility_age_to)
                                AND a.Profile_dob < %s -- viewer must be younger than candidate
                            )
                        )
                        AND (pv.visibility_height_from IS NULL OR pv.visibility_height_from = '' OR l1_from.Profile_height >= pv.visibility_height_from)
                        AND (pv.visibility_height_to IS NULL OR pv.visibility_height_to = '' OR l1_from.Profile_height <= pv.visibility_height_to)
                        AND (pv.visibility_profession IS NULL OR pv.visibility_profession = '' OR FIND_IN_SET(f_from.profession, pv.visibility_profession) > 0)
                        AND (pv.visibility_education IS NULL OR pv.visibility_education = '' OR FIND_IN_SET(f_from.highest_education, pv.visibility_education) > 0)
                        AND (pv.visibility_anual_income IS NULL OR pv.visibility_anual_income = '' 
                        OR h_from.id >= pv.visibility_anual_income)
                        AND (pv.visibility_anual_income_max IS NULL OR pv.visibility_anual_income_max = '' 
                        OR h_from.id <= pv.visibility_anual_income_max)

                        AND (pv.degree IS NULL OR pv.degree = '' OR FIND_IN_SET(f_from.degree, pv.degree) > 0)
                        AND (pv.visibility_field_of_study IS NULL OR pv.visibility_field_of_study = '' OR FIND_IN_SET(f_from.field_ofstudy, pv.visibility_field_of_study) > 0)
                        AND (pv.visibility_family_status IS NULL OR pv.visibility_family_status = '' OR FIND_IN_SET(f1_from.family_status, pv.visibility_family_status) > 0)
                        -- Chevvai visibility
                        AND (
                            pv.visibility_chevvai IS NULL OR pv.visibility_chevvai = '' OR LOWER(pv.visibility_chevvai) = 'both'
                            OR (
                                (LOWER(pv.visibility_chevvai) IN ('yes','true','1') 
                                    AND (LOWER(h1_from.calc_chevvai_dhosham) = 'yes' OR LOWER(h1_from.calc_chevvai_dhosham) = 'true' 
                                        OR h1_from.calc_chevvai_dhosham = '1' OR h1_from.calc_chevvai_dhosham = 1 
                                        OR h1_from.calc_chevvai_dhosham IS NULL OR h1_from.calc_chevvai_dhosham =''))
                                OR
                                (LOWER(pv.visibility_chevvai) IN ('no','false','2') 
                                    AND (LOWER(h1_from.calc_chevvai_dhosham) = 'no' OR LOWER(h1_from.calc_chevvai_dhosham) = 'false' 
                                        OR h1_from.calc_chevvai_dhosham = '2' OR h1_from.calc_chevvai_dhosham = 2 
                                        OR h1_from.calc_chevvai_dhosham IS NULL OR h1_from.calc_chevvai_dhosham =''))
                            )
                        )
                        -- Ragukethu visibility
                        AND (
                            pv.visibility_ragukethu IS NULL OR pv.visibility_ragukethu = '' OR LOWER(pv.visibility_ragukethu) = 'both'
                            OR (
                                (LOWER(pv.visibility_ragukethu) IN ('yes','true','1') 
                                    AND (LOWER(h1_from.calc_raguketu_dhosham) = 'yes' OR LOWER(h1_from.calc_raguketu_dhosham) = 'true' 
                                        OR h1_from.calc_raguketu_dhosham = '1' OR h1_from.calc_raguketu_dhosham = 1 
                                        OR h1_from.calc_raguketu_dhosham IS NULL OR h1_from.calc_raguketu_dhosham =''))
                                OR
                                (LOWER(pv.visibility_ragukethu) IN ('no','false','2') 
                                    AND (LOWER(h1_from.calc_raguketu_dhosham) = 'no' OR LOWER(h1_from.calc_raguketu_dhosham) = 'false' 
                                        OR h1_from.calc_raguketu_dhosham = '2' OR h1_from.calc_raguketu_dhosham = 2 
                                        OR h1_from.calc_raguketu_dhosham IS NULL OR h1_from.calc_raguketu_dhosham =''))
                            )
                        )
                    )
                    OR 
                    -- If opposite profile is not Platinum → skip pv.* checks
                    (a.Plan_id NOT IN (3,16,17))
                )
                    AND a.ProfileId != %s
                    AND a.Profile_dob BETWEEN %s AND %s """

            query_params = [profile_id,profile_id,profile_id,profile_id,profile_id,profile_id,gender,gender,profile.Profile_dob,gender,profile.Profile_dob, profile_id,min_dob, max_dob]
            
            
            if status == "sent":
                    # print('status is sent')
                    base_query += " AND a.Status != 0 " #Shows the deleted profiles also if it is already sent but deleted later
                    action_filter = "" if action_type == "all" else "AND sp.action_type = %s"
                    
                    base_query += """
                    AND EXISTS (
                        SELECT 1 
                        FROM admin_sentprofiles sp
                        WHERE sp.profile_id = %s 
                        AND sp.sentprofile_id = a.ProfileId
                        {action_filter}
                    )""".format(action_filter=action_filter)

                    # base_query += " ORDER BY asp.sent_date DESC "
                
                    query_params.append(profile_id)
                    if action_type != "all":
                        query_params.append(action_type)
                    

                    if search:
                        base_query += """ AND (a.Profile_name LIKE %s
                                        OR a.ProfileId LIKE %s
                                        OR prof.profession LIKE %s )"""
                        search_param = f"%{search.strip()}%"
                        query_params.extend([search_param] * 3)


                    
                    base_query += " ORDER BY CASE WHEN sent_date IS NULL THEN 1 ELSE 0 END, sent_date DESC"
            
            
            
            
            
            else:

                if search:
                    base_query += """ AND (a.Profile_name LIKE %s
                                    OR a.ProfileId LIKE %s
                                    OR prof.profession LIKE %s )"""
                    search_param = f"%{search.strip()}%"
                    query_params.extend([search_param] * 3)
                
                
                
                if from_date and to_date:
                    try:
                        from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
                        to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()+ timedelta(days=1) - timedelta(seconds=1)
                        base_query += " AND a.DateOfJoin BETWEEN %s AND %s"
                        query_params.extend([from_date_obj, to_date_obj])
                    except ValueError:
                        pass    
                inc_min = min_anual_income
                inc_max = max_anual_income

                inc_min = None if inc_min in ("null", "", None) else inc_min
                inc_max = None if inc_max in ("null", "", None) else inc_max
                annual_income_min = None if annual_income_min in ("null", "", None) else annual_income_min
                annual_income_max = None if annual_income_max in ("null", "", None) else annual_income_max

        
                if inc_min and inc_max:
                    base_query += "AND ((f.anual_income BETWEEN %s AND %s ) OR (f.anual_income IS NULL) OR (f.anual_income = ''))"
                    query_params.extend([int(inc_min), int(inc_max)])
                elif annual_income_min and annual_income_max:
                    base_query += "AND ((f.anual_income BETWEEN %s AND %s ) OR (f.anual_income IS NULL) OR (f.anual_income = ''))"
                    query_params.extend([int(annual_income_min),int(annual_income_max)])

                if my_suya_gothram_admin and str(my_suya_gothram_admin).strip() != "" and my_suya_gothram_admin != '0':
                    base_query += " AND (c.suya_gothram_admin IS NULL OR c.suya_gothram_admin = '' OR c.suya_gothram_admin != %s)"
                    query_params.append(str(my_suya_gothram_admin))
                if my_suya_gothram and str(my_suya_gothram).strip() != "":
                    base_query += " AND (c.suya_gothram IS NULL OR c.suya_gothram = '' OR c.suya_gothram != %s )"
                    query_params.append(my_suya_gothram)

                family_status_conditions = []

                # if partner_pref_familysts:
                #     family_status_conditions.append(
                #         "(FIND_IN_SET(c.family_status, %s) > 0 OR c.family_status IS NULL OR c.family_status = '')"
                #     )
                #     query_params.append(partner_pref_familysts)

                if partner_pref_familysts:
                    fstatuses = [s.strip() for s in str(partner_pref_familysts).split(',') if s.strip()]

                    if fstatuses:
                        # Generate placeholders for the IN query (e.g., %s, %s, %s)
                        placeholders = ','.join(['%s'] * len(fstatuses))
                        family_status_conditions.append(f"(c.family_status IN ({placeholders}))")
                        query_params.extend(fstatuses)

                # if family_status:
                #     statuses = [s.strip() for s in str(family_status).split(',') if s.strip()]
                #     if statuses:
                #         status_filters = []
                #         for status_f in statuses:
                #             status_filters.append("FIND_IN_SET(%s, c.family_status) > 0")
                #             query_params.append(status_f)
                #         family_status_conditions.append("(" + " OR ".join(status_filters) + ")")

                if family_status_conditions:

                    base_query += " AND ((" + " OR ".join(family_status_conditions) + ") OR c.family_status IS NULL OR c.family_status='' )"
            
                if pref_education and pref_education.strip():
                    edu_list = [e.strip() for e in pref_education.split(',') if e.strip().isdigit()]
                    if edu_list:
                        placeholders = ','.join(['%s'] * len(edu_list))
                        base_query += f" AND g.RowId IN ({placeholders})"
                        query_params.extend(edu_list)
                if matching_stars and matching_stars.strip():
                    try:
                        base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                        query_params.append(matching_stars.strip())
                    except Exception as e:
                        print(" Error processing matching_stars:", e)
                else :
                    if porutham_star_rasi and porutham_star_rasi.strip():
                        base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                        query_params.append(porutham_star_rasi.strip())

                if marital_status:
                    statuses = marital_status if isinstance(marital_status, list) else marital_status.split(',')
                    statuses = [s.strip() for s in statuses if s.strip()]
                    if statuses:
                        placeholders = ','.join(['%s'] * len(statuses))
                        base_query += f" AND a.Profile_marital_status IN ({placeholders})"
                        query_params.extend(statuses)

                if field_of_study:
                    fields = [f.strip() for f in field_of_study.split(',') if f.strip()]
                    if fields:
                        placeholders = ','.join(['%s'] * len(fields))
                        base_query += f" AND f.field_ofstudy IN ({placeholders})"
                        query_params.extend(fields)
                        
                if degree:
                    degrees = [d.strip() for d in degree.split(',') if d.strip()]
                    if degrees:
                        placeholders = ','.join(['%s'] * len(degrees))
                        # base_query += f" AND f.degree IN ({placeholders})"
                        base_query += f" AND ( f.degree IN ({placeholders}) OR f.degree IN (0,'86') OR f.degree IS NULL OR f.degree='')"
                        query_params.extend(degrees)
                # else:
                #     base_query += """ AND
                #     ( f.degree IN (0,'86') OR f.degree IS NULL OR f.degree='')"""

                # Height logic
                final_height_from = height_from or partner_pref.pref_height_from
                final_height_to = height_to or partner_pref.pref_height_to
                if final_height_from and final_height_to:
                    base_query += " AND a.Profile_height BETWEEN %s AND %s"
                    query_params.extend([final_height_from, final_height_to])
                elif final_height_from:
                    base_query += " AND a.Profile_height >= %s"
                    query_params.append(final_height_from)
                elif final_height_to:
                    base_query += " AND a.Profile_height <= %s"
                    query_params.append(final_height_to)

                # Apply extra filters
                if search_profile_id:
                    base_query += " AND (a.ProfileId = %s OR a.Profile_name LIKE %s)"
                    query_params.extend([search_profile_id, f"%{search_profile_id.strip()}%"])

                if search_profession:
                    professions = [p.strip() for p in search_profession.split(",") if p.strip()]
                    if professions:
                        placeholders = ", ".join(["%s"] * len(professions))
                        base_query += f" AND f.profession IN ({placeholders})"
                        query_params.extend(professions)

                if search_location:
                    base_query += " AND a.Profile_state = %s"
                    query_params.append(search_location)

                if complexion:
                    complexion_list = [c.strip() for c in complexion.split(',') if c.strip().isdigit()]
                    if complexion_list:
                        placeholders = ','.join(['%s'] * len(complexion_list))
                        base_query += f" AND a.Profile_complexion IN ({placeholders})"
                        query_params.extend(complexion_list)

                if city:
                    base_query += " AND a.Profile_city = %s"
                    query_params.append(city)

                if state:
                    base_query += """
                        AND (
                            FIND_IN_SET(f.work_state, %s) > 0 OR
                            FIND_IN_SET(a.Profile_state, %s) > 0 OR
                            a.Profile_state IS NULL OR
                            a.Profile_state = ''
                        )
                    """
                    query_params.extend([state, state])

                elif partner_pref_state:
                    base_query += """
                        AND (
                            FIND_IN_SET(f.work_state, %s) > 0 OR
                            FIND_IN_SET(a.Profile_state, %s) > 0 OR
                            a.Profile_state IS NULL OR
                            a.Profile_state = ''
                        )
                    """
                    query_params.extend([partner_pref_state, partner_pref_state])

                if has_photos and has_photos.lower() == "yes":
                    base_query += " AND pi.first_image_id IS NOT NULL"

                if except_viewed == 1:
                    base_query += """
                        AND NOT EXISTS (
                            SELECT 1 
                            FROM profile_visit_logs v1 
                            WHERE v1.viewed_profile = a.ProfileId 
                            AND v1.profile_id = %s
                        )
                    """
                    query_params.append(profile_id)

                if except_visitor == 1:
                    base_query += """
                        AND EXISTS (
                            SELECT 1 
                            FROM profile_visit_logs v2 
                            WHERE v2.profile_id = a.ProfileId 
                            AND v2.viewed_profile = %s
                        )
                    """
                    query_params.append(profile_id)



                if membership:
                    membership_ids = [m.strip() for m in membership.split(",") if m.strip().isdigit()]
                    if membership_ids:
                        placeholders = ','.join(['%s'] * len(membership_ids))
                        base_query += f" AND a.Plan_id IN ({placeholders})"
                        query_params.extend(membership_ids)


                # Foreign interest
                if pref_foreign and pref_foreign.strip().lower() in ['yes', 'no']:
                    if pref_foreign.lower() == "yes":
                        base_query += "  AND (f.work_country != '1' OR a.Profile_country!='1')"
                    elif pref_foreign.lower() == "no":
                        base_query += "  AND (f.work_country = '1' OR a.Profile_country='1')"
                
                conditions = []
                # print('ragu',ragu)
                # print('ragukethu',ragukethu)

                # if chev and chev.lower() == 'yes':
                #     print('2353543')
                #     conditions.append("""
                #         (
                #             LOWER(e.calc_chevvai_dhosham) IN ('yes', 'true')
                #             OR e.calc_chevvai_dhosham IN ('1', 1)
                #             OR e.calc_chevvai_dhosham IS NULL
                #         )
                #     """)

                # if ragu and ragu.lower() == 'yes':
                #     print('545454545')
                #     conditions.append("""
                #         (
                #             LOWER(e.calc_raguketu_dhosham) IN ('yes', 'true')
                #             OR e.calc_raguketu_dhosham IN ('1', 1)
                #             OR e.calc_raguketu_dhosham IS NULL
                #         )
                #     """)

                # Strict dosham filters — only apply fallback if primary is missing
                strict_conditions = []
                # if not ragu or chev:
                if ragukethu and ragukethu.lower() == 'yes':
                
                        base_query += " AND (LOWER(e.calc_raguketu_dhosham) = 'yes' OR LOWER(e.calc_raguketu_dhosham) = 'true' OR e.calc_raguketu_dhosham = '1' OR e.calc_raguketu_dhosham = 1 OR e.calc_raguketu_dhosham IS NULL OR e.calc_raguketu_dhosham ='' )"
                elif ragukethu and ragukethu.lower() == 'no':
                        base_query += "  AND (LOWER(e.calc_raguketu_dhosham) = 'no' OR LOWER(e.calc_raguketu_dhosham) = 'false' OR e.calc_raguketu_dhosham = '2' OR e.calc_raguketu_dhosham = 2 OR e.calc_raguketu_dhosham IS NULL OR e.calc_raguketu_dhosham ='')"

                if chevvai and chevvai.lower() == 'yes':
                        # base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"

                        base_query += " AND (LOWER(e.calc_chevvai_dhosham) = 'yes' OR LOWER(e.calc_chevvai_dhosham) = 'true' OR e.calc_chevvai_dhosham = '1' OR e.calc_chevvai_dhosham = 1 OR e.calc_chevvai_dhosham IS NULL OR e.calc_chevvai_dhosham ='')"
                elif chevvai and chevvai.lower() == 'no':
                        base_query += "  AND (LOWER(e.calc_chevvai_dhosham) = 'no' OR LOWER(e.calc_chevvai_dhosham) = 'false' OR e.calc_chevvai_dhosham = '2' OR e.calc_chevvai_dhosham = 2 OR e.calc_chevvai_dhosham IS NULL OR e.calc_chevvai_dhosham ='')"


                # Combine all conditions
                all_conditions = conditions + strict_conditions

                if all_conditions:
                    base_query += f"\nAND ({' OR '.join(all_conditions)})"

                if father_alive is not None and father_alive.strip().lower() in ['yes', 'no']:
                    if father_alive =='yes':
                        base_query += " AND c.father_alive = 'yes'"
                    else:
                        base_query += " AND c.father_alive = 'no'"
                if mother_alive is not None and mother_alive.strip().lower() in ['yes', 'no']:
                    if mother_alive == 'yes':
                        base_query += " AND c.mother_alive = 'yes'"
                    else:
                        base_query += " AND c.mother_alive = 'no'"
                
                if status is not None:
                    # print('status is not none')
                    # print('status is',status)
                    if status == "unsent":
                        action_filter = "" if action_type == "all" else "AND sp.action_type = %s"
                        
                        base_query += " AND a.Status = 1 " #approved Only
                        base_query += """
                        AND NOT EXISTS (
                            SELECT 1 
                            FROM admin_sentprofiles sp
                            WHERE sp.profile_id = %s 
                            AND sp.sentprofile_id = a.ProfileId
                            {action_filter}
                        )""".format(action_filter=action_filter)
                        query_params.append(profile_id)
                        if action_type != "all":
                            query_params.append(action_type)

                    elif status == "sent":
                        # print('status is sent')
                        base_query += " AND a.Status != 0 " #Shows the deleted profiles also if it is already sent but deleted later
                        action_filter = "" if action_type == "all" else "AND sp.action_type = %s"
                        
                        base_query += """
                        AND EXISTS (
                            SELECT 1 
                            FROM admin_sentprofiles sp
                            WHERE sp.profile_id = %s 
                            AND sp.sentprofile_id = a.ProfileId
                            {action_filter}
                        ) """.format(action_filter=action_filter)

                        # base_query += " ORDER BY asp.sent_date DESC "
                        
                        query_params.append(profile_id)
                        if action_type != "all":
                            query_params.append(action_type)
                    else:
                        base_query += " AND a.Status = 1 "   #approved Only
                        pass

            # COUNT
            with connection.cursor() as cursor:
                cursor.execute(base_query, query_params)
                all_ids = [row[0] for row in cursor.fetchall()]

            total = len(all_ids)
            profile_with_indices = {str(i + 1): pid for i, pid in enumerate(all_ids)}
            
            def format_sql_for_debug(query, params):
                def escape(value):
                    if isinstance(value, str):
                        return f"'{value}'"
                    elif value is None:
                        return 'NULL'
                    else:
                        return str(value)
                try:
                    return query % tuple(map(escape, params))
                except Exception as e:
                    print("Error formatting query:", e)
                    return query

            # Usage:
            # print("MySQL Executable Query:")
            # print(format_sql_for_debug(base_query, query_params))

            with connection.cursor() as cursor:
                cursor.execute(base_query, query_params)
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return results, total, profile_with_indices

            return [], 0, {}

        except Exception as e:
            print(f"[ERROR] get_profile_list: {str(e)}")
            return [], 0, {}
    
    @staticmethod
    def get_suggest_profile_list(gender, profile_id, start, per_page, search_profile_id,
                                order_by, search_profession, search_age, search_location,complexion=None,
                                city=None, state=None, education=None, foreign_intrest=None, has_photos=None,
                                height_from=None, height_to=None,
                                matching_stars=None, min_anual_income=None, max_anual_income=None, membership=None,ragu=None, chev=None,
                                father_alive=None, mother_alive=None,marital_status=None,family_status=None,whatsapp_field=None,field_of_study=None,degree=None,exclude_profile_ids=None
                                ):
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(ProfileSuggestedPref, profile_id=profile_id)
            pref_annual_income = partner_pref.pref_anual_income
            pref_annual_income_max = partner_pref.pref_anual_income_max
            pref_marital_status =marital_status or partner_pref.pref_marital_status
            partner_pref_education =education or partner_pref.pref_education
            partner_pref_height_from =height_from or  partner_pref.pref_height_from
            partner_pref_height_to = height_to or partner_pref.pref_height_to
            partner_pref_porutham_star_rasi = partner_pref.pref_porutham_star_rasi
            partner_pref_foreign_interest = partner_pref.pref_foreign_intrest
            partner_pref_ragukethu = partner_pref.pref_ragukethu
            partner_pref_chevvai = partner_pref.pref_chevvai
            partner_pref_familysts = partner_pref.pref_family_status
            partner_pref_state = partner_pref.pref_state
            
            field_of_study = field_of_study or partner_pref.pref_fieldof_study
            degree = degree or partner_pref.degree

            if search_age and search_age.strip().isdigit() and int(search_age) > 0:
                age_diff = int(search_age)
            else:
                try:
                    pref_age_diff = int(partner_pref.pref_age_differences)
                    age_diff = pref_age_diff if pref_age_diff > 0 else 5
                except (ValueError, TypeError):
                    age_diff = 5

            # if gender.upper() == "MALE":
            #     min_age = max(current_age - age_diff, 18)  # 🛡 Never below 18
            #     max_age = current_age
            # elif gender.upper() == "FEMALE":
            #     min_age = max(current_age, 18)             # 🛡 Ensure at least 18
            #     max_age = current_age + age_diff

            if gender.upper() == "MALE":
                max_dob  = profile.Profile_dob + relativedelta(years=age_diff)  # older partner limit
                min_dob = profile.Profile_dob                                  # same age
            elif gender.upper() == "FEMALE":
                max_dob = profile.Profile_dob                                  # same age
                min_dob = profile.Profile_dob - relativedelta(years=age_diff)
                
            min_income_id = pref_annual_income
            max_income_id = pref_annual_income_max

                        
            # Start base query
            base_query = """
                SELECT DISTINCT a.*, e.birthstar_name, e.birth_rasi_name,
                 c.family_status,c.father_occupation,c.suya_gothram,e.calc_chevvai_dhosham,e.calc_raguketu_dhosham,
                    f.degree,f.other_degree, f.profession, f.highest_education,f.actual_income,f.anual_income,f.work_city,
                    f.work_state,f.work_country,f.designation,f.business_name,f.company_name,f.nature_of_business,
                    g.EducationLevel, d.star, h.income FROM logindetails a
                JOIN profile_suggested_pref s ON a.ProfileId = s.profile_id
                JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                JOIN masterbirthstar d ON d.id = e.birthstar_name 
                JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                JOIN mastereducation g ON f.highest_education = g.RowId 
                JOIN masterannualincome h ON h.id = f.anual_income
                LEFT JOIN vw_profile_images pi ON a.ProfileId = pi.profile_id
                WHERE a.Status=1 AND a.Plan_id NOT IN (0,16, 17, 3) AND a.gender != %s AND a.ProfileId != %s
                AND a.Profile_dob BETWEEN %s AND %s"""
                
            query_params = [gender, profile_id, min_dob, max_dob]


            # Education
            # if partner_pref_education and partner_pref_education.strip():
            #     edu_list = [e.strip() for e in partner_pref_education.split(',') if e.strip().isdigit()]
            #     if edu_list:
            #         placeholders = ','.join(['%s'] * len(edu_list))
            #         base_query += f" AND g.RowId IN ({placeholders})"
            #         query_params.extend(edu_list)
            if partner_pref_education:
                base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                query_params.append(partner_pref_education)
            if exclude_profile_ids:
                exclude_ids = [pid for pid in exclude_profile_ids if pid]
                if exclude_ids:
                    placeholders = ','.join(['%s'] * len(exclude_ids))
                    base_query += f" AND a.ProfileId NOT IN ({placeholders})"
                    query_params.extend(exclude_ids)
            # Porutham star/rasi
            # if partner_pref_porutham_star_rasi and partner_pref_porutham_star_rasi.strip():
            #     base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
            #     query_params.append(partner_pref_porutham_star_rasi.strip())

            # Marital status
            if pref_marital_status and pref_marital_status.strip():
                marital_status_str = ",".join(pref_marital_status) if isinstance(pref_marital_status, list) else pref_marital_status.strip()
                base_query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                query_params.append(marital_status_str)

            # Foreign interest
            pref_foreign =foreign_intrest or partner_pref_foreign_interest
            if pref_foreign and pref_foreign.strip().lower() in ['yes', 'no']:
                if pref_foreign.lower() == "yes":
                    base_query += " AND (f.work_country != '1' OR a.Profile_country!='1')"
                elif pref_foreign.lower() == "no":
                    base_query += " AND (f.work_country = '1' OR a.Profile_country='1')"

            # if ragu == 'yes':
            #     base_query += " AND LOWER(e.ragu_dosham) = 'yes'"
            # elif ragu == 'no':
            #     base_query += " AND LOWER(e.ragu_dosham) = 'no'"
            # elif partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'yes':
            #     base_query += " AND LOWER(e.ragu_dosham) = 'yes'"
            # elif partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'no':
            #     base_query += " AND LOWER(e.ragu_dosham) = 'no'"

            # if chev == 'yes':
            #     base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"
            # elif chev == 'no':
            #     base_query += " AND LOWER(e.chevvai_dosaham) = 'no'"
            # elif partner_pref_chevvai and partner_pref_chevvai.lower() == 'yes':
            #     base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"
            # elif partner_pref_chevvai and partner_pref_chevvai.lower() == 'no':
            #     base_query += " AND LOWER(e.chevvai_dosaham) = 'no'"
            
            conditions = []

            if chev and chev.lower() == 'yes':
                conditions.append("""
                    (
                        LOWER(e.calc_chevvai_dhosham) IN ('yes', 'true')
                        OR e.calc_chevvai_dhosham IN ('1', 1)
                        OR e.calc_chevvai_dhosham IS NULL
                    )
                """)

            if ragu and ragu.lower() == 'yes':
                conditions.append("""
                    (
                        LOWER(e.calc_raguketu_dhosham) IN ('yes', 'true')
                        OR e.calc_raguketu_dhosham IN ('1', 1)
                        OR e.calc_raguketu_dhosham IS NULL
                    )
                """)

            # Strict dosham filters — only apply fallback if primary is missing
            strict_conditions = []
            if not chev or ragu:
                if partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'yes':
                    
                    base_query += " AND (LOWER(e.calc_raguketu_dhosham) = 'yes' OR LOWER(e.calc_raguketu_dhosham) = 'True' OR e.calc_raguketu_dhosham = '1' OR e.calc_raguketu_dhosham = 1 OR e.calc_raguketu_dhosham IS NULL OR e.calc_raguketu_dhosham ='' )"
                elif partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'no':
                    base_query += "  AND (LOWER(e.calc_raguketu_dhosham) = 'no' OR LOWER(e.calc_raguketu_dhosham) = 'False' OR e.calc_raguketu_dhosham = '2' OR e.calc_raguketu_dhosham = 2 OR e.calc_raguketu_dhosham IS NULL OR e.calc_raguketu_dhosham ='')"

                if partner_pref_chevvai and partner_pref_chevvai.lower() == 'yes':
                    # base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"

                    base_query += " AND (LOWER(e.calc_chevvai_dhosham) = 'yes' OR LOWER(e.calc_chevvai_dhosham) = 'True' OR e.calc_chevvai_dhosham = '1' OR e.calc_chevvai_dhosham = 1 OR e.calc_chevvai_dhosham IS NULL OR e.calc_chevvai_dhosham ='')"
                elif partner_pref_chevvai and partner_pref_chevvai.lower() == 'no':
                    base_query += "  AND (LOWER(e.calc_chevvai_dhosham) = 'no' OR LOWER(e.calc_chevvai_dhosham) = 'False' OR e.calc_chevvai_dhosham = '2' OR e.calc_chevvai_dhosham = 2 OR e.calc_chevvai_dhosham IS NULL OR e.calc_chevvai_dhosham ='')"


            # Combine all conditions
            all_conditions = conditions + strict_conditions

            if all_conditions:
                base_query += f"\nAND ({' OR '.join(all_conditions)})"
            # Height filters
            if partner_pref_height_from and partner_pref_height_to:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([partner_pref_height_from, partner_pref_height_to])
            elif partner_pref_height_from:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(partner_pref_height_to)

            # Search filters
            if search_profile_id:
                base_query += " AND (a.ProfileId = %s OR a.Profile_name LIKE %s)"
                query_params.extend([search_profile_id, f"%{search_profile_id}%"])

            if search_profession:
                profession_list = [p.strip() for p in search_profession.split(',') if p.strip().isdigit()]
                if profession_list:
                    placeholders = ','.join(['%s'] * len(profession_list))
                    base_query += f" AND f.profession IN ({placeholders})"
                    query_params.extend(profession_list)

            if search_location:
                base_query += " AND a.Profile_state = %s"
                query_params.append(search_location)

            # Matching stars
            if matching_stars and matching_stars.strip():
                base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                query_params.append(matching_stars.strip())
            elif partner_pref_porutham_star_rasi and partner_pref_porutham_star_rasi.strip():
                base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                query_params.append(partner_pref_porutham_star_rasi.strip())
                
            if complexion:
                complexion_list = [c.strip() for c in complexion.split(',') if c.strip().isdigit()]
                if complexion_list:
                    placeholders = ','.join(['%s'] * len(complexion_list))
                    base_query += f" AND a.Profile_complexion IN ({placeholders})"
                    query_params.extend(complexion_list)
                 
            if has_photos and has_photos.lower() == "yes":
                base_query += " AND pi.first_image_id IS NOT NULL" 
                  
            if city:
                base_query += " AND a.Profile_city = %s"
                query_params.append(city)
                
            if state:
                base_query += """
                    AND (
                        FIND_IN_SET(f.work_state, %s) > 0 OR
                        FIND_IN_SET(a.Profile_state, %s) > 0 OR
                        a.Profile_state IS NULL OR
                        a.Profile_state = ''
                    )
                """
                query_params.extend([state, state])

            elif partner_pref_state:
                base_query += """
                    AND (
                        FIND_IN_SET(f.work_state, %s) > 0 OR
                        FIND_IN_SET(a.Profile_state, %s) > 0 OR
                        a.Profile_state IS NULL OR
                        a.Profile_state = ''
                    )
                """
                query_params.extend([partner_pref_state, partner_pref_state])
                
            if membership:
                membership_ids = [m.strip() for m in membership.split(",") if m.strip().isdigit()]
                if membership_ids:
                    placeholders = ','.join(['%s'] * len(membership_ids))
                    base_query += f" AND a.Plan_id IN ({placeholders})"
                    query_params.extend(membership_ids)
                    
            if father_alive and father_alive.strip().lower() in ['yes', 'no']:
                base_query += " AND c.father_alive = %s"
                query_params.append(father_alive.strip().lower())

            if mother_alive and mother_alive.strip().lower() in ['yes', 'no']:
                base_query += " AND c.mother_alive = %s"
                query_params.append(mother_alive.strip().lower())
            
            if family_status:
                statuses = [s.strip() for s in str(family_status).split(',') if s.strip()]
                if statuses:
                    family_status_filters = []
                    for status in statuses:
                        family_status_filters.append("FIND_IN_SET(%s, c.family_status) > 0")
                        query_params.append(status)
                    base_query += " AND (" + " OR ".join(family_status_filters) + ")"
            else:
                if partner_pref_familysts:
                    base_query += " AND ((FIND_IN_SET(c.family_status, %s) > 0) OR (c.family_status  IS NULL OR c.family_status=''))"
                    query_params.append(partner_pref_familysts)
                 
                 
            if field_of_study:
                fields = [f.strip() for f in field_of_study.split(',') if f.strip()]
                if fields:
                    placeholders = ','.join(['%s'] * len(fields))
                    base_query += f" AND f.field_ofstudy IN ({placeholders})"
                    query_params.extend(fields)
                    
            if degree:
                degrees = [d.strip() for d in degree.split(',') if d.strip()]
                if degrees:
                    placeholders = ','.join(['%s'] * len(degrees))
                    base_query += f" AND f.degree IN ({placeholders})"
                    query_params.extend(degrees)
            else:
                base_query += """ AND
                ( f.degree IN (0,'86') OR f.degree IS NULL OR f.degree='')"""
                    
            manual_min = min_anual_income if min_anual_income not in [None, "", "null"] else None
            manual_max = max_anual_income if max_anual_income not in [None, "", "null"] else None

            if manual_min and manual_max:
                base_query += " AND (f.anual_income BETWEEN %s AND %s OR f.anual_income IS NULL OR f.anual_income = '')"
                query_params.extend([int(manual_min), int(manual_max)])
            elif min_income_id and max_income_id:
                base_query += " AND (f.anual_income BETWEEN %s AND %s OR f.anual_income IS NULL OR f.anual_income = '')"
                query_params.extend([int(min_income_id), int(max_income_id)])
    
            try:
                order_by = int(order_by)
            except (ValueError, TypeError):
                order_by = None

            if order_by == 1:
                orderby_cond = " ORDER BY a.DateOfJoin ASC"
            elif order_by == 2:
                orderby_cond = " ORDER BY a.DateOfJoin DESC"
            else:
                orderby_cond = " ORDER BY a.DateOfJoin DESC"

            # Full query
            query = base_query + orderby_cond

            # For count + profile indexing
            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                all_profile_ids = [row[1] for row in cursor.fetchall()]
                total_count = len(all_profile_ids)
                profile_with_indices = {str(i + 1): pid for i, pid in enumerate(all_profile_ids)}

            # Add pagination
            query += " LIMIT %s OFFSET %s"
            query_params.extend([per_page, start])
            def format_sql_for_debug(query, params):
                def escape(value):
                    if isinstance(value, str):
                        return f"'{value}'"
                    elif value is None:
                        return 'NULL'
                    else:
                        return str(value)
                try:
                    return query % tuple(map(escape, params))
                except Exception as e:
                    # print("Error formatting query:", e)
                    return query
                
            # print("MySQL Executable Query:", format_sql_for_debug(query, query_params))
            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return results, total_count, profile_with_indices

            return [], 0, {}

        except Exception as e:
            print(f"Suggest Profile Error: {str(e)}")
            return [], 0, {}
       
    @staticmethod
    def get_unique_suggested_match_count(gender, profile_id):
        try:
            # Suggested profiles list
            suggested_profiles = gpt.get_profile_list_for_pref_type(
                profile_id=profile_id,
                use_suggested=True
            )

            suggested_ids = {p['ProfileId'] for p in suggested_profiles if p.get("ProfileId")}
            # print(f"Total suggested profiles: {len(suggested_ids)}")
            # Matched profiles list
            matched_profiles = gpt.get_profile_list_for_pref_type(
                profile_id=profile_id,
                use_suggested=False
            )
            partner_ids = {r['ProfileId'] for r in matched_profiles if r.get("ProfileId")}
            # print(f"Total matched profiles: {len(partner_ids)}")
            # Subtract partner matches from suggested
            unique_ids = suggested_ids - partner_ids

            # print(f"Total suggested: {len(suggested_ids)}")
            # print(f"Matched profiles: {len(partner_ids)}")
            # print(f"Unique suggestions (suggested - matched): {len(unique_ids)}")

            return len(unique_ids)

        except Exception as e:
            # print("Error in get_unique_suggested_match_count:", str(e))
            return 0
    
    @staticmethod
    def get_profile_match_count(gender, profile_id):
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            my_family = get_object_or_404(ProfileFamilyDetails, profile_id=profile_id)
            my_suya_gothram = my_family.suya_gothram
            my_suya_gothram_admin = my_family.suya_gothram_admin

            pref_annual_income = partner_pref.pref_anual_income
            pref_annual_income_max = partner_pref.pref_anual_income_max
            
            pref_marital_status = partner_pref.pref_marital_status
            partner_pref_education = partner_pref.pref_education
            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi = partner_pref.pref_porutham_star_rasi
            ragukethu = partner_pref.pref_ragukethu
            chevvai = partner_pref.pref_chevvai
            pref_foreign = partner_pref.pref_foreign_intrest
            partner_pref_state = partner_pref.pref_state
            partner_pref_familysts = partner_pref.pref_family_status
            field_of_study = partner_pref.pref_fieldof_study
            partner_pref_profess = partner_pref.pref_profession
            degree = partner_pref.degree
            # Get min and max income
            # min_income, max_income = 0, 0
            # if pref_annual_income:
            #     with connection.cursor() as cursor:
            #         cursor.execute("""
            #             SELECT MIN(income_amount), MAX(income_amount)
            #             FROM masterannualincome
            #             WHERE FIND_IN_SET(id, %s) > 0
            #         """, [pref_annual_income])
            #         min_max_income = cursor.fetchone()
            #         if min_max_income:
            #             min_income, max_income = min_max_income

            # Parse age difference
            try:
                pref_age_diff = int(partner_pref.pref_age_differences)
                age_diff = pref_age_diff if pref_age_diff > 0 else 5
            except (ValueError, TypeError):
                age_diff = 5

            # if gender.upper() == "MALE":
            #     min_age = max(current_age - age_diff, 18)
            #     max_age = current_age
            # elif gender.upper() == "FEMALE":
            #     min_age = max(current_age, 18)
            #     max_age = current_age + age_diff
            if gender.upper() == "MALE":
                max_dob  = profile.Profile_dob + relativedelta(years=age_diff)  # older partner limit
                min_dob = profile.Profile_dob                                  # same age
            elif gender.upper() == "FEMALE":
                max_dob = profile.Profile_dob                                  # same age
                min_dob = profile.Profile_dob - relativedelta(years=age_diff)

            base_query = """
                SELECT COUNT(*) as match_count
                FROM logindetails a
                JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                JOIN profile_horoscope e ON a.ProfileId = e.profile_id
                JOIN masterbirthstar d ON d.id = e.birthstar_name
                JOIN profile_edudetails f ON a.ProfileId = f.profile_id
                lEFT JOIN mastereducation g ON f.highest_education = g.RowId
                lEFT JOIN masterannualincome h ON h.id = f.anual_income
                LEFT JOIN profile_visibility pv ON pv.profile_id = a.ProfileId
                JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                LEFT JOIN vw_profile_images pi ON a.ProfileId = pi.profile_id
                LEFT JOIN profile_visit_logs v ON v.viewed_profile = a.ProfileId AND v.profile_id = %s

                LEFT JOIN masterprofession prof ON f.profession = prof.RowId
                JOIN profile_edudetails f_from ON f_from.profile_id = %s
                JOIN profile_familydetails f1_from ON f1_from.profile_id = %s
                JOIN profile_horoscope h1_from ON h1_from.profile_id = %s
                JOIN logindetails l1_from ON l1_from.ProfileId = %s
                LEFT JOIN masterannualincome h_from ON h_from.id = f_from.anual_income
                
                
                WHERE a.Status = 1 
                AND (
                        -- If the opposite profile is Platinum, apply pv only when set
                        (
                            a.Plan_id IN (3,17)
                        AND (
                            (%s = 'male' 
                                AND (pv.visibility_age_from IS NULL OR pv.visibility_age_from = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= pv.visibility_age_from)
                                AND (pv.visibility_age_to IS NULL OR pv.visibility_age_to = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= pv.visibility_age_to)
                                AND a.Profile_dob > %s -- viewer must be older than candidate
                            )
                            OR
                            (%s = 'female' 
                                AND (pv.visibility_age_from IS NULL OR pv.visibility_age_from = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= pv.visibility_age_from)
                                AND (pv.visibility_age_to IS NULL OR pv.visibility_age_to = '' 
                                    OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= pv.visibility_age_to)
                                AND a.Profile_dob < %s -- viewer must be younger than candidate
                            )
                        )
                        AND (pv.visibility_height_from IS NULL OR pv.visibility_height_from = '' OR l1_from.Profile_height >= pv.visibility_height_from)
                        AND (pv.visibility_height_to IS NULL OR pv.visibility_height_to = '' OR l1_from.Profile_height <= pv.visibility_height_to)
                        AND (pv.visibility_profession IS NULL OR pv.visibility_profession = '' OR FIND_IN_SET(f_from.profession, pv.visibility_profession) > 0)
                        AND (pv.visibility_education IS NULL OR pv.visibility_education = '' OR FIND_IN_SET(f_from.highest_education, pv.visibility_education) > 0)
                        AND (pv.visibility_anual_income IS NULL OR pv.visibility_anual_income = '' 
                        OR h_from.id >= pv.visibility_anual_income)
                        AND (pv.visibility_anual_income_max IS NULL OR pv.visibility_anual_income_max = '' 
                        OR h_from.id <= pv.visibility_anual_income_max)

                        AND (pv.degree IS NULL OR pv.degree = '' OR FIND_IN_SET(f_from.degree, pv.degree) > 0)
                        AND (pv.visibility_field_of_study IS NULL OR pv.visibility_field_of_study = '' OR FIND_IN_SET(f_from.field_ofstudy, pv.visibility_field_of_study) > 0)
                        AND (pv.visibility_family_status IS NULL OR pv.visibility_family_status = '' OR FIND_IN_SET(f1_from.family_status, pv.visibility_family_status) > 0)
                        -- Chevvai visibility
                        AND (
                            pv.visibility_chevvai IS NULL OR pv.visibility_chevvai = '' OR LOWER(pv.visibility_chevvai) = 'both'
                            OR (
                                (LOWER(pv.visibility_chevvai) IN ('yes','true','1') 
                                    AND (LOWER(h1_from.calc_chevvai_dhosham) = 'yes' OR LOWER(h1_from.calc_chevvai_dhosham) = 'true' 
                                        OR h1_from.calc_chevvai_dhosham = '1' OR h1_from.calc_chevvai_dhosham = 1 
                                        OR h1_from.calc_chevvai_dhosham IS NULL OR h1_from.calc_chevvai_dhosham =''))
                                OR
                                (LOWER(pv.visibility_chevvai) IN ('no','false','2') 
                                    AND (LOWER(h1_from.calc_chevvai_dhosham) = 'no' OR LOWER(h1_from.calc_chevvai_dhosham) = 'false' 
                                        OR h1_from.calc_chevvai_dhosham = '2' OR h1_from.calc_chevvai_dhosham = 2 
                                        OR h1_from.calc_chevvai_dhosham IS NULL OR h1_from.calc_chevvai_dhosham =''))
                            )
                        )
                        -- Ragukethu visibility
                        AND (
                            pv.visibility_ragukethu IS NULL OR pv.visibility_ragukethu = '' OR LOWER(pv.visibility_ragukethu) = 'both'
                            OR (
                                (LOWER(pv.visibility_ragukethu) IN ('yes','true','1') 
                                    AND (LOWER(h1_from.calc_raguketu_dhosham) = 'yes' OR LOWER(h1_from.calc_raguketu_dhosham) = 'true' 
                                        OR h1_from.calc_raguketu_dhosham = '1' OR h1_from.calc_raguketu_dhosham = 1 
                                        OR h1_from.calc_raguketu_dhosham IS NULL OR h1_from.calc_raguketu_dhosham =''))
                                OR
                                (LOWER(pv.visibility_ragukethu) IN ('no','false','2') 
                                    AND (LOWER(h1_from.calc_raguketu_dhosham) = 'no' OR LOWER(h1_from.calc_raguketu_dhosham) = 'false' 
                                        OR h1_from.calc_raguketu_dhosham = '2' OR h1_from.calc_raguketu_dhosham = 2 
                                        OR h1_from.calc_raguketu_dhosham IS NULL OR h1_from.calc_raguketu_dhosham =''))
                            )
                        )
                    )
                    OR 
                    -- If opposite profile is not Platinum → skip pv.* checks
                    (a.Plan_id NOT IN (3,16,17))
                )
                AND a.gender != %s
                AND a.ProfileId != %s
                AND a.Profile_dob BETWEEN %s AND %s """

            params = [profile_id,profile_id,profile_id,profile_id,profile_id,gender,profile.Profile_dob,gender,profile.Profile_dob, gender, profile_id, min_dob, max_dob]

            pref_annual_income = None if pref_annual_income in ("null", "", None) else pref_annual_income
            pref_annual_income_max = None if pref_annual_income_max in ("null", "", None) else pref_annual_income_max
            
            if pref_annual_income and pref_annual_income_max:
                base_query += "AND ((f.anual_income BETWEEN %s AND %s ) OR (f.anual_income IS NULL) OR (f.anual_income = '')) "
                params.extend([int(pref_annual_income),int(pref_annual_income_max)])
            # Gothram filter
            if my_suya_gothram_admin and my_suya_gothram_admin != '0':
                base_query += " AND (c.suya_gothram_admin IS NULL OR c.suya_gothram_admin = '' OR c.suya_gothram_admin != %s)"
                params.append(str(my_suya_gothram_admin))
            if my_suya_gothram:
                base_query += " AND (c.suya_gothram IS NULL OR c.suya_gothram = '' OR c.suya_gothram != %s )"
                params.append(my_suya_gothram)

            # Family status
            if partner_pref_familysts:
                base_query += " AND (FIND_IN_SET(c.family_status, %s) > 0 OR c.family_status IS NULL OR c.family_status = '')"
                params.append(partner_pref_familysts)

            # Education
            if partner_pref_education:
                base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                params.append(partner_pref_education)

            # Income
            # if min_income and max_income:
            #     base_query += " AND ((h.income_amount BETWEEN %s AND %s) OR h.income_amount IS NULL OR h.income_amount = '')"
            #     params.extend([min_income, max_income])

            # Stars
            if partner_pref_porutham_star_rasi:
                base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                params.append(partner_pref_porutham_star_rasi)

            # Marital Status
            if pref_marital_status:
                base_query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                params.append(pref_marital_status)

            # Height
            if partner_pref_height_from and partner_pref_height_to:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                params.extend([partner_pref_height_from, partner_pref_height_to])
            elif partner_pref_height_from:
                base_query += " AND a.Profile_height >= %s"
                params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                base_query += " AND a.Profile_height <= %s"
                params.append(partner_pref_height_to)

            # Foreign Interest
            if pref_foreign and pref_foreign.strip().lower() in ['yes', 'no']:
                if pref_foreign.lower() == "yes":
                    base_query += " AND (f.work_country != '1' OR f.work_country IS NULL OR f.work_country='' OR a.Profile_country!='1' OR a.Profile_country='' OR a.Profile_country IS NULL)"
                else:
                    base_query += " AND (f.work_country = '1' OR f.work_country IS NULL OR f.work_country='' OR a.Profile_country='1')"

            if field_of_study:
                fields = [f.strip() for f in field_of_study.split(',') if f.strip()]
                if fields:
                    placeholders = ','.join(['%s'] * len(fields))
                    base_query += f" AND f.field_ofstudy IN ({placeholders})"
                    params.extend(fields)
                
            if degree:
                degrees = [d.strip() for d in degree.split(',') if d.strip()]
                if degrees:
                    placeholders = ','.join(['%s'] * len(degrees))
                    # base_query += f" AND f.degree IN ({placeholders})"
                    base_query += f" AND f.degree IN ({placeholders}) OR f.degree IN (0,'86') OR f.degree IS NULL OR f.degree='')"
                    params.extend(degrees)

            if partner_pref_profess:
                    professions = [p.strip() for p in partner_pref_profess.split(",") if p.strip()]
                    placeholders = ", ".join(["%s"] * len(professions))
                    base_query += f" AND f.profession IN ({placeholders})"
                    params.extend(professions)
            # else:
            #     base_query += """ AND
            #     ( f.degree IN (0,'86') OR f.degree IS NULL OR f.degree='')"""
             
            if ragukethu and ragukethu.lower() == 'yes':
                
                base_query += " AND (LOWER(e.calc_raguketu_dhosham) = 'yes' OR LOWER(e.calc_raguketu_dhosham) = 'True' OR e.calc_raguketu_dhosham = '1' OR e.calc_raguketu_dhosham = 1 OR e.calc_raguketu_dhosham IS NULL OR e.calc_raguketu_dhosham ='' )"
            elif ragukethu and ragukethu.lower() == 'no':
                base_query += "  AND (LOWER(e.calc_raguketu_dhosham) = 'no' OR LOWER(e.calc_raguketu_dhosham) = 'False' OR e.calc_raguketu_dhosham = '2' OR e.calc_raguketu_dhosham = 2 OR e.calc_raguketu_dhosham IS NULL OR e.calc_raguketu_dhosham ='')"

            if chevvai and chevvai.lower() == 'yes':
                # base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"

                base_query += " AND (LOWER(e.calc_chevvai_dhosham) = 'yes' OR LOWER(e.calc_chevvai_dhosham) = 'True' OR e.calc_chevvai_dhosham = '1' OR e.calc_chevvai_dhosham = 1 OR e.calc_chevvai_dhosham IS NULL OR e.calc_chevvai_dhosham ='')"
            elif chevvai and chevvai.lower() == 'no':
                base_query += "  AND (LOWER(e.calc_chevvai_dhosham) = 'no' OR LOWER(e.calc_chevvai_dhosham) = 'False' OR e.calc_chevvai_dhosham = '2' OR e.calc_chevvai_dhosham = 2 OR e.calc_chevvai_dhosham IS NULL OR e.calc_chevvai_dhosham ='')"


            # State filter (partner pref state)
            if partner_pref_state:
                base_query += """
                    AND (
                        FIND_IN_SET(f.work_state, %s) > 0 OR
                        FIND_IN_SET(a.Profile_state, %s) > 0 OR
                        a.Profile_state IS NULL OR
                        a.Profile_state = ''
                    )
                """
                params.extend([partner_pref_state, partner_pref_state])

            # Debug Query
            def format_sql_for_debug(query, params):
                def escape(value):
                    if isinstance(value, str):
                        return f"'{value}'"
                    elif value is None:
                        return 'NULL'
                    return str(value)
                return query % tuple(map(escape, params))

            # print("Final matching Match Count SQL:")
            # print(format_sql_for_debug(base_query, params))

            # print("COUNT EXECUTABLE QUERY ➤\n", format_sql_for_debug(base_query, params))

            with connection.cursor() as cursor:
                cursor.execute(base_query, params)
                result = cursor.fetchone()
                return result[0] if result else 0

        except Exception as e:
            # print(f"[ERROR] get_profile_match_count: {str(e)}")
            return 0
        
    @staticmethod
    def get_suggest_match_count(gender, profile_id, has_photos=None, search_profession=None,
                                search_location=None, city=None, state=None,
                                education=None, foreign_interest=None,
                                height_from=None, height_to=None,
                                matching_stars=None, min_anual_income=None, max_anual_income=None,
                                membership=None, ragu=None, chev=None,
                                father_alive=None, mother_alive=None, marital_status=None,
                                family_status=None, complexion=None):
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            current_age = calculate_age(profile.Profile_dob)

            suggest_pref = get_object_or_404(ProfileSuggestedPref, profile_id=profile_id)
            pref_annual_income = suggest_pref.pref_anual_income
            pref_marital_status = marital_status or suggest_pref.pref_marital_status
            partner_pref_education = education or suggest_pref.pref_education
            partner_pref_height_from = height_from or suggest_pref.pref_height_from
            partner_pref_height_to = height_to or suggest_pref.pref_height_to
            partner_pref_porutham_star_rasi = suggest_pref.pref_porutham_star_rasi
            partner_pref_state = suggest_pref.pref_state
            partner_pref_ragukethu = suggest_pref.pref_ragukethu
            partner_pref_chevvai = suggest_pref.pref_chevvai
            field_of_study = suggest_pref.pref_fieldof_study
            degree =suggest_pref.degree

            # Age Range
            try:
                age_difference = int(suggest_pref.pref_age_differences)
                if age_difference <= 0:
                    age_difference = 5
            except Exception:
                age_difference = 5

            if gender.upper() == "MALE":
                max_dob  = profile.Profile_dob + relativedelta(years=age_difference)  # older partner limit
                min_dob = profile.Profile_dob                                  # same age
            elif gender.upper() == "FEMALE":
                max_dob = profile.Profile_dob                                  # same age
                min_dob = profile.Profile_dob - relativedelta(years=age_difference)

            # Income range
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MIN(income_amount), MAX(income_amount)
                    FROM masterannualincome
                    WHERE FIND_IN_SET(id, %s) > 0
                """, [pref_annual_income])
                min_income, max_income = cursor.fetchone() or (0, 0)

            query = """
                SELECT COUNT(*) as match_count
                FROM logindetails a
                JOIN profile_suggested_pref s ON a.ProfileId = s.profile_id
                JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                JOIN profile_horoscope e ON a.ProfileId = e.profile_id
                JOIN masterbirthstar d ON d.id = e.birthstar_name
                JOIN profile_edudetails f ON a.ProfileId = f.profile_id
                JOIN mastereducation g ON f.highest_education = g.RowId
                JOIN masterannualincome h ON h.id = f.anual_income
                JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                LEFT JOIN profile_images pi ON a.ProfileId = pi.profile_id
                WHERE a.Status = 1
                AND a.Plan_id NOT IN (0, 3, 16, 17)
                AND a.gender != %s
                AND a.ProfileId != %s
                AND a.Profile_dob BETWEEN %s AND %s"""

            params = [gender, profile_id, min_dob, max_dob]

            if min_income and max_income:
                query += " AND ((h.income_amount BETWEEN %s AND %s) OR h.income_amount IS NULL OR h.income_amount = '')"
                params += [min_anual_income or min_income, max_anual_income or max_income]

            if partner_pref_education:
                query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                params.append(partner_pref_education)

            if partner_pref_porutham_star_rasi:
                query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                params.append(partner_pref_porutham_star_rasi)

            if pref_marital_status:
                query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                params.append(pref_marital_status)

            if partner_pref_height_from and partner_pref_height_to:
                query += " AND a.Profile_height BETWEEN %s AND %s"
                params += [partner_pref_height_from, partner_pref_height_to]
            elif partner_pref_height_from:
                query += " AND a.Profile_height >= %s"
                params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                query += " AND a.Profile_height <= %s"
                params.append(partner_pref_height_to)

            # Foreign interest
            if foreign_interest:
                if foreign_interest.lower() == 'yes':
                    query += " AND f.work_country != '1'"
                elif foreign_interest.lower() == 'no':
                    query += " AND f.work_country = '1'"

            # Matching Stars
            if matching_stars:
                star_ids = [s.strip() for s in matching_stars.split(',') if s.strip().isdigit()]
                if star_ids:
                    placeholders = ','.join(['%s'] * len(star_ids))
                    query += f" AND e.birthstar_name IN ({placeholders})"
                    params += star_ids

            # Profession
            if search_profession:
                profession_ids = [p.strip() for p in search_profession.split(',') if p.strip().isdigit()]
                if profession_ids:
                    placeholders = ','.join(['%s'] * len(profession_ids))
                    query += f" AND f.profession IN ({placeholders})"
                    params += profession_ids

            # Photo filter
            if has_photos and has_photos.lower() == "yes":
                query += " AND pi.image_approved = 1"

            # Complexion
            if complexion:
                complexion_list = [c.strip() for c in complexion.split(',') if c.strip().isdigit()]
                if complexion_list:
                    placeholders = ','.join(['%s'] * len(complexion_list))
                    query += f" AND a.Profile_complexion IN ({placeholders})"
                    params += complexion_list

            # City
            if city:
                query += " AND a.Profile_city = %s"
                params.append(city)

            # State / Work State
            if state:
                query += """
                    AND (
                        FIND_IN_SET(f.work_state, %s) > 0 OR
                        FIND_IN_SET(a.Profile_state, %s) > 0 OR
                        a.Profile_state IS NULL OR a.Profile_state = ''
                    )
                """
                params += [state, state]
            elif partner_pref_state:
                query += """
                    AND (
                        FIND_IN_SET(f.work_state, %s) > 0 OR
                        FIND_IN_SET(a.Profile_state, %s) > 0 OR
                        a.Profile_state IS NULL OR a.Profile_state = ''
                    )
                """
                params += [partner_pref_state, partner_pref_state]

            # Father / Mother Alive
            if father_alive and father_alive.lower() in ['yes', 'no']:
                query += " AND c.father_alive = %s"
                params.append(father_alive.lower())

            if mother_alive and mother_alive.lower() in ['yes', 'no']:
                query += " AND c.mother_alive = %s"
                params.append(mother_alive.lower())

            # Family Status
            if family_status:
                family_values = [f.strip() for f in family_status.split(',') if f.strip()]
                if family_values:
                    fs_conditions = []
                    for f in family_values:
                        fs_conditions.append("FIND_IN_SET(%s, c.family_status) > 0")
                        params.append(f)
                    query += " AND (" + " OR ".join(fs_conditions) + ")"

            # Membership
            if membership:
                mem_ids = [m.strip() for m in membership.split(',') if m.strip().isdigit()]
                if mem_ids:
                    placeholders = ','.join(['%s'] * len(mem_ids))
                    query += f" AND a.Plan_id IN ({placeholders})"
                    params += mem_ids

            # ✅ Dosham filters — same logic as profile list
            conditions = []
            if chev and chev.lower() == 'yes':
                conditions.append("""
                    (
                        LOWER(e.calc_chevvai_dhosham) IN ('yes', 'true')
                        OR e.calc_chevvai_dhosham IN ('1', 1)
                        OR e.calc_chevvai_dhosham IS NULL
                    )
                """)
            if ragu and ragu.lower() == 'yes':
                conditions.append("""
                    (
                        LOWER(e.calc_raguketu_dhosham) IN ('yes', 'true')
                        OR e.calc_raguketu_dhosham IN ('1', 1)
                        OR e.calc_raguketu_dhosham IS NULL
                    )
                """)
                
            if field_of_study:
                fields = [f.strip() for f in field_of_study.split(',') if f.strip()]
                if fields:
                    placeholders = ','.join(['%s'] * len(fields))
                    base_query += f" AND f.field_ofstudy IN ({placeholders})"
                    params.extend(fields)
                
            if degree:
                degrees = [d.strip() for d in degree.split(',') if d.strip()]
                if degrees:
                    placeholders = ','.join(['%s'] * len(degrees))
                    base_query += f" AND f.degree IN ({placeholders})"
                    params.extend(degrees)
            else:
                base_query += """ AND
                ( f.degree IN (0,'86') OR f.degree IS NULL OR f.degree='')"""
            # Strict fallback
            strict_conditions = []
            def add_strict_condition(field, value, fallback_value):
                if value and value.lower() in ['yes', 'no']:
                    strict_conditions.append(f"LOWER(e.{field}) = '{value.lower()}'")
                elif fallback_value and fallback_value.lower() in ['yes', 'no']:
                    strict_conditions.append(f"LOWER(e.{field}) = '{fallback_value.lower()}'")

            add_strict_condition("calc_raguketu_dhosham", ragu, partner_pref_ragukethu)
            add_strict_condition("calc_chevvai_dhosham", chev, partner_pref_chevvai)

            dosham_clauses = conditions + strict_conditions
            if dosham_clauses:
                query += f"\nAND ({' OR '.join(dosham_clauses)})"

            # Debug SQL
            def format_sql_for_debug(query, params):
                def escape(value):
                    if value is None:
                        return 'NULL'
                    if isinstance(value, str):
                        return f"'{value}'"
                    return str(value)

                for p in params:
                    query = query.replace('%s', escape(p), 1)
                return query

            # print("🔍 Final Suggest Match Count SQL:")
            # print(format_sql_for_debug(query, params))

            with connection.cursor() as cursor:
                cursor.execute(query, params)
                count_row = cursor.fetchone()
                return count_row[0] if count_row else 0

        except Exception as e:
            print("[ERROR] get_suggest_match_count:", e)
            return 0
    
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

    @staticmethod
    def get_profile_visibility(
        gender,
        profile_id,
        start,
        per_page,
        order_by,
        profession=None,
        age_from=None,
        age_to=None,
        education=None,
        foreign_intrest=None,
        height_from=None,
        height_to=None,
        min_anual_income=None,
        max_anual_income=None,
        ragu=None,
        chev=None,
        marital_status=None,
        family_status=None,
        field_of_study=None,
        degree=None
    ):
        try:
            today = date.today()

            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            profile_dob = profile.Profile_dob

            partner_pref = get_object_or_404(ProfileVisibility, profile_id=profile_id)

            # Preferences fallback
            pref_annual_income = partner_pref.visibility_anual_income
            pref_annual_income_max = partner_pref.visibility_anual_income_max
            partner_pref_education = education or partner_pref.visibility_education
            partner_pref_age_from = age_from or partner_pref.visibility_age_from
            partner_pref_age_to = age_to or partner_pref.visibility_age_to  # ✅ fixed
            partner_pref_height_from = height_from or partner_pref.visibility_height_from
            partner_pref_height_to = height_to or partner_pref.visibility_height_to
            partner_pref_profession = profession or partner_pref.visibility_profession
            partner_pref_foreign_interest = partner_pref.visibility_foreign_interest
            partner_pref_ragukethu = ragu or partner_pref.visibility_ragukethu
            partner_pref_chevvai = chev or partner_pref.visibility_chevvai
            partner_pref_familysts = family_status or partner_pref.visibility_family_status
            field_of_study = field_of_study or partner_pref.visibility_field_of_study
            degree = degree or partner_pref.degree
            
            my_family= get_object_or_404(ProfileFamilyDetails, profile_id=profile_id)

            my_suya_gothram=my_family.suya_gothram
            my_suya_gothram_admin=my_family.suya_gothram_admin
            # DOB range calculation
            try:
                if partner_pref_age_from and partner_pref_age_to:
                    from_age = int(partner_pref_age_from)
                    to_age = int(partner_pref_age_to)
                    if from_age > 0 and to_age > 0 and from_age <= to_age:
                        min_dob = today - relativedelta(years=to_age)
                        max_dob = today - relativedelta(years=from_age)
                    else:
                        raise ValueError("Invalid age range")
                else:
                    if gender.upper() == "MALE":
                        min_dob = profile_dob - relativedelta(years=5)
                        max_dob = profile_dob
                    elif gender.upper() == "FEMALE":
                        min_dob = profile_dob
                        max_dob = profile_dob + relativedelta(years=5)
            except (ValueError, TypeError):
                if gender.upper() == "MALE":
                    min_dob = profile_dob - relativedelta(years=5)
                    max_dob = profile_dob
                else:
                    min_dob = profile_dob
                    max_dob = profile_dob + relativedelta(years=5)

            # Base query
            base_query = """
                SELECT DISTINCT a.*, e.birthstar_name, e.birth_rasi_name,
                       c.family_status, c.father_occupation, c.suya_gothram,
                       e.calc_chevvai_dhosham, e.calc_raguketu_dhosham,
                       f.degree, f.other_degree, f.profession, f.highest_education,
                       f.actual_income, f.anual_income, f.work_city, f.work_state,
                       f.work_country, f.designation, f.business_name, f.company_name,
                       f.nature_of_business,
                       g.EducationLevel, d.star, h.income
                FROM logindetails a
                JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                LEFT JOIN masterbirthstar d ON d.id = e.birthstar_name 
                JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                LEFT JOIN mastereducation g ON f.highest_education = g.RowId 
                LEFT JOIN masterannualincome h ON h.id = f.anual_income
                LEFT JOIN masterprofession r ON r.RowId = f.profession
                LEFT JOIN profile_images pi ON a.ProfileId = pi.profile_id
                WHERE a.Status = 1 
                  AND a.Plan_id NOT IN (0,16)
                  AND a.gender != %s 
                  AND a.ProfileId != %s
                AND (
            (%s = 'male' 
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= %s)
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= %s)
                AND a.Profile_dob > %s  -- viewer (male) older than candidate
            )
            OR
            (%s = 'female' 
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= %s)
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= %s)
                AND a.Profile_dob < %s  -- viewer (female) younger than candidate
            )
        )
            """

            query_params = [gender, profile_id,gender,partner_pref_age_from, partner_pref_age_from, partner_pref_age_from,partner_pref_age_to, partner_pref_age_to, partner_pref_age_to,profile_dob,gender,partner_pref_age_from, partner_pref_age_from, partner_pref_age_from, partner_pref_age_to, partner_pref_age_to, partner_pref_age_to,profile_dob ]

            # Income filter
            if min_anual_income and max_anual_income:
                base_query += " AND h.id BETWEEN %s AND %s"
                query_params.extend([min_anual_income, max_anual_income])
            elif pref_annual_income and pref_annual_income_max:
                base_query += " AND h.id BETWEEN %s AND %s"
                query_params.extend([pref_annual_income, pref_annual_income_max])

            # Education filter
            if partner_pref_education:
                base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                query_params.append(partner_pref_education)

            # Profession filter (fixed column)
            if partner_pref_profession:
                base_query += " AND FIND_IN_SET(f.profession, %s) > 0"
                query_params.append(partner_pref_profession)

            # Foreign interest
            pref_foreign = foreign_intrest or partner_pref_foreign_interest
            if pref_foreign and pref_foreign.strip().lower() in ['yes', 'no']:
                if pref_foreign.lower() == "yes":
                    base_query += " AND f.work_country != '1'"
                else:
                    base_query += " AND f.work_country = '1'"

            # Dosham filters
            # if not chev and not ragu:
            # print('partner_pref_ragukethu',partner_pref_ragukethu)
            # print('partner_pref_chevvai',partner_pref_chevvai)
            
            # print('chev',chev)
            # print('ragu',ragu)

            
            # Check suya_gothram_admin first (ID stored as string in DB)
            if my_suya_gothram_admin and str(my_suya_gothram_admin).strip() != "" and my_suya_gothram_admin != '0':

                    base_query += " AND (c.suya_gothram_admin IS NULL OR c.suya_gothram_admin = '' OR c.suya_gothram_admin != %s)"
                    query_params.append(str(my_suya_gothram_admin))
            if my_suya_gothram and str(my_suya_gothram).strip() != "":

                    base_query += " AND (c.suya_gothram IS NULL OR c.suya_gothram = '' OR c.suya_gothram != %s )"
                    query_params.append(my_suya_gothram)
            
            
            if partner_pref_ragukethu:
                if partner_pref_ragukethu.lower() == 'yes':
                    base_query += " AND (LOWER(e.calc_raguketu_dhosham) IN ('yes','true') OR e.calc_raguketu_dhosham IN ('1',1,'','NULL'))"
                elif partner_pref_ragukethu.lower() == 'no':
                    base_query += " AND (LOWER(e.calc_raguketu_dhosham) IN ('no','false') OR e.calc_raguketu_dhosham IN ('2',2,'','NULL'))"

            if partner_pref_chevvai:
                if partner_pref_chevvai.lower() == 'yes':
                    base_query += " AND (LOWER(e.calc_chevvai_dhosham) IN ('yes','true') OR e.calc_chevvai_dhosham IN ('1',1,'','NULL'))"
                elif partner_pref_chevvai.lower() == 'no':
                    base_query += " AND (LOWER(e.calc_chevvai_dhosham) IN ('no','false') OR e.calc_chevvai_dhosham IN ('2',2,'','NULL'))"

            # Height filters
            if partner_pref_height_from and partner_pref_height_to:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([partner_pref_height_from, partner_pref_height_to])
            elif partner_pref_height_from:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(partner_pref_height_to)

            # Family status filter
            # if family_status:
            #     statuses = [s.strip() for s in str(family_status).split(',') if s.strip()]
            #     if statuses:
            #         # Use IN clause for family_status values
            #         placeholders = ','.join(['%s'] * len(statuses))
            #         base_query += " AND (c.family_status IN (" + placeholders + ") OR c.family_status IS NULL OR c.family_status = '')"
            #         query_params.extend(statuses)
            if partner_pref_familysts:
                pref_statuses = [s.strip() for s in str(partner_pref_familysts).split(',') if s.strip()]
                if pref_statuses:
                    placeholders = ','.join(['%s'] * len(pref_statuses))
                    base_query += " AND (c.family_status IN (" + placeholders + ") OR c.family_status IS NULL OR c.family_status = '')"
                    query_params.extend(pref_statuses)

            # Field of study filter
            if field_of_study:
                fields = [f.strip() for f in field_of_study.split(',') if f.strip()]
                if fields:
                    placeholders = ','.join(['%s'] * len(fields))
                    base_query += f" AND f.field_ofstudy IN ({placeholders})"
                    query_params.extend(fields)

            # Degree filter
            if degree:
                degrees = [d.strip() for d in degree.split(',') if d.strip()]
                if degrees:
                    placeholders = ','.join(['%s'] * len(degrees))
                    base_query += f" AND f.degree IN ({placeholders})"
                    query_params.extend(degrees)

            # Order by
            try:
                order_by = int(order_by)
            except (ValueError, TypeError):
                order_by = None

            if order_by == 1:
                orderby_cond = " ORDER BY a.DateOfJoin ASC"
            else:
                orderby_cond = " ORDER BY a.DateOfJoin DESC"

            query = base_query + orderby_cond

            # First fetch for total count
            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                all_profile_ids = [row[0] for row in cursor.fetchall()]
                total_count = len(all_profile_ids)
                profile_with_indices = {str(i + 1): pid for i, pid in enumerate(all_profile_ids)}

            # Add pagination
            # query += " LIMIT %s OFFSET %s"
            # query_params.extend([per_page, start])


            def format_sql_for_debug(query, params):
                def escape(value):
                    if isinstance(value, str):
                        return f"'{value}'"
                    elif value is None:
                        return 'NULL'
                    else:
                        return str(value)
                try:
                    return query % tuple(map(escape, params))
                except Exception as e:
                    print("Error formatting query:", e)
                    return query

            # Usage:
            # print("MySQL Executable Query:")
            # print(format_sql_for_debug(query, query_params))


            with connection.cursor() as cursor:
                cursor.execute(query, query_params)
                rows = cursor.fetchall()
                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return results, total_count, profile_with_indices

            return [], 0, {}

        except Exception as e:
            print(f"visibility Profile Error: {str(e)}")
            return [], 0, {}

    @staticmethod
    def get_visibility_match_count(
        gender,
        profile_id
    ):
        try:
            today = date.today()

            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            profile_dob = profile.Profile_dob

            partner_pref = get_object_or_404(ProfileVisibility, profile_id=profile_id)

            # Preferences fallback
            pref_annual_income = partner_pref.visibility_anual_income
            pref_annual_income_max = partner_pref.visibility_anual_income_max
            partner_pref_education =  partner_pref.visibility_education
            partner_pref_age_from =  partner_pref.visibility_age_from
            partner_pref_age_to =  partner_pref.visibility_age_to  
            partner_pref_height_from = partner_pref.visibility_height_from
            partner_pref_height_to =  partner_pref.visibility_height_to
            partner_pref_profession =  partner_pref.visibility_profession
            partner_pref_foreign_interest = partner_pref.visibility_foreign_interest
            partner_pref_ragukethu = partner_pref.visibility_ragukethu
            partner_pref_chevvai = partner_pref.visibility_chevvai
            partner_pref_familysts = partner_pref.visibility_family_status
            field_of_study = partner_pref.visibility_field_of_study
            degree = partner_pref.degree

            my_family= get_object_or_404(ProfileFamilyDetails, profile_id=profile_id)

            my_suya_gothram=my_family.suya_gothram
            my_suya_gothram_admin=my_family.suya_gothram_admin

            # DOB range calculation
            try:
                if partner_pref_age_from and partner_pref_age_to:
                    from_age = int(partner_pref_age_from)
                    to_age = int(partner_pref_age_to)
                    if from_age > 0 and to_age > 0 and from_age <= to_age:
                        min_dob = today - relativedelta(years=to_age)
                        max_dob = today - relativedelta(years=from_age)
                    else:
                        raise ValueError("Invalid age range")
                else:
                    if gender.upper() == "MALE":
                        min_dob = profile_dob - relativedelta(years=5)
                        max_dob = profile_dob
                    elif gender.upper() == "FEMALE":
                        min_dob = profile_dob
                        max_dob = profile_dob + relativedelta(years=5)
            except (ValueError, TypeError):
                if gender.upper() == "MALE":
                    min_dob = profile_dob - relativedelta(years=5)
                    max_dob = profile_dob
                else:
                    min_dob = profile_dob
                    max_dob = profile_dob + relativedelta(years=5)

            # Base query
            base_query = """
                SELECT COUNT(DISTINCT a.ProfileId) AS match_count
                FROM logindetails a
                JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                LEFT JOIN masterbirthstar d ON d.id = e.birthstar_name 
                JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                LEFT JOIN mastereducation g ON f.highest_education = g.RowId 
                LEFT JOIN masterannualincome h ON h.id = f.anual_income
                LEFT JOIN masterprofession r ON r.RowId = f.profession
                LEFT JOIN profile_images pi ON a.ProfileId = pi.profile_id
                WHERE a.Status = 1 
                  AND a.Plan_id NOT IN (0,16)
                  AND a.gender != %s 
                  AND a.ProfileId != %s
                  AND (
            (%s = 'male' 
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= %s)
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= %s)
                AND a.Profile_dob > %s  -- viewer (male) older than candidate
            )
            OR
            (%s = 'female' 
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) >= %s)
                AND (%s IS NULL OR %s = '' OR TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) <= %s)
                AND a.Profile_dob < %s  -- viewer (female) younger than candidate
            )
        )
            """

            query_params = [gender, profile_id,gender,partner_pref_age_from, partner_pref_age_from, partner_pref_age_from,partner_pref_age_to, partner_pref_age_to, partner_pref_age_to,profile_dob,gender,partner_pref_age_from, partner_pref_age_from, partner_pref_age_from, partner_pref_age_to, partner_pref_age_to, partner_pref_age_to,profile_dob ]


            if my_suya_gothram_admin and str(my_suya_gothram_admin).strip() != "" and my_suya_gothram_admin != '0':

                    base_query += " AND (c.suya_gothram_admin IS NULL OR c.suya_gothram_admin = '' OR c.suya_gothram_admin != %s)"
                    query_params.append(str(my_suya_gothram_admin))
            if my_suya_gothram and str(my_suya_gothram).strip() != "":

                    base_query += " AND (c.suya_gothram IS NULL OR c.suya_gothram = '' OR c.suya_gothram != %s )"
                    query_params.append(my_suya_gothram)
            
            # Income filter
            if pref_annual_income and pref_annual_income_max:
                base_query += " AND h.id BETWEEN %s AND %s"
                query_params.extend([pref_annual_income, pref_annual_income_max])

            # Education filter
            if partner_pref_education:
                base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                query_params.append(partner_pref_education)

            # Profession filter (fixed column)
            if partner_pref_profession:
                base_query += " AND FIND_IN_SET(f.profession, %s) > 0"
                query_params.append(partner_pref_profession)

            # Foreign interest
            pref_foreign = partner_pref_foreign_interest
            if pref_foreign and pref_foreign.strip().lower() in ['yes', 'no']:
                if pref_foreign.lower() == "yes":
                    base_query += " AND f.work_country != '1'"
                else:
                    base_query += " AND f.work_country = '1'"

            if partner_pref_ragukethu:
                if partner_pref_ragukethu.lower() == 'yes':
                    base_query += " AND (LOWER(e.calc_raguketu_dhosham) IN ('yes','true') OR e.calc_raguketu_dhosham IN ('1',1,'','NULL'))"
                elif partner_pref_ragukethu.lower() == 'no':
                    base_query += " AND (LOWER(e.calc_raguketu_dhosham) IN ('no','false') OR e.calc_raguketu_dhosham IN ('2',2,'','NULL'))"

            if partner_pref_chevvai:
                if partner_pref_chevvai.lower() == 'yes':
                    base_query += " AND (LOWER(e.calc_chevvai_dhosham) IN ('yes','true') OR e.calc_chevvai_dhosham IN ('1',1,'','NULL'))"
                elif partner_pref_chevvai.lower() == 'no':
                    base_query += " AND (LOWER(e.calc_chevvai_dhosham) IN ('no','false') OR e.calc_chevvai_dhosham IN ('2',2,'','NULL'))"



            # Height filters
            if partner_pref_height_from and partner_pref_height_to:
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([partner_pref_height_from, partner_pref_height_to])
            elif partner_pref_height_from:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(partner_pref_height_to)


            if partner_pref_familysts:
                pref_statuses = [s.strip() for s in str(partner_pref_familysts).split(',') if s.strip()]
                if pref_statuses:
                    placeholders = ','.join(['%s'] * len(pref_statuses))
                    base_query += " AND (c.family_status IN (" + placeholders + ") OR c.family_status IS NULL OR c.family_status = '')"
                    query_params.extend(pref_statuses)

            # Field of study filter
            if field_of_study:
                fields = [f.strip() for f in field_of_study.split(',') if f.strip()]
                if fields:
                    placeholders = ','.join(['%s'] * len(fields))
                    base_query += f" AND f.field_ofstudy IN ({placeholders})"
                    query_params.extend(fields)

            # Degree filter
            if degree:
                degrees = [d.strip() for d in degree.split(',') if d.strip()]
                if degrees:
                    placeholders = ','.join(['%s'] * len(degrees))
                    base_query += f" AND f.degree IN ({placeholders})"
                    query_params.extend(degrees)



            
            # def format_sql_for_debug(query, params):
            #     def escape(value):
            #         if isinstance(value, str):
            #             return f"'{value}'"
            #         elif value is None:
            #             return 'NULL'
            #         else:
            #             return str(value)
            #     try:
            #         return query % tuple(map(escape, params))
            #     except Exception as e:
            #         print("Error formatting query:", e)
            #         return query

            # # Usage:
            # print("MySQL Executable Query:")
            # print(format_sql_for_debug(base_query, query_params))

            with connection.cursor() as cursor:
                cursor.execute(base_query,query_params)
                count_row = cursor.fetchone()
                return count_row[0] if count_row else 0

        except Exception as e:
            print("[ERROR] get_visibilitymatchcount:", e)
            return 0
    
    
    
    
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



    @staticmethod
    def get_common_profile_list(start, per_page, 
                                search_profile_id=None, order_by=None,chevvai_dosham=None, ragu_dosham=None,
                                search_profession=None, age_from=None,age_to=None, search_location=None,
                                complexion=None, city=None, state=None, education=None,
                                foreign_intrest=None, has_photos=None, height_from=None, height_to=None,
                                matching_stars=None, min_anual_income=None, max_anual_income=None,
                                membership=None,profile_name=None,father_alive=None,mother_alive=None,martial_status=None,
                                mobile_no=None, profile_dob=None,status=None,dob_date=None,dob_month=None,dob_year=None,family_status=None,
                                email_id=None,gender=None,father_name=None,father_occupation=None,mother_name=None,mother_occupation=None,
                                business_name=None,company_name=None,from_last_action_date=None,to_last_action_date=None,from_doj=None,to_doj=None,created_by=None,
                                delete_status=None,address=None,admin_comments=None,marriage_from=None,marriage_to=None,
                                engagement_from=None,engagement_to=None,field_of_study=None,degree=None
                                ):

        try:
            base_query = """
                SELECT DISTINCT a.ProfileId, a.Gender, a.Photo_protection, a.Profile_city, a.Profile_verified,
                    a.Profile_name, a.Profile_dob, a.Profile_height,
                    e.birthstar_name, e.birth_rasi_name,
                    f.degree,f.other_degree, f.profession, g.EducationLevel, 
                    h.income, (SELECT image FROM profile_images WHERE profile_id = a.ProfileId LIMIT 1) as image
                FROM logindetails a
                LEFT JOIN profile_horoscope e ON a.ProfileId = e.profile_id
                LEFT JOIN profile_familydetails c ON a.ProfileId = c.profile_id
                LEFT JOIN profile_edudetails f ON a.ProfileId = f.profile_id
                LEFT JOIN mastereducation g ON f.highest_education = g.RowId
                LEFT JOIN masterannualincome h ON f.anual_income = h.id
                LEFT JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                LEFT JOIN profile_images i ON i.profile_id=a.ProfileId
                LEFT JOIN marriage_settled j ON a.ProfileId = j.profile_id
                WHERE 1 
            """

            query_params = []

            
            if field_of_study:
                base_query += " AND f.field_ofstudy = %s"
                query_params.append(field_of_study)

            if degree:
                base_query += " AND f.degree = %s"
                query_params.append(degree)

            if engagement_from and engagement_to:
                try:
                    ef = datetime.strptime(engagement_from, '%Y-%m-%d').date()
                    et = datetime.strptime(engagement_to, '%Y-%m-%d').date()
                    base_query += " AND j.engagement_date BETWEEN %s AND %s"
                    query_params.extend([ef, et])
                except Exception:
                    pass
            elif engagement_from:  
                try:
                    ef = datetime.strptime(engagement_from, '%Y-%m-%d').date()
                    base_query += " AND j.engagement_date >= %s"
                    query_params.append(ef)
                except Exception:
                    pass
            elif engagement_to:
                try:
                    et = datetime.strptime(engagement_to, '%Y-%m-%d').date()
                    base_query += " AND j.engagement_date <= %s"
                    query_params.append(et)
                except Exception:
                    pass
            
            if marriage_from and marriage_to:
                try:
                    mf = datetime.strptime(marriage_from, '%Y-%m-%d').date()
                    mt = datetime.strptime(marriage_to, '%Y-%m-%d').date()
                    base_query += " AND j.marriage_date BETWEEN %s AND %s"
                    query_params.extend([mf, mt])
                except Exception:
                    pass
            elif marriage_from:
                try:
                    mf = datetime.strptime(marriage_from, '%Y-%m-%d').date()
                    base_query += " AND j.marriage_date >= %s"
                    query_params.append(mf)
                except Exception:
                    pass
            elif marriage_to:
                try:
                    mt = datetime.strptime(marriage_to, '%Y-%m-%d').date()
                    base_query += " AND j.marriage_date <= %s"
                    query_params.append(mt)
                except Exception:
                    pass
            
            if admin_comments:
                base_query += " AND lower(a.Admin_comments) LIKE %s"
                query_params.append(f"%{admin_comments.lower()}%")
            
            if address:
                base_query += " AND lower(a.Profile_address) LIKE %s"
                query_params.append(f"%{address.lower()}%")
            
            if delete_status:
                delete_status_list = [s.strip() for s in delete_status.split(',') if s.strip()]

                if len(delete_status_list) == 1:
                    base_query += " AND a.secondary_status = %s"
                    query_params.append(delete_status_list[0])
                elif len(delete_status_list) > 1:
                    placeholders = ','.join(['%s'] * len(delete_status_list))
                    base_query += f" AND a.secondary_status IN ({placeholders})"
                    query_params.extend(delete_status_list)
            
            if created_by:
                base_query += " AND a.Profile_for = %s"
                query_params.append(created_by)
            
            if from_doj and to_doj:
                try:
                    fd = datetime.strptime(from_doj, '%Y-%m-%d').date()
                    td = datetime.strptime(to_doj, '%Y-%m-%d').date()
                    base_query += " AND a.DateOfJoin BETWEEN %s AND %s"
                    query_params.extend([fd, td])
                except Exception:
                    pass
            elif from_doj:
                try:
                    fd = datetime.strptime(from_doj, '%Y-%m-%d').date()
                    base_query += " AND a.DateOfJoin >= %s"
                    query_params.append(fd)
                except Exception:
                    pass
            elif to_doj:
                try:
                    td = datetime.strptime(to_doj, '%Y-%m-%d').date()
                    base_query += " AND a.DateOfJoin <= %s"
                    query_params.append(td)
                except Exception:
                    pass
            
            if from_last_action_date and to_last_action_date:
                try:
                    lad = datetime.strptime(from_last_action_date, '%Y-%m-%d').date()
                    tad = datetime.strptime(to_last_action_date, '%Y-%m-%d').date()
                    base_query += " AND a.Last_login_date BETWEEN %s AND %s"
                    query_params.extend([lad, tad])
                except Exception:
                    pass
            elif from_last_action_date:
                try:
                    lad = datetime.strptime(from_last_action_date, '%Y-%m-%d').date()
                    base_query += " AND a.Last_login_date >= %s"
                    query_params.append(lad)
                except Exception:
                    pass
            elif to_last_action_date:
                try:
                    tad = datetime.strptime(to_last_action_date, '%Y-%m-%d').date()
                    base_query += " AND a.Last_login_date <= %s"
                    query_params.append(tad)
                except Exception:
                    pass
                
            if business_name:
                base_query += " AND lower(f.business_name) LIKE %s"
                query_params.append(f"%{business_name.lower()}%")
                
            if company_name:
                base_query += " AND lower(f.company_name) LIKE %s"
                query_params.append(f"%{company_name.lower()}%")
            
            if father_name:
                base_query += " AND lower(c.father_name) LIKE %s"
                query_params.append(f"%{father_name.lower()}%")
                
            if father_occupation:
                base_query += " AND lower(c.father_occupation) LIKE %s"
                query_params.append(f"%{father_occupation.lower()}%")
                
            if mother_name:
                base_query += " AND lower(c.mother_name) LIKE %s"
                query_params.append(f"%{mother_name.lower()}%")
                
            if mother_occupation:
                base_query += " AND lower(c.mother_occupation) LIKE %s"
                query_params.append(f"%{mother_occupation.lower()}%")
            
            if email_id:
                base_query += " AND a.EmailId LIKE %s"
                query_params.append(f"%{email_id}%")

            if gender:
                gender_list = [g.strip().lower() for g in gender.split(',') if g.strip()]
                
                if len(gender_list) == 1:
                    base_query += " AND lower(a.Gender) = %s"
                    query_params.append(gender_list[0])
                else:
                    placeholders = ','.join(['%s'] * len(gender_list))
                    base_query += f" AND lower(a.Gender) IN ({placeholders})"
                    query_params.extend(gender_list)

            if family_status and family_status != "0":
                family_status_list = [c.strip() for c in family_status.split(',') if c.strip()]
                placeholders = ', '.join(['%s'] * len(family_status_list))
                base_query += f" AND c.family_status IN ({placeholders})"
                query_params.extend(family_status_list)

            if dob_year:
                try:
                    dob_year = int(dob_year)
                    base_query += " AND EXTRACT(YEAR FROM a.Profile_dob) = %s"
                    query_params.append(dob_year)
                except ValueError:
                    pass

            if dob_month:
                try:
                    dob_month = int(dob_month)
                    base_query += " AND EXTRACT(MONTH FROM a.Profile_dob) = %s"
                    query_params.append(dob_month)
                except ValueError:
                    pass

            if dob_date:
                try:
                    dob_date = int(dob_date)
                    base_query += " AND EXTRACT(DAY FROM a.Profile_dob) = %s"
                    query_params.append(dob_date)
                except ValueError:
                    pass

            if status is not None and status != '':
                status_list = []
                for s in status.split(','):
                    s = s.strip()
                    if s.isdigit():
                        status_list.append(int(s))

                if len(status_list) == 1:
                    base_query += " AND a.Status = %s"
                    query_params.append(status_list[0])

                elif len(status_list) > 1:
                    placeholders = ','.join(['%s'] * len(status_list))
                    base_query += f" AND a.Status IN ({placeholders})"
                    query_params.extend(status_list)
        
            # profile_id and name search
            if search_profile_id:
                base_query += " AND (a.ProfileId = %s OR a.Profile_name LIKE %s)"
                query_params.append(search_profile_id)
                query_params.append(f"%{search_profile_id}%")

            # Profession filter (multiple IDs support)
            if search_profession:
                try:
                    profession_ids = tuple(map(int, search_profession.split(',')))
                    if profession_ids:
                        base_query += " AND f.profession IN %s"
                        query_params.append(profession_ids)
                except:
                    pass

            # Age filter
            today = date.today()

            if 'age_from' in locals() or 'age_to' in locals():
                if age_from and age_to:
                    age_from = int(age_from)  # Cast string to int
                    age_to = int(age_to)
                    dob_from = today - timedelta(days=(age_to * 365.25))  # older date
                    dob_to = today - timedelta(days=(age_from * 365.25))  # newer date
                    base_query += " AND a.Profile_dob BETWEEN %s AND %s"
                    query_params.extend([dob_from, dob_to])
                elif age_from:
                    age_from = int(age_from)
                    dob_to = today - timedelta(days=(age_from * 365.25))
                    base_query += " AND a.Profile_dob <= %s"
                    query_params.append(dob_to)
                elif age_to:
                    age_to = int(age_to)
                    dob_from = today - timedelta(days=(age_to * 365.25))
                    base_query += " AND a.Profile_dob >= %s"
                    query_params.append(dob_from)

            # Location filter (if separate from state)
            if search_location:
                base_query += " AND a.Profile_state = %s"
                query_params.append(search_location)

            # Complexion
            if complexion and complexion != "0":
                complexion_list = [c.strip() for c in complexion.split(',') if c.strip()]
                placeholders = ', '.join(['%s'] * len(complexion_list))
                base_query += f" AND a.Profile_complexion IN ({placeholders})"
                query_params.extend(complexion_list)

            if martial_status and martial_status != "0":
                martial_status_list = [c.strip() for c in martial_status.split(',') if c.strip()]
                placeholders = ', '.join(['%s'] * len(martial_status_list))
                base_query += f" AND a.Profile_marital_status IN ({placeholders})"
                query_params.extend(martial_status_list)
            if profile_name:
                base_query += " AND a.Profile_name LIKE %s"
                query_params.append(f"%{profile_name}%")
            
            # City
            if city and city != "":
                base_query += "AND LOWER(TRIM(a.Profile_city)) LIKE LOWER(%s)"
                query_params.append(f"%{city}%")

            # State
            if state and state != "0":
                state_list = [s.strip() for s in state.split(',') if s.strip()]
                
                if len(state_list) == 1:
                    base_query += " AND a.Profile_state = %s"
                    query_params.append(state_list[0])
                else:
                    placeholders = ','.join(['%s'] * len(state_list))
                    base_query += f" AND a.Profile_state IN ({placeholders})"
                    query_params.extend(state_list)


            # Education (multi IDs)
            if education:
                try:
                    education_ids = tuple(map(int, education.split(',')))
                    if education_ids:
                        base_query += " AND g.RowId IN %s"
                        query_params.append(education_ids)
                except:
                    pass

            # Matching stars (as comma-separated star-rasi strings)
            if matching_stars:
                matching_stars = matching_stars.strip()
                if matching_stars and matching_stars != "0":
                    try:
                        star_ids = tuple(map(int, matching_stars.split(',')))
                        if star_ids:
                            base_query += " AND e.birthstar_name IN %s"
                            query_params.append(star_ids)
                    except ValueError:
                        pass

            if foreign_intrest:
                foreign_intrest_val = foreign_intrest.strip().lower()

                if foreign_intrest_val == "yes":
                    base_query += """
                        AND (
                            a.Profile_country != 1 
                            OR (f.work_country != 1 AND f.work_country IS NOT NULL AND f.work_country != 0)
                        )
                    """
                elif foreign_intrest_val == "no":
                    base_query += """
                        AND (a.Profile_country = 1 AND (f.work_country = 1 OR f.work_country IS NULL))
                    """

            # Has photos
            if has_photos and has_photos.lower() == "yes":
                base_query += " AND i.image IS NOT NULL"

            # Membership plan filter
            if membership:
                memberships = [m.strip() for m in membership.split(",") if m.strip()]
                placeholders = ", ".join(["%s"] * len(memberships))
                base_query += f" AND a.Plan_id IN ({placeholders})"
                query_params.extend(memberships)
            
            conditions = []

            if chevvai_dosham and chevvai_dosham.lower() == 'yes':
                conditions.append("""
                    (
                        LOWER(e.calc_chevvai_dhosham) IN ('yes', 'true')
                        OR e.calc_chevvai_dhosham IN ('1', 1)
                        OR e.calc_chevvai_dhosham IS NULL
                    )
                """)

            if ragu_dosham and ragu_dosham.lower() == 'yes':
                conditions.append("""
                    (
                        LOWER(e.calc_raguketu_dhosham) IN ('yes', 'true')
                        OR e.calc_raguketu_dhosham IN ('1', 1)
                        OR e.calc_raguketu_dhosham IS NULL
                    )
                """)

            if conditions:
                base_query += f"\nAND ({' OR '.join(conditions)})"

            if min_anual_income and max_anual_income:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT income_amount 
                            FROM masterannualincome 
                            WHERE id IN (%s, %s)
                            ORDER BY id
                        """, [min_anual_income, max_anual_income])
                        income_rows = cursor.fetchall()

                        amounts = [row[0] for row in income_rows if row[0] is not None]

                        if len(amounts) >= 2:
                            income_min = min(amounts)
                            income_max = max(amounts)
                            base_query += " AND h.income_amount BETWEEN %s AND %s"
                            query_params.extend([income_min, income_max])
                        elif len(amounts) == 1:
                            base_query += " AND h.income_amount >= %s"
                            query_params.append(amounts[0])
                except Exception as e:
                    print("[Income Filter Error]", str(e))

            if height_from and height_to:
                if height_from > height_to:
                    height_from, height_to = height_to, height_from
                base_query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([height_from, height_to])
            elif height_from:
                base_query += " AND a.Profile_height >= %s"
                query_params.append(height_from)
            elif height_to:
                base_query += " AND a.Profile_height <= %s"
                query_params.append(height_to)

            if father_alive and father_alive.strip().lower() in ['yes', 'no']:
                base_query += " AND c.father_alive = %s"
                query_params.append(father_alive.strip().lower())

            if mother_alive and mother_alive.strip().lower() in ['yes', 'no']:
                base_query += " AND c.mother_alive = %s"
                query_params.append(mother_alive.strip().lower())
            
            if mobile_no:
                    cleaned_mobile = ''.join(filter(str.isdigit, mobile_no))
                    
                    if cleaned_mobile:
                        base_query += """
                            AND (a.Mobile_no LIKE %s 
                                OR a.Profile_alternate_mobile LIKE %s 
                                OR a.Profile_mobile_no LIKE %s
                                OR a.Profile_whatsapp LIKE %s
                                )
                        """
                        like_pattern = f'%{cleaned_mobile}%'
                        query_params.extend([like_pattern, like_pattern, like_pattern, like_pattern]) 

            if profile_dob:
                try:
                    dob = datetime.strptime(profile_dob, '%Y-%m-%d').date()
                    base_query += " AND YEAR(a.Profile_dob) = %s AND MONTH(a.Profile_dob) = %s AND DAY(a.Profile_dob) = %s"
                    query_params.append(dob.year)
                    query_params.append(dob.month)
                    query_params.append(dob.day)
                except Exception:
                    pass
            
            # Order by clause
            if order_by:
                try:
                    order_by = int(order_by)
                    if order_by == 1:
                        base_query += " ORDER BY a.DateOfJoin ASC"
                    elif order_by == 2:
                        base_query += " ORDER BY a.DateOfJoin DESC"
                except:
                    pass

       

            # print("MySQL Executable Query:", format_sql_for_debug_new(base_query, query_params))

            # Count total
            count_query = f"""SELECT COUNT(*) FROM ({base_query}) AS total"""
            with connection.cursor() as cursor:
                cursor.execute(count_query, query_params)
                total_count = cursor.fetchone()[0]

            # Limit and offset
            base_query += " LIMIT %s OFFSET %s"
            query_params.extend([per_page, start])

            # Execute final query
            with connection.cursor() as cursor:
                cursor.execute(base_query, query_params)
                rows = cursor.fetchall()
                columns = [col[0] for col in cursor.description]
                results = [dict(zip(columns, row)) for row in rows]

                all_profile_ids = [row["ProfileId"] for row in results]
                profile_with_indices = {str(i + 1): pid for i, pid in enumerate(all_profile_ids)}

                return results, total_count, profile_with_indices

        except Exception as ex:
            print(f"[get_common_profile_list] ERROR: {str(ex)}")
            return [], 0, {}




def format_sql_for_debug_new(query, params):
                def escape(value):
                    if isinstance(value, str):
                        return f"'{value}'"
                    elif value is None:
                        return 'NULL'
                    else:
                        return str(value)
                try:
                    return query % tuple(map(escape, params))
                except Exception as e:
                    print("Error formatting query:", e)
                    return query

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
    
    @staticmethod
    def get_matching_stars_pdf(birth_rasi_id, birth_star_id, gender):
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
                LEFT JOIN masterbirthstar sd ON sd.id = sp.dest_star_id 
                LEFT JOIN masterrasi rd ON rd.id = sp.dest_rasi_id
                LEFT JOIN matching_porutham_names pn ON FIND_IN_SET(pn.id, sp.matching_porutham) 
            WHERE 
                sp.gender = %s 
                AND sp.source_star_id = %s 
                AND sp.source_rasi_id = %s 
            GROUP BY 
                sp.id, sp.gender, sp.source_star_id, 
                sp.matching_porutham, sp.dest_rasi_id, 
                sp.dest_star_id, sp.match_count, 
                sd.star, rd.name
            '''

        with connection.cursor() as cursor:
            cursor.execute(query, [gender, birth_star_id , birth_rasi_id])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        
        # Group the results by Porutham count
        grouped_data = defaultdict(list)
        for item in result:
            match_count = item['match_count']
            grouped_data[match_count].append(item)

        # Separate by Porutham counts 9, 8, 7, 6, 5
        porutham_data = {
            "9 Poruthams": grouped_data.get(9, []),
            "8 Poruthams": grouped_data.get(8, []),
            "7 Poruthams": grouped_data.get(7, []),
            "6 Poruthams": grouped_data.get(6, []),
            "5 Poruthams": grouped_data.get(5, [])
        }
        
        return porutham_data



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
    pref_anual_income_max = models.CharField(max_length=50,null=True, blank=True)
    pref_chevvai = models.CharField(max_length=20)  # Changed from CharField to TextField
    pref_ragukethu = models.CharField(max_length=20)
    pref_foreign_intrest = models.CharField(max_length=20)
    pref_family_status = models.CharField(max_length=100,null=True, blank=True)
    pref_state = models.CharField(max_length=100,null=True, blank=True)
    pref_porutham_star = models.TextField(max_length=200)
    pref_porutham_star_rasi = models.TextField(max_length=200 , null=True, blank=True)
    status = models.IntegerField()   # Changed from CharField to TextField
    degree = models.CharField(max_length=255, blank=True, null=True) 
    pref_fieldof_study = models.CharField(max_length=255, blank=True, null=True)
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


class SentFullProfileEmailLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Change from IntegerField to CharField
    to_ids = models.CharField(max_length=255)
    profile_owner = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    sent_datetime = models.DateTimeField()
    class Meta:
        managed = False  # Django won't create or modify this table
        db_table = 'sent_profile_email_log'  # Name of the existing table in your database

    def __str__(self):
        return f"Email Log {self.id} - Profile {self.profile_id} to {self.to_ids}"


class SentShortProfileEmailLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField()  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'sent_short_profile_email_log'  # Database table name

    def __str__(self):
        return f"Short Profile Email Log {self.id} - Profile {self.profile_id} to {self.to_ids}"



class SentFullProfilePrintPDFLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField(default=datetime.now)  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'sent_full_profile_print_pdf_log'  # Database table name

    def __str__(self):
        return f"Full Profile Print PDF Log {self.id} - Profile {self.profile_id} to {self.to_ids}"
    

class SentShortProfilePrintPDFLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField(default=datetime.now)  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'sent_short_profile_print_pdf_log'  # Database table name

    def __str__(self):
        return f"Short Profile Print PDF Log {self.id} - Profile {self.profile_id} to {self.to_ids}"


class SentFullProfilePrintwpLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField(default=datetime.now)  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'matching_whatsapp_full_profile_log'  # Database table name

    def __str__(self):
        return f"Full Profile Print PDF Log {self.id} - Profile {self.profile_id} to {self.to_ids}"
    
class SentShortProfilePrintwpLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField(default=datetime.now)  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'matching_whatsapp_short_profile_log'  # Database table name

    def __str__(self):
        return f"Short Profile Print PDF Log {self.id} - Profile {self.profile_id} to {self.to_ids}"



class CallType(models.Model):
    id = models.AutoField(primary_key=True)
    call_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'calltypes'  # Database table name

    def __str__(self):
        return self.call_type

class CallStatus(models.Model):
    id = models.AutoField(primary_key=True)
    call_status = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  # This table already exists in the DB
        db_table = 'callstatus'  # Database table name

    def __str__(self):
        return self.call_status
    
class CallAction(models.Model):
    id = models.AutoField(primary_key=True)
    call_action_name = models.CharField(max_length=255)
    status = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  # This table already exists in the DB
        db_table = 'callactions'  # Database table name

    def __str__(self):
        return self.call_action_name

class ProfileCallManagement(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)
    profile_status_id = models.IntegerField()
    owner_id = models.IntegerField()

    inoutbound_id = models.IntegerField(null=True, blank=True)
    call_type_id = models.IntegerField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    call_status_id = models.IntegerField(null=True, blank=True)
    next_calldate = models.DateTimeField(null=True, blank=True)
    callaction_today_id = models.IntegerField(null=True, blank=True)
    future_actiontaken_id = models.IntegerField(null=True, blank=True)
    next_dateaction_point = models.DateTimeField(null=True, blank=True)
    work_asignid = models.IntegerField(null=True, blank=True)
    updated_by = models.CharField(max_length=255 , null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        managed = False  # This table already exists in the DB
        db_table = 'profile_call_management'  # Database table name

    def __str__(self):
        return f"ProfileCallManagement {self.id}"

class MarriageSettleDetails(models.Model):
    profile_id = models.CharField(max_length=255,primary_key=True)
    owner_id = models.IntegerField()

    marriage_date = models.DateField(null=True, blank=True)
    groombridefathername = models.CharField(max_length=255, null=True, blank=True)
    groom_bride_vysyamala_id = models.CharField(max_length=255, null=True, blank=True)
    engagement_date = models.DateField(null=True, blank=True)
    marriage_photo_details = models.TextField(null=True, blank=True)
    engagement_photo_details = models.TextField(null=True, blank=True)
    admin_marriage_comments = models.TextField(null=True, blank=True)
    groom_bride_name = models.CharField(max_length=255, null=True, blank=True)
    groombridecity = models.CharField(max_length=255, null=True, blank=True)
    settled_thru= models.CharField(max_length=255, null=True, blank=True)
    marriage_comments = models.TextField(null=True, blank=True)
    marriage_invitation_details = models.TextField(null=True, blank=True)
    engagement_invitation_details = models.TextField(null=True, blank=True)
    admin_settled_thru = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    others = models.CharField(max_length=255, null=True, blank=True)
    admin_others = models.TextField(max_length=255, null=True, blank=True)
    marriage_location = models.CharField(max_length=255, null=True, blank=True)
    wish_card_accept = models.CharField(max_length=255, null=True, blank=True)
    instagram_accept = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  # This table already exists in the DB
        db_table = 'marriage_settled'  # Database table name

class PaymentTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)
    plan_id = models.IntegerField(null=True, blank=True)
    order_id = models.CharField(max_length=255,null=True, blank=True)
    payment_id = models.CharField(max_length=255,null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    status = models.CharField(max_length=50)  # 1: pending, 2: paid, 3: failed
    created_at = models.DateTimeField()

    payment_type = models.CharField(max_length=100,null=True, blank=True)
    discount_amont = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_refno = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    owner_id = models.IntegerField(null=True, blank=True)
    addon_package=models.CharField(max_length=255, null=True, blank=True)
    admin_status=models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False  # Table already exists in DB
        db_table = 'payment_transaction'

    def __str__(self):
        return f"PaymentTransaction {self.id}"

class Invoice(models.Model):
    customer_name = models.CharField(max_length=100)
    address = models.TextField()
    invoice_number = models.CharField(max_length=20)
    vysyamala_id = models.CharField(max_length=20)
    service_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    valid_till = models.DateField()
    date = models.DateField()


class ProfileVisibility(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    visibility_age_from = models.CharField(max_length=50)
    visibility_age_to = models.CharField(max_length=50)
    visibility_height_from = models.CharField(max_length=50)
    visibility_height_to = models.CharField(max_length=50)
    visibility_profession = models.CharField(max_length=50,null=True, blank=True)  
    visibility_education = models.CharField(max_length=50,null=True, blank=True)
    visibility_anual_income = models.CharField(max_length=255,null=True, blank=True)
    visibility_family_status = models.CharField(max_length=50,null=True, blank=True)
    visibility_chevvai = models.CharField(max_length=20)  
    visibility_ragukethu = models.CharField(max_length=20)
    visibility_foreign_interest = models.CharField(max_length=20)
    visibility_anual_income_max = models.CharField(max_length=255,null=True, blank=True)
    status = models.IntegerField()  
    degree = models.CharField(max_length=255, blank=True, null=True) 
    visibility_field_of_study = models.CharField(max_length=255, blank=True, null=True) 
    
    class Meta:
        managed = False  
        db_table = 'profile_visibility'  

    def __str__(self):
        return self.id

class Profilefieldstudy(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    field_of_study = models.CharField(max_length=100)
    is_active = models.SmallIntegerField()
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterfieldofstudy'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class AdminPrintLogs(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)
    sentprofile_id = models.CharField(max_length=50)
    action_type = models.CharField(max_length=20)
    format_type = models.CharField(max_length=20)
    sent_date =  models.DateTimeField()
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField()
    class Meta:
        managed = False  
        db_table = 'admin_sentprofiles'
        
class DataHistory(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)
    owner_id = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(default=timezone.now)
    profile_status = models.IntegerField(default=0)
    plan_id = models.IntegerField(blank=True, null=True)
    others =  models.CharField(max_length=255,blank=True, null=True)
    pending_others = models.CharField(max_length=255,blank=True, null=True)
    hide_others = models.CharField(max_length=255,blank=True, null=True)
    delete_others = models.CharField(max_length=255,blank=True, null=True)
    
    class Meta:
        managed = False  
        db_table = 'datahistory'
    



class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email= models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    role = models.ForeignKey('Roles', on_delete=models.SET_NULL,null=True, blank=True)
    # state = models.CharField(max_length=255,null=True, blank=True)
    state = models.TextField(null=True,blank=True)
    status = models.IntegerField(default=1)
    is_deleted = models.IntegerField(default=0)
    
    USERNAME_FIELD = 'username'
    objects = UserManager()

    class Meta:
        db_table = 'users'
        managed = False

    def __str__(self):
        return self.username


# =========================
#  ROLE MODEL
# =========================
# models.py

class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        managed = False  # ✅ Since table already exists


class Action(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    # created_at = models.DateTimeField()

    class Meta:
        db_table = 'actions'
        managed = False


class RolePermission(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(Roles, related_name='permissions', on_delete=models.CASCADE, db_column='role_id')
    action = models.ForeignKey(Action, on_delete=models.CASCADE, db_column='action_id')
    value = models.PositiveSmallIntegerField(default=0)
    # updated_at = models.DateTimeField()

    class Meta:
        db_table = 'rolepermissions'
        managed = False
        unique_together = ('role', 'action')


#Call management New Code starts here
# -----------------------------
# MASTER TABLES
# -----------------------------

class CallTypeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    call_type = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'master_call_type'


class ParticularsMaster(models.Model):
    id = models.AutoField(primary_key=True)
    particulars = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'master_particulars'


class CallStatusMaster(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'master_call_status'


class ActionPointMaster(models.Model):
    id = models.AutoField(primary_key=True)
    action_point = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'master_action_point'


# -----------------------------
# PARENT TABLE
# -----------------------------

class CallManagement(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'call_management'


# -----------------------------
# LOG TABLES
# -----------------------------

class CallLog(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(CallManagement, on_delete=models.CASCADE)

    call_date = models.DateTimeField(null=True, blank=True)
    call_type = models.ForeignKey(CallTypeMaster, on_delete=models.SET_NULL, null=True)
    particulars = models.ForeignKey(ParticularsMaster, on_delete=models.SET_NULL, null=True)
    call_status = models.ForeignKey(CallStatusMaster, on_delete=models.SET_NULL, null=True)
    next_call_date= models.DateField(null=True, blank=True)
    call_owner=models.CharField(max_length=25)
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'call_logs'

    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["call_date", "next_call_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)


class ActionLog(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(
        CallManagement,
        on_delete=models.CASCADE,
        db_column='call_management_id'
    )

    action_date = models.DateTimeField(null=True, blank=True)

    action_point = models.ForeignKey(
        ActionPointMaster,
        null=True,
        on_delete=models.SET_NULL,
        db_column='action_point_id',
        related_name='action_point_logs'
    )

    next_action = models.ForeignKey(
        ActionPointMaster,
        null=True,
        on_delete=models.SET_NULL,
        db_column='next_action_id',
        related_name='next_action_logs'
    )

    comments = models.TextField(null=True)
    next_action_date = models.DateField(null=True, blank=True)
    action_owner=models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'action_logs'
    
    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["action_date", "next_action_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)

class AssignLog(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(
        CallManagement,
        on_delete=models.CASCADE,
        db_column='call_management_id'
    )

    assigned_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.IntegerField(null=True)
    assigned_by = models.IntegerField(null=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'assign_logs'

    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["assigned_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)





# -----------------------------
# LOG TABLES
# -----------------------------

class CallLog_New(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(CallManagement, on_delete=models.CASCADE)

    call_date = models.DateField(null=True, blank=True)
    call_type = models.ForeignKey(CallTypeMaster, on_delete=models.SET_NULL, null=True)
    particulars = models.ForeignKey(ParticularsMaster, on_delete=models.SET_NULL, null=True)
    call_status = models.ForeignKey(CallStatusMaster, on_delete=models.SET_NULL, null=True)
    next_call_date= models.DateField(null=True, blank=True)
    call_owner=models.CharField(max_length=25)
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'call_logs'

    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["call_date", "next_call_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)


class ActionLog_New(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(
        CallManagement,
        on_delete=models.CASCADE,
        db_column='call_management_id'
    )

    action_date = models.DateField(null=True, blank=True)

    action_point = models.ForeignKey(
        ActionPointMaster,
        null=True,
        on_delete=models.SET_NULL,
        db_column='action_point_id',
        related_name='action_point_logs'
    )

    next_action = models.ForeignKey(
        ActionPointMaster,
        null=True,
        on_delete=models.SET_NULL,
        db_column='next_action_id',
        related_name='next_action_logs'
    )

    comments = models.TextField(null=True)
    next_action_date = models.DateField(null=True, blank=True)
    action_owner=models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'action_logs'
    
    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["action_date", "next_action_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)

class AssignLog_New(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(
        CallManagement,
        on_delete=models.CASCADE,
        db_column='call_management_id'
    )

    assigned_date = models.DateField(null=True, blank=True)
    assigned_to = models.IntegerField(null=True)
    assigned_by = models.IntegerField(null=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'assign_logs'

    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["assigned_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)




# -----------------------------
# New Call Management TABLES
# -----------------------------


class CallManagement_New(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50,null=True, blank=True)
    mobile_no = models.CharField(max_length=50,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'call_management_new'


# -----------------------------
# LOG TABLES
# -----------------------------

class CallLog_New(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(CallManagement_New, on_delete=models.CASCADE)

    call_date = models.DateTimeField(null=True, blank=True)
    call_type = models.ForeignKey(CallTypeMaster, on_delete=models.SET_NULL, null=True)
    particulars = models.ForeignKey(ParticularsMaster, on_delete=models.SET_NULL, null=True)
    call_status = models.ForeignKey(CallStatusMaster, on_delete=models.SET_NULL, null=True)
    next_call_date= models.DateField(null=True, blank=True)
    call_owner=models.CharField(max_length=25)
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'call_logs_new'

    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["call_date", "next_call_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)


class ActionLog_New(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(
        CallManagement_New,
        on_delete=models.CASCADE,
        db_column='call_management_id'
    )

    action_date = models.DateTimeField(null=True, blank=True)

    action_point = models.ForeignKey(
        ActionPointMaster,
        null=True,
        on_delete=models.SET_NULL,
        db_column='action_point_id',
        related_name='action_point_logs_new'
    )

    next_action = models.ForeignKey(
        ActionPointMaster,
        null=True,
        on_delete=models.SET_NULL,
        db_column='next_action_id',
        related_name='next_action_logs_new'
    )

    comments = models.TextField(null=True)
    next_action_date = models.DateField(null=True, blank=True)
    action_owner=models.CharField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'action_logs_new'
    
    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["action_date", "next_action_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)

class AssignLog_New(models.Model):
    id = models.AutoField(primary_key=True)

    call_management = models.ForeignKey(
        CallManagement_New,
        on_delete=models.CASCADE,
        db_column='call_management_id'
    )

    assigned_date = models.DateTimeField(null=True, blank=True)
    assigned_to = models.IntegerField(null=True)
    assigned_by = models.IntegerField(null=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.IntegerField(default=0)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = False
        db_table = 'assign_logs_new'

    def save(self, *args, **kwargs):
        # Clean empty strings before saving
        for field in ["assigned_date"]:
            if getattr(self, field) == "":
                setattr(self, field, None)

        super().save(*args, **kwargs)


class StateRoundRobin(models.Model):
    id = models.AutoField(primary_key=True)
    
    # IMPORTANT: use state_id, not name
    state_id = models.IntegerField(unique=True)
    
    last_assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "state_round_robin"
        managed = False  # Set to True only if Django should manage the table