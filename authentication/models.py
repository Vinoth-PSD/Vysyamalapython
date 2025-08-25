from django.db import models, connection
from django.http import JsonResponse
from rest_framework.views import status
from django.shortcuts import get_object_or_404
import os
from django.utils import timezone
from datetime import datetime
from ckeditor.fields import RichTextField
from django.conf import settings
from .storages import AzureMediaStorage
from collections import defaultdict

class AuthUser(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Note: storing passwords as plain text is insecure

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'auth_user'  # Name of the table in your database

    def __str__(self):
        return self.username

class Basic_Registration(models.Model):
    ContentId  = models.AutoField(primary_key=True)
    Profile_name = models.CharField(max_length=255, blank=True, null=True)
    ProfileId = models.CharField(max_length=50)
    LoginId = models.CharField(max_length=50)
    Profile_for = models.CharField(max_length=50)
    Gender = models.TextField(max_length=100)  # Changed from CharField to TextField
    Mobile_no = models.CharField(max_length=50, blank=True, null=True)
    EmailId = models.CharField(max_length=100, blank=True, null=True)
    Password = models.CharField(max_length=20)  # Changed from CharField to TextField
    Otp = models.CharField(max_length=10)
    Stage = models.SmallIntegerField()
    AdminPermission = models.SmallIntegerField()  # Changed from CharField to TextField
    Payment = models.CharField(max_length=10)  # Changed from CharField to TextField
    PaymentExpire = models.DateTimeField(max_length=15)  # Changed from CharField to TextField
    PaymentType = models.CharField(max_length=255)  # Changed from CharField to TextField
    Status = models.IntegerField()

    
    
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'logindetails_temp'  # Name of the table in your database

    def __str__(self):
        return self.ProfileId


def upload_to_profile_basic(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.ProfileId), filename)
    return f"profile_idproof/IDProof/{filename}"
 
def upload_to_profile_horoscope(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.ProfileId), filename)
    return f"profile_horoscope_original/HoroscopeOriginal/{filename}"
 

 
def upload_to_profile_divorce(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.ProfileId), filename)
    return f"profile_divorce/{filename}"
 
def upload_to_profile(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.profile_id), filename)
    return f"profile_images/{filename}"

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
    Otp_verify = models.SmallIntegerField(max_length=10)
    Stage = models.SmallIntegerField()
    AdminPermission = models.SmallIntegerField()  # Changed from CharField to TextField
    Payment = models.CharField(max_length=10)  # Changed from CharField to TextField
    PaymentExpire = models.DateTimeField(max_length=15)  # Changed from CharField to TextField
    PaymentType = models.CharField(max_length=255)  # Changed from CharField to TextField


    Profile_name = models.CharField(max_length=255,null=True, blank=True) 
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
    Profile_emailid= models.CharField(max_length=20)
    Profile_idproof = models.FileField(upload_to=upload_to_profile_basic,storage=AzureMediaStorage())
    # Profile_divorceproof = models.FileField(upload_to=upload_to_profile_basic,storage=AzureMediaStorage())
    Profile_divorceproof = models.FileField(upload_to=upload_to_profile_divorce,storage=AzureMediaStorage())
    Profile_gothras = models.CharField(max_length=255)
    Photo_password = models.CharField(max_length=255)
    Photo_protection = models.SmallIntegerField(default=0)
    Video_url= models.CharField(max_length=255)
    Plan_id= models.CharField(max_length=100)
    Addon_package= models.CharField(max_length=100)
    # Last_login_date= models.CharField(max_length=100)
    Last_login_date= models.CharField(max_length=100,null=True, blank=True)  
    # Last_login_date = models.DateTimeField(null=True, blank=True)
    #Last_login_date= models.DateTimeField()
    Notifcation_enabled= models.CharField(max_length=100,null=True, blank=True)
    Featured_profile= models.CharField(max_length=100,null=True, blank=True)
    DateOfJoin= models.CharField(max_length=100,null=True, blank=True) #models.DateTimeField()
    Reset_OTP = models.CharField(max_length=6, blank=True, null=True)
    quick_registration=models.CharField(max_length=6, blank=True, null=True)
    #Reset_OTP_Time =  models.CharField(max_length=100)   #models.CharField(max_length=100)
    # Reset_OTP_Time = models.DateTimeField()
    #Reset_OTP_Time = models.DateTimeField('Edit the date', null=True, blank=True)
    Reset_OTP_Time = models.DateTimeField(null=True, blank=True)
    Profile_verified = models.SmallIntegerField(default=0)
    device_id=models.TextField(null=True, blank=True)
    fcm_token=models.TextField(null=True, blank=True)
    primary_status = models.IntegerField() 
    secondary_status = models.IntegerField() 
    plan_status = models.IntegerField() 

    #Profile_idproof= models.TextField()
    

    Status = models.IntegerField(null=True, blank=True) 


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'logindetails'  # Name of the table in your database

    def __str__(self):
        return self.ProfileId
    






    
    
# class Registration2(models.Model):
#     Profile_name = models.CharField(max_length=250)
#     Profile_marital_status = models.CharField(max_length=250)
#     Profile_dob = models.CharField(max_length=250)
#     Profile_height = models.CharField(max_length=250)
#     Profile_complexion = models.CharField(max_length=250)


#     class Meta:
#         managed = False  # This tells Django not to handle database table creation/migration for this model
#         db_table = 'logindetails_temp'  # Name of the table in your database

#     def __str__(self):
#         return self.ProfileId
    

class Profileholder(models.Model):

    Mode = models.SmallIntegerField(primary_key=True)
    ModeName = models.CharField(max_length=50)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'mastermode'  # Name of the table in your database

    def __str__(self):
        return self.Mode
    
# class Profileheights(models.Model):

#     height_id = models.SmallIntegerField(primary_key=True)
#     height_desc = models.CharField(max_length=50)
   

#     class Meta:
#         managed = False  # This tells Django not to handle database table creation/migration for this model
#         db_table = 'heightmaster'  # Name of the table in your database

#     def __str__(self):
#         return self.Mode
    


class Profileheights(models.Model):

    height_id = models.SmallIntegerField(primary_key=True)
    height_desc = models.CharField(max_length=50)
    height_value = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'heightmaster'  # Name of the table in your database

    def __str__(self):
        return self.height_id


class Profilecomplexion(models.Model):

    complexion_id    = models.SmallIntegerField(primary_key=True)
    complexion_desc = models.CharField(max_length=200)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'complexionmaster'  # Name of the table in your database

    def __str__(self):
        return self.complexion_id
    


# class Profilecomplexion(models.Model):

#     complexion_id    = models.SmallIntegerField(primary_key=True)
#     complexion_desc = models.CharField(max_length=200)
   

#     class Meta:
#         managed = False  # This tells Django not to handle database table creation/migration for this model
#         db_table = 'complexionmaster'  # Name of the table in your database

#     def __str__(self):
#         return self.complexion_id
    

class Profilecountry(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    most_pref = models.SmallIntegerField()
    is_active = models.SmallIntegerField()
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'mastercountry'  # Name of the table in your database

    def __str__(self):
        return self.id
    





class Profilestate(models.Model):

    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    country_id = models.SmallIntegerField()  
    is_active = models.SmallIntegerField()
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterstate'  # Name of the table in your database

    def __str__(self):
        return self.id
    

class Profiledistrict(models.Model):

    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    state_id = models.SmallIntegerField()  
    is_active = models.SmallIntegerField()
    is_deleted = models.SmallIntegerField()

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterdistrict'  # Name of the table in your database

    def __str__(self):
        return self.id


class Profilecity(models.Model):
    
    id = models.SmallIntegerField(primary_key=True)
    district_id = models.SmallIntegerField() 
    city_name=models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'mastercity'  # Name of the table in your database

    def __str__(self):
        return self.id


class ProfileMaritalstatus(models.Model):

    StatusId = models.SmallIntegerField(primary_key=True)
    MaritalStatus = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   
   
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'maritalstatusmaster'  # Name of the table in your database

    def __str__(self):
        return self.StatusId 
    


    
class Parentoccupation(models.Model):

    id     = models.SmallIntegerField(primary_key=True)
    occupation = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterparentsoccupation'  # Name of the table in your database

    def __str__(self):

        print('masterparentsoccupation')
        return self.id
    

class Propertyworth(models.Model):

    id     = models.SmallIntegerField(primary_key=True)
    property = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterpropertyworth'  # Name of the table in your database

    def __str__(self):

        # print('masterpropertyworth')
        return self.id
    
class Highesteducation(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    degree = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterhighesteducation'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Ugdegree(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    degree = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterugdegree'  # Name of the table in your database

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
    
class Profileedu_degree(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    edu_level = models.CharField(max_length=100)
    fieldof_study = models.CharField(max_length=100)
    degeree_name = models.CharField(max_length=100)
    is_active = models.SmallIntegerField()
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masteredu_degeree'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Annualincome(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    income = models.DecimalField(max_digits=10, decimal_places=2)  
    is_deleted = models.SmallIntegerField() 

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterannualincome'  # Name of the table in your database

    def __str__(self):
        return self.id

class Placeofbirth(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    place = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterplaceofbirth'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Lagnamdidi(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterlagnam'  # Name of the table in your database

    def __str__(self):
        return self.id
    
   
class Dasaname(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterdasaname'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Birthstar(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    star = models.CharField(max_length=100)
    tamil_series = models.CharField(max_length=200)
    telugu_series = models.CharField(max_length=200)
    kannada_series = models.CharField(max_length=200)
    is_deleted = models.SmallIntegerField()
    #is_active = models.SmallIntegerField(max_length=1)

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterbirthstar'  # Name of the table in your database

    def __str__(self):
        return str(self.id)


class Rasi(models.Model):

    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    star_id = models.CharField(max_length=20)
    tamil_series = models.CharField(max_length=200)
    telugu_series = models.CharField(max_length=200)
    kannada_series = models.CharField(max_length=200)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterrasi'  # Name of the table in your database

    def __str__(self):
        return self.id

# class Image_Upload(models.Model):
#     id = models.AutoField(primary_key=True)  # Use AutoField for primary key
#     profile_id = models.CharField(max_length=50)  # Use IntegerField for profile_id
#     image = models.ImageField(upload_to='images/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         managed = False  # Assuming this model is managed externally
#         db_table = 'profile_images'



class Image_Upload(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    # image = models.ImageField(upload_to=upload_to_profile)
    image = models.ImageField(upload_to=upload_to_profile, storage=AzureMediaStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)
    image_approved  = models.SmallIntegerField(blank=True, null=True)
    is_deleted  = models.SmallIntegerField(blank=True, null=True)

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
  


# class profile_images(models.Model):
#     id = models.AutoField(primary_key=True)
#     profile_id = models.CharField(max_length=50)
#     image = models.CharField(max_length=255)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         managed = False  # Assuming this model is managed externally
#         db_table = 'profile_images'


class Familytype(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterfamilytype'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Familystatus(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    status  = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    is_deleted = models.SmallIntegerField()

   
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterfamilystatus'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Familyvalue(models.Model):

    FamilyValueid = models.SmallIntegerField(primary_key=True)
    FamilyValue = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()

   
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterfamilyvalue'  # Name of the table in your database

    def __str__(self):
        return self.FamilyValueid
        


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

    def get_matching_stars(birth_rasi_id, birth_star_id, gender):
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
            AND sp.source_star_id = %s AND sp.source_rasi_id = %s 
        GROUP BY 
            sp.id, sp.gender, sp.source_star_id
        '''
        with connection.cursor() as cursor:
            cursor.execute(query, [gender, birth_star_id , birth_rasi_id])
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


class Matchingporutham(models.Model):
    id = models.IntegerField(primary_key=True)
    protham_name = models.CharField(max_length=200)
    status =models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'matching_porutham_names'

    def __str__(self):
        return self.id



class Statepref(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    state  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterstatepref'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Edupref(models.Model):

    RowId  = models.SmallIntegerField(primary_key=True)
    EducationLevel  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'mastereducation'  # Name of the table in your database

    def __str__(self):
        return self.RowId
    
class Profespref(models.Model):

    RowId    = models.SmallIntegerField(primary_key=True)
    profession  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterprofession'  # Name of the table in your database

    def __str__(self):
        return self.RowId

def upload_to_profile_horoscope_admin(instance, filename):
    # return os.path.join('profile_{0}'.format(instance.ProfileId), filename)
    return f"profile_horoscope/horoscope/{filename}"
    
class Horoscope(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)  
    time_of_birth = models.CharField(max_length=100,null=True,blank=True)
    place_of_birth = models.CharField(max_length=100)
    birthstar_name = models.CharField(max_length=20)
    birth_rasi_name = models.CharField(max_length=20)  # Changed from CharField to TextField
    lagnam_didi = models.CharField(max_length=50,null=True,blank=True)
    didi= models.CharField(max_length=100,null=True,blank=True)
    chevvai_dosaham = models.CharField(max_length=100,null=True,blank=True)
    ragu_dosham = models.CharField(max_length=100,null=True,blank=True)  # Changed from CharField to TextField
    nalikai = models.CharField(max_length=100,null=True,blank=True)
    dasa_name = models.CharField(max_length=100,null=True,blank=True)
    dasa_balance = models.CharField(max_length=100,null=True,blank=True)  # Changed from CharField to TextField
    horoscope_hints = models.CharField(max_length=200,null=True,blank=True)  # Changed from CharField to TextField
    rasi_kattam = models.CharField(max_length=1000,null=True,blank=True)  # Changed from CharField to TextField
    amsa_kattam = models.CharField(max_length=1000,null=True,blank=True)  # Changed from CharField to TextField
   # horoscope_file = models.TextField()
    horoscope_file = models.FileField(upload_to=upload_to_profile_horoscope,storage=AzureMediaStorage(),null=True,blank=True)
    horo_file_updated = models.CharField(max_length=100,null=True, blank=True)

    calc_chevvai_dhosham = models.CharField(max_length=100,null=True, blank=True)
    calc_raguketu_dhosham = models.CharField(max_length=100,null=True, blank=True)
    horoscope_file_admin = models.FileField(upload_to=upload_to_profile_horoscope_admin,storage=AzureMediaStorage(),null=True,blank=True)

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_horoscope'  # Name of the table in your database

    def __str__(self):
        return self.id


class Familydetails(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)   
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)  # Changed from CharField to TextField
    mother_occupation = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    about_self = models.CharField(max_length=1000)  # Changed from CharField to TextField
    hobbies = models.CharField(max_length=500)
    blood_group = models.CharField(max_length=50)
    Pysically_changed = models.CharField(max_length=20)  # Changed from CharField to TextField
    no_of_brother = models.CharField(max_length=20)  # Changed from CharField to TextField
    no_of_sister = models.CharField(max_length=20)  # Changed from CharField to TextField
    no_of_sis_married = models.CharField(max_length=20)  # Changed from CharField to TextField
    no_of_bro_married = models.CharField(max_length=20)  # Changed from CharField to TextField
    family_type = models.CharField(max_length=100)
    family_value = models.CharField(max_length=100)
    family_status = models.CharField(max_length=100)
    property_details = models.CharField(max_length=1000)
    property_worth = models.CharField(max_length=1000)
    suya_gothram = models.CharField(max_length=100)
    uncle_gothram = models.CharField(max_length=100)
    ancestor_origin = models.CharField(max_length=1000)
    about_family = models.CharField(max_length=1000)
    weight = models.CharField(max_length=100, null=True)
    eye_wear = models.CharField(max_length=100, null=True)
    body_type = models.CharField(max_length=100, null=True)
    no_of_children = models.IntegerField(max_length=10 , null=True)
    madulamn = models.CharField(max_length=10 ,null=True,blank=True)
    father_alive = models.CharField(max_length=10 ,null=True,blank=True)
    mother_alive = models.CharField(max_length=10 ,null=True,blank=True)
    
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_familydetails'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Edudetails(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    highest_education = models.CharField(max_length=100)
    field_ofstudy= models.CharField(max_length=100)
    degree= models.CharField(max_length=100)
    ug_degeree = models.CharField(max_length=100)
    about_edu = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)  # Changed from CharField to TextField
    anual_income = models.CharField(max_length=50)
    actual_income = models.CharField(max_length=100)
    work_country = models.CharField(max_length=100)  # Changed from CharField to TextField
    work_state = models.CharField(max_length=100)
    work_city = models.CharField(max_length=100)
    work_district = models.CharField(max_length=100) 
    work_pincode = models.CharField(max_length=100)
    work_place = models.CharField(max_length=100)
    career_plans = models.CharField(max_length=100)  # Changed from CharField to TextField
    currency= models.CharField(max_length=100) 
    company_name= models.CharField(max_length=100) 
    designation= models.CharField(max_length=100) 
    profession_details= models.CharField(max_length=100) 
    business_name= models.CharField(max_length=100) 
    business_address= models.CharField(max_length=100) 
    nature_of_business= models.CharField(max_length=100) 
    other_degree= models.CharField(max_length=100) 



    status = models.IntegerField()   # Changed from CharField to TextField
    

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_edudetails'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Partnerpref(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    pref_age_differences = models.CharField(max_length=50)
    pref_height_from = models.CharField(max_length=50)
    pref_height_to = models.CharField(max_length=50)
    pref_marital_status = models.CharField(max_length=50,null=True, blank=True)
    pref_profession = models.CharField(max_length=50,null=True, blank=True)  # Changed from CharField to TextField
    pref_education = models.CharField(max_length=50,null=True, blank=True)
    pref_anual_income = models.CharField(max_length=50,null=True, blank=True)
    pref_anual_income_max = models.CharField(max_length=255,null=True, blank=True)
    pref_chevvai = models.CharField(max_length=20,null=True, blank=True)  # Changed from CharField to TextField
    pref_ragukethu = models.CharField(max_length=20,null=True, blank=True)
    pref_foreign_intrest = models.CharField(max_length=20,null=True, blank=True)
    pref_porutham_star = models.TextField(null=True, blank=True)
    pref_porutham_star_rasi = models.TextField(null=True, blank=True)
    status = models.IntegerField()   # Changed from CharField to TextField
    
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_partner_pref'  # Name of the table in your database

    def __str__(self):
        return self.id
    

class PlanDetails(models.Model):
    # Define your model fields here
    id = models.IntegerField(primary_key=True)
    plan_name = models.CharField(max_length=50)
    plan_price = models.DecimalField(max_digits=10, decimal_places=2)
    plan_renewal_cycle = models.IntegerField()
    plan_status = models.CharField(max_length=100)

    class Meta:
        db_table = 'plan_master'

    @staticmethod
    def get_plan_details():
        query = '''
        SELECT
            pm.id AS plan_id,
            pm.plan_name,
            CAST(pm.plan_price AS SIGNED) AS plan_price,
            pm.plan_renewal_cycle,
            pf.id AS feature_id,
            pf.feature_name,
            pf.feature_desc
        FROM
            plan_master pm
        JOIN
            plan_feature_associations pfa ON pm.id = pfa.plan_id
        JOIN
            plan_features pf ON pfa.feature_id = pf.id
            WHERE pm.id NOT IN (14, 15, 17)  
        '''   #exclude the Plan id for the renewal customers
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]


            return result

    @staticmethod
    def get_plan_details_renewal():
        query = '''
        SELECT
            pm.id AS plan_id,
            pm.plan_name,
            CAST(pm.plan_price AS SIGNED) AS plan_price,
            pm.plan_renewal_cycle,
            pf.id AS feature_id,
            pf.feature_name,
            pf.feature_desc
        FROM
            plan_master pm
        JOIN
            plan_feature_associations pfa ON pm.id = pfa.plan_id
        JOIN
            plan_features pf ON pfa.feature_id = pf.id
            WHERE pm.id IN (14, 15, 17)  
        '''   #exclude the Plan id for the renewal customers
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]


            return result
        

class Get_profiledata(models.Model):

    ContentId  = models.AutoField(primary_key=True)
    temp_profileid = models.CharField(max_length=200)
    profile_id = models.CharField(max_length=50)
    LoginId = models.CharField(max_length=50)
    Profile_for = models.CharField(max_length=50)
    Gender = models.TextField(max_length=100)  # Changed from CharField to TextField
    Mobile_no = models.CharField(max_length=50)
   
    # @staticmethod
    # def get_profile_list(gender,profile_id):
    #     # query = '''SELECT l.*,pi.*,pp.*pf.*,ph.*,pe.* FROM logindetails l LEFT JOIN profile_edudetails pe ON pe.profile_id=l.ProfileId LEFT JOIN profile_familydetails pf ON pf.profile_id=l.ProfileId LEFT JOIN profile_horoscope ph ON ph.profile_id=l.ProfileId LEFT JOIN profile_images pi ON pi.profile_id=l.ProfileId LEFT JOIN profile_partner_pref pp ON pp.profile_id=l.ProfileId '''
    #     query = '''SELECT a.*, a.ProfileId, a.Profile_name, a.Profile_marital_status, a.Profile_dob, a.Profile_height, a.Profile_city, f.profession, 
    #             f.highest_education, g.EducationLevel, d.star as star_name , e.birthstar_name ,e.birth_rasi_name
    #             FROM logindetails a 
    #             JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
    #             JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
    #             JOIN masterbirthstar d ON d.id = e.birthstar_name 
    #             JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
    #             JOIN mastereducation g ON f.highest_education = g.RowId 
    #             WHERE a.Gender != %s AND a.ProfileId != %s '''
    #     with connection.cursor() as cursor:
    #         cursor.execute(query,[gender,profile_id])
    #         columns = [col[0] for col in cursor.description]
    #         rows = cursor.fetchall()
    #         result = [
    #             dict(zip(columns, row))
    #             for row in rows
    #         ]
    #     #print("Query result:", result)
    #     return result
    # @staticmethod
    # def get_profile_details(profile_ids):
    #     # query = '''SELECT l.*, pi.*, pp.*, pf.*, ph.*, pe.*
    #     #     FROM logindetails l 
    #     #     LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
    #     #     LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
    #     #     LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
    #     #     LEFT JOIN profile_images pi ON pi.profile_id = l.ProfileId 
    #     #     LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
    #     #     WHERE l.ProfileId IN %s  '''
    #     query = '''SELECT l.*, pp.*, pf.*, ph.*, pe.*
    #         FROM logindetails l 
    #         LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
    #         LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
    #         LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
    #         LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
    #         WHERE l.ProfileId IN %s  '''
    #     with connection.cursor() as cursor:
    #         cursor.execute(query,[tuple(profile_ids)])
    #         columns = [col[0] for col in cursor.description]
    #         rows = cursor.fetchall()
    #         result = [
    #             dict(zip(columns, row))
    #             for row in rows
    #         ]
    #     #print("Query result:", result)
    #     return result


    #updated by vinoth 1908-2024

    @staticmethod
    def get_profile_list(gender, profile_id, start, per_page, search_profile_id, order_by, search_profession, search_age, search_location):
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences

            try:
                age_diff = int(age_difference_str) if age_difference_str else 5  # Default to 5 if None
            except (ValueError, TypeError):
                age_diff = 5  # Fallback to default if conversion fails

            pref_annual_income = partner_pref.pref_anual_income
            pref_marital_status = partner_pref.pref_marital_status
            partner_pref_education = partner_pref.pref_education
            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi = partner_pref.pref_porutham_star_rasi
            partner_pref_foreign_intrest = partner_pref.pref_foreign_intrest
            partner_pref_ragukethu = partner_pref.pref_ragukethu
            partner_pref_chevvai = partner_pref.pref_chevvai

            min_max_query = """
                SELECT MIN(income_amount) AS min_income, 
                    MAX(income_amount) AS max_income
                FROM masterannualincome
                WHERE FIND_IN_SET(id, %s) > 0"""

            with connection.cursor() as cursor:
                cursor.execute(min_max_query, [pref_annual_income])
                min_max_income = cursor.fetchone()
            
            if min_max_income:
                min_income, max_income = min_max_income
            
            try:
                age_difference = int(age_difference_str)
            except ValueError:
                return [], 0, {}           
            
            if search_age:
                age_difference = int(search_age)
            age_diff = int(age_difference) if age_difference else 5

            if gender.upper() == "MALE":
                min_age = max(current_age - age_diff, 18)
                max_age = current_age
            elif gender.upper() == "FEMALE":
                min_age = max(current_age, 18)
                max_age = current_age + age_diff

            try:
                base_query = """
                SELECT DISTINCT 
                        a.ProfileId, a.Plan_id, a.DateOfJoin, a.Photo_protection,
                        a.Profile_city, a.Profile_verified, a.Profile_name, a.Profile_dob,
                        a.Profile_height, e.birthstar_name, e.birth_rasi_name, f.ug_degeree,
                        f.profession, f.highest_education, g.EducationLevel, d.star, h.income,
                        v.viewed_profile,
                        pi.first_image_id AS has_image
                    FROM logindetails a
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id
                    JOIN masterbirthstar d ON d.id = e.birthstar_name
                    JOIN profile_edudetails f
                        ON a.ProfileId = f.profile_id
                    JOIN mastereducation g ON f.highest_education = g.RowId
                    JOIN masterannualincome h ON h.id = f.anual_income
                    LEFT JOIN vw_profile_images pi ON a.ProfileId = pi.profile_id
                    LEFT JOIN profile_visit_logs v
                        ON v.viewed_profile = a.ProfileId AND v.profile_id = %s
                    WHERE a.Status = 1 
                    AND a.Plan_id NOT IN (0,3, 16, 18)
                    AND a.gender != %s
                    AND a.ProfileId != %s
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) BETWEEN %s AND %s"""

                query_params = [profile_id, gender, profile_id, min_age, max_age]

                if min_income and max_income:
                    base_query += " AND h.income_amount BETWEEN %s AND %s"
                    query_params.extend([min_income, max_income])

                if partner_pref_porutham_star_rasi:
                    base_query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                    query_params.append(partner_pref_porutham_star_rasi)

                if partner_pref_education:
                    base_query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                    query_params.append(partner_pref_education)

                if pref_marital_status:
                    base_query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                    query_params.append(pref_marital_status)

                if partner_pref_foreign_intrest and partner_pref_foreign_intrest.lower() == 'yes':
                    base_query += " AND f.work_country != '1'"
                elif partner_pref_foreign_intrest and partner_pref_foreign_intrest.lower() == 'no':
                    base_query += " AND f.work_country = '1'"

                if partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'yes':
                    base_query += " AND LOWER(e.ragu_dosham) = 'yes'"
                elif partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'no':
                    base_query += " AND LOWER(e.ragu_dosham) = 'no'"

                if partner_pref_chevvai and partner_pref_chevvai.lower() == 'yes':
                    base_query += " AND LOWER(e.chevvai_dosaham) = 'yes'"
                elif partner_pref_chevvai and partner_pref_chevvai.lower() == 'no':
                    base_query += " AND LOWER(e.chevvai_dosaham) = 'no'"

                height_conditions = ""
                if partner_pref_height_from and partner_pref_height_to:
                    height_conditions = " AND a.Profile_height BETWEEN %s AND %s"
                    query_params.extend([partner_pref_height_from, partner_pref_height_to])
                elif partner_pref_height_from:
                    height_conditions = " AND a.Profile_height >= %s"
                    query_params.append(partner_pref_height_from)
                elif partner_pref_height_to:
                    height_conditions = " AND a.Profile_height <= %s"
                    query_params.append(partner_pref_height_to)

                search_profile_id_cond = ''
                if search_profile_id:
                    search_profile_id_cond = " AND (a.ProfileId = %s OR a.Profile_name LIKE %s)"
                    query_params.append(search_profile_id)
                    query_params.append(f"%{search_profile_id}%")

                search_profession_cond = ''
                if search_profession:
                    search_profession_cond = " AND f.profession = %s"
                    query_params.append(search_profession)

                search_location_cond = ''
                if search_location:
                    search_location_cond = " AND a.Profile_state = %s"
                    query_params.append(search_location)

                # Updated ordering logic
                # plan_priority = "FIELD(a.Plan_id, 2,15,1,14,11,12,13,6,7,8,9)"
                # photo_priority = "(SELECT 1 FROM profile_images WHERE profile_id = a.ProfileId AND image_approved = 1 AND is_deleted = 0 LIMIT 1) IS NOT NULL"
                # view_priority = "v.viewed_profile IS NULL"

                try:
                    # [Previous code remains the same until the ordering logic]
                    
                    # Updated ordering logic with proper image priority
                    plan_priority = "FIELD(a.Plan_id, 2,15,1,14,11,12,13,6,7,8,9)"
                    # Changed to ensure profiles with images come first
                    # photo_priority = "CASE WHEN (SELECT 1 FROM profile_images WHERE profile_id = a.ProfileId AND image_approved = 1 AND is_deleted = 0 LIMIT 1) IS NOT NULL THEN 0 ELSE 1 END"
                    photo_priority = "CASE WHEN pi.first_image_id IS NOT NULL THEN 0 ELSE 1 END"
                    view_priority = "CASE WHEN v.viewed_profile IS NULL THEN 0 ELSE 1 END"

                    try:
                        order_by = int(order_by)
                    except (ValueError, TypeError):
                        order_by = None

                    if order_by == 1:
                        orderby_cond = f" ORDER BY {plan_priority}, {photo_priority}, {view_priority}, a.DateOfJoin DESC"
                    elif order_by == 2:
                        orderby_cond = f" ORDER BY {plan_priority}, {photo_priority}, {view_priority}, a.DateOfJoin ASC"
                    else:
                        orderby_cond = f" ORDER BY {plan_priority}, {photo_priority}, {view_priority}, a.DateOfJoin DESC"
                
                except Exception as e:
                    print(f"Error in profile listing: {str(e)}")
                    return [], 0, {}

                query = base_query + height_conditions + search_profile_id_cond + search_profession_cond + search_location_cond + orderby_cond
                count_query_params = query_params.copy()

                with connection.cursor() as cursor1:
                    cursor1.execute(query, query_params)
                    profile_with_indices = {}
                    index = 1
                    fetch_size = 200

                    while True:
                        rows = cursor1.fetchmany(fetch_size)
                        if not rows:
                            break
                        for row in rows:
                            profile_with_indices[str(index)] = row[0]
                            index += 1

                total_count = index - 1

                query += " LIMIT %s, %s"
                query_params.extend([start, per_page])

                # print(query)


                # def format_sql_for_debug(query, params):
                #         def escape(value):
                #             if isinstance(value, str):
                #                 return f"'{value}'"
                #             elif value is None:
                #                 return 'NULL'
                #             else:
                #                 return str(value)
                #         try:
                #             return query % tuple(map(escape, params))
                #         except Exception as e:
                #             print("Error formatting query:", e)
                #             return query

                #     # Usage:
                # final_query = format_sql_for_debug(query, query_params)

                # print(final_query)

                with connection.cursor() as cursor:
                    cursor.execute(query, query_params)
                    rows = cursor.fetchall()

                    if rows:
                        columns = [col[0] for col in cursor.description]
                        results = [dict(zip(columns, row)) for row in rows]
                        return results, total_count, profile_with_indices
                    else:
                        return [], 0, {}

            except Exception as e:
                print(f"Error in profile listing: {str(e)}")
                return [], 0, {}

        except Exception as e:
            print(f"Error in profile listing: {str(e)}")
            return [], 0, {}


    @staticmethod
    def get_profile_match_count(profile_id):
        # print("Fetching profile details...")

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
            partner_pref_porutham_star_rasi = partner_pref.pref_porutham_star_rasi

            partner_pref_foreign_intrest= partner_pref.pref_foreign_intrest
            partner_pref_ragukethu= partner_pref.pref_ragukethu
            partner_pref_chevvai= partner_pref.pref_chevvai

            # Get Min/Max income range from masterannualincome
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MIN(income_amount), MAX(income_amount)
                    FROM masterannualincome
                    WHERE FIND_IN_SET(id, %s) > 0
                """, [pref_annual_income])
                min_max_income = cursor.fetchone()

            min_income, max_income = min_max_income if min_max_income else (None, None)

            try:
                age_difference = int(age_difference_str)
                
            except ValueError:
                return [], 0, {}
            

            age_difference = int(age_difference) if age_difference else 5
        
            
            # if gender.upper() == "MALE":
            #     matching_age = current_age - age_difference
            #     age_condition_operator = "<"
            # else:
            #     matching_age = current_age + age_difference
            #     age_condition_operator = ">"
            # if gender.upper() == "MALE":
            #     min_age = current_age - age_difference
            #     max_age = current_age
            # elif gender.upper() == "FEMALE":
            #     min_age = current_age
            #     max_age = current_age + age_difference
            print(age_difference,'age_difference')
            if gender.upper() == "MALE":
                min_age = max(current_age - age_difference, 18)  # 🛡 Never below 18
                max_age = current_age
            elif gender.upper() == "FEMALE":
                min_age = max(current_age, 18)             # 🛡 Ensure at least 18
                max_age = current_age + age_difference


            # Base query to get matching profiles
            query = """
                 SELECT DISTINCT a.ProfileId,a.Plan_id ,a.DateOfJoin,a.Photo_protection,a.Profile_city,a.Profile_verified,a.Profile_name,a.Profile_dob,a.Profile_height,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.Status=1 AND a.Plan_id NOT IN (0,16, 18, 3) AND a.gender != %s AND a.ProfileId != %s 
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) BETWEEN %s AND %s
            """
            
            query_params = [gender, profile_id, min_age , max_age]

            if min_income and max_income:
                query += " AND h.income_amount BETWEEN %s AND %s"
                query_params.extend([min_income, max_income])

            if partner_pref_education:
                query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                query_params.append(partner_pref_education)

            if partner_pref_porutham_star_rasi:
                query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                query_params.append(partner_pref_porutham_star_rasi)

            if pref_marital_status:
                query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                query_params.append(pref_marital_status)
            
            if partner_pref_foreign_intrest == 'yes' or partner_pref_foreign_intrest == 'Yes':
                query += " AND f.work_country !='1'"

            elif partner_pref_foreign_intrest == 'no' or partner_pref_foreign_intrest == 'No':
                query += " AND f.work_country = '1'"


            if partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'yes':
                query += " AND LOWER(e.ragu_dosham) = 'yes'"
            elif partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'no':
                query += " AND LOWER(e.ragu_dosham) = 'no'"

            if partner_pref_chevvai and partner_pref_chevvai.lower() == 'yes':
                query += " AND LOWER(e.chevvai_dosaham) = 'yes'"
            elif partner_pref_chevvai and partner_pref_chevvai.lower() == 'no':
                query += " AND LOWER(e.chevvai_dosaham) = 'no'"



            if partner_pref_height_from and partner_pref_height_to:
                query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([partner_pref_height_from, partner_pref_height_to])
            elif partner_pref_height_from:
                query += " AND a.Profile_height >= %s"
                query_params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                query += " AND a.Profile_height <= %s"
                query_params.append(partner_pref_height_to)

            # Sorting logic
            orderby_cond = " ORDER BY a.DateOfJoin DESC"
            query += orderby_cond

            with connection.cursor() as cursor:
                # cursor.execute(query.format(operator=age_condition_operator), query_params)
                cursor.execute(query, query_params)
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return results  # Returns full profile details

            return []  # Return empty list if no matches found

        except Exception as e:
            print(f"Error: {e}")
            return []



    @staticmethod
    def get_profile_list_for_pref_type(profile_id,use_suggested=False):
        # print("Fetching profile details...")

        
        if use_suggested:
            try:
                partner_pref = ProfileSuggestedPref.objects.get(profile_id=profile_id)
            except ProfileSuggestedPref.DoesNotExist:
                return []
        else:
            try:
                partner_pref = Partnerpref.objects.get(profile_id=profile_id)
            except Partnerpref.DoesNotExist:
                return []
        
        
        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            # partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences
            pref_annual_income = partner_pref.pref_anual_income
            pref_marital_status = partner_pref.pref_marital_status
            partner_pref_education = partner_pref.pref_education
            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi = partner_pref.pref_porutham_star_rasi

            partner_pref_foreign_intrest= partner_pref.pref_foreign_intrest
            partner_pref_ragukethu= partner_pref.pref_ragukethu
            partner_pref_chevvai= partner_pref.pref_chevvai

            # Get Min/Max income range from masterannualincome
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT MIN(income_amount), MAX(income_amount)
                    FROM masterannualincome
                    WHERE FIND_IN_SET(id, %s) > 0
                """, [pref_annual_income])
                min_max_income = cursor.fetchone()

            min_income, max_income = min_max_income if min_max_income else (None, None)

            try:
                age_difference = int(age_difference_str)
                
            except ValueError:
                return []

            age_difference = int(age_difference) if age_difference else 5
            if gender.upper() == "MALE":
                min_age = max(current_age - age_difference, 18)  # 🛡 Never below 18
                max_age = current_age
            elif gender.upper() == "FEMALE":
                min_age = max(current_age, 18)             # 🛡 Ensure at least 18
                max_age = current_age + age_difference


            # Base query to get matching profiles
            query = """
                 SELECT DISTINCT a.ProfileId,a.Plan_id ,a.DateOfJoin,a.Photo_protection,a.Profile_city,a.Profile_verified,a.Profile_name,a.Profile_dob,a.Profile_height,e.birthstar_name,e.birth_rasi_name,f.ug_degeree,f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.Status=1 AND a.Plan_id NOT IN (0,16, 18, 3) AND a.gender != %s AND a.ProfileId != %s 
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) BETWEEN %s AND %s
            """
            
            query_params = [gender, profile_id, min_age , max_age]

            if min_income and max_income:
                query += " AND h.income_amount BETWEEN %s AND %s"
                query_params.extend([min_income, max_income])

            if partner_pref_education:
                query += " AND FIND_IN_SET(g.RowId, %s) > 0"
                query_params.append(partner_pref_education)

            if partner_pref_porutham_star_rasi:
                query += " AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0"
                query_params.append(partner_pref_porutham_star_rasi)

            if pref_marital_status:
                query += " AND FIND_IN_SET(a.Profile_marital_status, %s) > 0"
                query_params.append(pref_marital_status)
            
            if partner_pref_foreign_intrest == 'yes' or partner_pref_foreign_intrest == 'Yes':
                query += " AND f.work_country !='1'"

            elif partner_pref_foreign_intrest == 'no' or partner_pref_foreign_intrest == 'No':
                query += " AND f.work_country = '1'"


            if partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'yes':
                query += " AND LOWER(e.ragu_dosham) = 'yes'"
            elif partner_pref_ragukethu and partner_pref_ragukethu.lower() == 'no':
                query += " AND LOWER(e.ragu_dosham) = 'no'"

            if partner_pref_chevvai and partner_pref_chevvai.lower() == 'yes':
                query += " AND LOWER(e.chevvai_dosaham) = 'yes'"
            elif partner_pref_chevvai and partner_pref_chevvai.lower() == 'no':
                query += " AND LOWER(e.chevvai_dosaham) = 'no'"



            if partner_pref_height_from and partner_pref_height_to:
                query += " AND a.Profile_height BETWEEN %s AND %s"
                query_params.extend([partner_pref_height_from, partner_pref_height_to])
            elif partner_pref_height_from:
                query += " AND a.Profile_height >= %s"
                query_params.append(partner_pref_height_from)
            elif partner_pref_height_to:
                query += " AND a.Profile_height <= %s"
                query_params.append(partner_pref_height_to)

            # view_priority = "CASE WHEN v.viewed_profile IS NULL THEN 0 ELSE 1 END "
            # plan_priority = "FIELD(a.Plan_id, '3','17','2','15','1','14','11','12','13','6','7','8','9') "
            # photo_priority = "CASE WHEN i.image IS NOT NULL AND i.image != '' THEN 0 ELSE 1 END "

            # # Sorting logic
            # orderby_cond = f" ORDER BY {plan_priority}, {photo_priority}, {view_priority}, a.DateOfJoin DESC"
            # query += orderby_cond

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
                
            print("MySQL Executable Query:", format_sql_for_debug(query, query_params))

            with connection.cursor() as cursor:
                # cursor.execute(query.format(operator=age_condition_operator), query_params)
                cursor.execute(query, query_params)
                rows = cursor.fetchall()

                if rows:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in rows]
                    return results  # Returns full profile details

            return []  # Return empty list if no matches found

        except Exception as e:
            print(f"Error: {e}")
            return []



    @staticmethod
    def get_profile_details(profile_ids):
        
        query = '''SELECT l.*,l.status as pstatus, pp.*, pf.*, ph.*, pe.*,mr.name as rasi_name,mb.star as star_name , mp.Profession as profession_name
            FROM logindetails l 
            LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
            LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
            LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
            LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
            LEFT JOIN masterrasi mr ON mr.id = ph.birth_rasi_name 
            LEFT JOIN masterbirthstar mb ON mb.id = ph.birthstar_name
            LEFT JOIN masterprofession mp ON mp.RowId = pe.profession
            WHERE  l.ProfileId IN %s  '''


        with connection.cursor() as cursor:
            cursor.execute(query,[tuple(profile_ids)])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            result = [
                dict(zip(columns, row))
                for row in rows
            ]
        # print("Query result:", result)
        return result


class Express_interests(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    to_express_message = models.CharField(max_length=1000)
    req_datetime = models.DateTimeField()
    response_datetime = models.DateTimeField() 
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_express_interest'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Profile_wishlists(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    marked_datetime = models.DateTimeField()
    status = models.CharField(max_length=50)  #if status is 1 requestsent 2 is accepted 3 is rejected


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_wishlists'  # Name of the table in your database

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


class Profile_docviewlogs(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=100)
    viewed_profile = models.CharField(max_length=100)
    type = models.IntegerField(null=True)
    datetime = models.DateTimeField()
    status = models.CharField(max_length=15)  #if status is 1 requestsent 2 is accepted 3 is rejected


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_doc_view_log'  # Name of the table in your database

    def __str__(self):
        return self.id


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
    





class Photo_request(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    req_datetime = models.TextField()
    response_datetime = models.DateTimeField()
    response_message = models.DateTimeField() 
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_photo_request'  # Name of the table in your database

    def __str__(self):
        return self.id
    


class Profile_vysassist(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_from = models.CharField(max_length=50)
    profile_to = models.CharField(max_length=50)
    req_datetime = models.DateTimeField()
    response_datetime = models.DateTimeField(null=True, blank=True) 
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
    

class Profile_notification(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=100)
    from_profile_id = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50)
    message_titile = models.TextField()
    to_message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_notifications'  # Name of the table in your database

    def __str__(self):
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
    click_to_call_count  = models.IntegerField(null=True, blank=True)
    who_can_see_profile = models.IntegerField(null=True, blank=True)
    featured_profile = models.IntegerField(null=True, blank=True)
    priority_circulation = models.IntegerField(null=True, blank=True)
    email_blast = models.IntegerField(null=True, blank=True)
    astro_service = models.IntegerField(null=True, blank=True)
    vys_assist = models.IntegerField(null=True, blank=True)
    vys_assist_count = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'plan_feature_limits'
   
    def __str__(self):
        # return f"PlanFeatureLimit {self.id}"
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
    


class ProfileAlertSettings(models.Model):
    id = models.AutoField(primary_key=True)
    alert_type = models.IntegerField(null=True)
    alert_name = models.CharField(max_length=155, null=True)
    notification_type = models.CharField(max_length=155, null=True)
    status = models.IntegerField(null=True)

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_alertsettings'  # Name of the table in your database

    def __str__(self):
        return self.alert_name
    

class MasterProfession(models.Model):
    id = models.IntegerField(primary_key=True)
    profession = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        managed = False  
        db_table = 'masterprofession1'

    def __str__(self):
        return self.profession
    

#Happy stories api


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
    

class Testimonial(models.Model):
    profile_id = models.CharField(max_length=50)
    rating = models.IntegerField()
    review_content = models.TextField()
    user_image = models.ImageField(upload_to='testimonials/',storage=AzureMediaStorage())
    status = models.IntegerField(default=1)
    date = models.DateField(auto_now_add=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        managed = False 
        db_table = 'profile_testimonials'  

    def __str__(self):
        return f"Testimonial by {self.profile_id} - Rating: {self.rating}"
    




class PageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False) 

class Page(models.Model):
    page_name = models.CharField(max_length=255)
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.CharField(max_length=255)
    status = models.CharField(max_length=10)
    content = RichTextField()  
    deleted = models.BooleanField(default=False)  
    objects = models.Manager() 
    active_objects = PageManager()  

    class Meta:
        managed = False  # Django will not handle table creation/migration
        db_table = 'page'  # Database table name

    def __str__(self):
        return self.page_name
    

class NotificationQueue(models.Model):
    id =models.AutoField(primary_key=True)
    profile_id =  models.CharField(max_length=255)
    notification_type = models.CharField(max_length=50)
    message_title = models.CharField(max_length=100)
    message_text = models.TextField()
    is_processed = models.BooleanField(default=False)  # Track if it's been processed
    is_taken = models.BooleanField(default=False) 
    take_datetime = models.DateTimeField(default=None)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  # Django will not handle table creation/migration
        db_table = 'notificationqueue'  # Database table name

    def __str__(self):
        return self.profile_id


class AdminSettings(models.Model):
    site_name = models.CharField(max_length=100, primary_key=True)  
    meta_title = models.CharField(max_length=100)
    meta_description = models.TextField()
    contact_number = models.CharField(max_length=15)
    whatsapp_number = models.CharField(max_length=15)
    email_address = models.EmailField()
    location_address = models.CharField(max_length=200)
    support_phone = models.CharField(max_length=15, blank=True, null=True)
    support_whatsapp = models.CharField(max_length=15, blank=True, null=True)
    support_email = models.EmailField(blank=True, null=True)
    copyrights = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  
        db_table = 'adminsite'  

    def __str__(self):
        return self.site_name





from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=1000)
    user_ids = models.CharField(max_length=1000)

    class Meta:
        managed = False  # Django will not handle table creation/migration
        db_table = 'room'  # Database table name

    def __str__(self):
        return self.name

class Message(models.Model):
    value = models.CharField(max_length=1000000)
    date = models.DateTimeField(default=timezone.now)
    user = models.CharField(max_length=255)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    read_msg = models.BooleanField(default=False)


    class Meta:
        managed = False  # Django will not handle table creation/migration
        db_table = 'Message'  # Database table name

    def __str__(self):
        return self.value


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


    
class Districtpref(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    district  = models.CharField(max_length=100)
    is_deleted = models.SmallIntegerField()
   

    class Meta:
        managed = False  
        db_table = 'masterdistrictpref'  

    def __str__(self):
        return self.id



class ProfileVisibility(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    visibility_age_from = models.CharField(max_length=50)
    visibility_age_to = models.CharField(max_length=50)
    visibility_height_from = models.CharField(max_length=50)
    visibility_height_to = models.CharField(max_length=50)
    visibility_profession = models.CharField(max_length=50)  
    visibility_education = models.CharField(max_length=50)
    visibility_anual_income = models.CharField(max_length=50)
    visibility_chevvai = models.CharField(max_length=20)  
    visibility_ragukethu = models.CharField(max_length=20)
    visibility_foreign_interest = models.CharField(max_length=20)
    status = models.IntegerField()   
    
    class Meta:
        managed = False  
        db_table = 'profile_visibility'  

    def __str__(self):
        return self.id



class profile_loginLogs(models.Model):
    id  = models.AutoField(primary_key=True)
    profile_id =  models.CharField(max_length=250)
    user_token  =  models.CharField(max_length=250)
    login_datetime = models.DateTimeField()
    logout_datetime = models.DateTimeField()

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_loginLogs'  # Name of the table in your database

    def __str__(self):
        return self.id


class PaymentTransaction(models.Model):

    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)
    plan_id = models.IntegerField(max_length=50)
    addon_package = models.CharField(max_length=255)
    order_id = models.CharField(max_length=255)
    payment_id =  models.CharField(max_length=255)  
    payment_type = models.CharField(max_length=255)  
    amount = models.DecimalField(max_digits=10, decimal_places=2) 
    status = models.CharField(max_length=50) #i is pending #2 is paid  # 3 is failed
    created_at = models.DateTimeField()

    class Meta:
        managed = False  
        db_table = 'payment_transaction'  

    def __str__(self):
        return self.id
    
    
class PlanSubscription(models.Model):

    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)
    plan_id = models.IntegerField(max_length=50)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode= models.CharField(max_length=75)
    status =  models.IntegerField(max_length=10)  
    payment_date = models.DateTimeField()
    payment_by= models.CharField(max_length=150)
    admin_user= models.CharField(max_length=150)
    order_id= models.CharField(max_length=150)

    class Meta:
        managed = False  
        db_table = 'plan_subscription'  

    def __str__(self):
        return self.id
    
class ProfileVysAssistFollowup(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key with auto-increment
    assist_id = models.IntegerField()
    owner_id = models.IntegerField()
    comments = models.TextField()
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False  
        db_table = 'profile_vys_assist_followups'

    def __str__(self):
        return f"Follow-up {self.id} (Assist ID: {self.assist_id})"
    

    
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
    click_to_call_count  = models.IntegerField(null=True, blank=True)
    who_can_see_profile = models.IntegerField(null=True, blank=True)
    featured_profile = models.IntegerField(null=True, blank=True)
    priority_circulation = models.IntegerField(null=True, blank=True)
    email_blast = models.IntegerField(null=True, blank=True)
    astro_service = models.IntegerField(null=True, blank=True)
    vys_assist = models.IntegerField(null=True, blank=True)
    vys_assist_count = models.IntegerField(null=True, blank=True)
    exp_int_lock = models.IntegerField(null=True, blank=True)
    membership_fromdate = models.DateTimeField(null=True, blank=True)
    membership_todate = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'profile_plan_feature_limits'
   
    def __str__(self):
        # return f"PlanFeatureLimit {self.id}"
        return str(self.id)
    
class SentWithoutAddressEmailLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Multiple profile IDs
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField()  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'sent_without_address_email_log'  # Table name

    def __str__(self):
        return f"Without Address Email Log {self.id} - Profile {self.profile_id} to {self.to_ids}"

    
class SentWithoutAddressPrintPDFLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField(default=datetime.now)  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'sent_without_address_print_pdf_log'  # Database table name

    def __str__(self):
        return f"Without Address Print PDF Log {self.id} - Profile {self.profile_id} to {self.to_ids}"
    
class SentWithoutAddressPrintwpPDFLog(models.Model):
    id = models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=255)  # Stores multiple profile IDs as a string
    to_ids = models.CharField(max_length=255)  # Recipient profile ID
    profile_owner = models.CharField(max_length=50)  # Owner of the profile
    status = models.CharField(max_length=20)  # "sent" or "failed"
    sent_datetime = models.DateTimeField(default=datetime.now)  # Timestamp

    class Meta:
        managed = False  # This table already exists in DB
        db_table = 'sent_withoutaddress_whatsapp_print_pdf_log'  # Database table name

    def __str__(self):
        return f"Without Address Print PDF Log {self.id} - Profile {self.profile_id} to {self.to_ids}"


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