from django.db import models, connection
from django.http import JsonResponse
from rest_framework.views import status
from django.shortcuts import get_object_or_404
import os
from django.utils import timezone
from datetime import datetime
from ckeditor.fields import RichTextField

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
    status = models.IntegerField() 

    
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'logindetails_temp'  # Name of the table in your database

    def __str__(self):
        return self.ProfileId


def upload_to_profile_basic(instance, filename):
    return os.path.join('profile_{0}'.format(instance.ProfileId), filename)


def upload_to_profile(instance, filename):
    return os.path.join('profile_{0}'.format(instance.profile_id), filename)
    
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
    Profile_pincode = models.CharField(max_length=200)
    Profile_alternate_mobile= models.CharField(max_length=20)
    Profile_whatsapp= models.CharField(max_length=20)
    Profile_mobile_no= models.CharField(max_length=20)
    Profile_idproof = models.FileField(upload_to=upload_to_profile_basic)
    Profile_divorceproof = models.FileField(upload_to=upload_to_profile_basic)
    Profile_gothras = models.CharField(max_length=255)
    Photo_password = models.CharField(max_length=255)
    Photo_protection = models.SmallIntegerField(default=0)
    Video_url= models.CharField(max_length=255)
    Plan_id= models.CharField(max_length=100)
    Addon_package= models.CharField(max_length=100)
    # Last_login_date= models.CharField(max_length=100)
    Last_login_date= models.CharField(max_length=100)  
    #Last_login_date= models.DateTimeField()
    Notifcation_enabled= models.CharField(max_length=100)
    Featured_profile= models.CharField(max_length=100)
    DateOfJoin= models.CharField(max_length=100) #models.DateTimeField()
    Reset_OTP = models.CharField(max_length=6, blank=True, null=True)
    #Reset_OTP_Time =  models.CharField(max_length=100)   #models.CharField(max_length=100)
    # Reset_OTP_Time = models.DateTimeField()
    #Reset_OTP_Time = models.DateTimeField('Edit the date', null=True, blank=True)
    Reset_OTP_Time = models.DateTimeField(null=True, blank=True)

    #Profile_idproof= models.TextField()
    

    status = models.IntegerField() 


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
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'heightmaster'  # Name of the table in your database

    def __str__(self):
        return self.height_id


class Profilecomplexion(models.Model):

    complexion_id    = models.SmallIntegerField(primary_key=True)
    complexion_desc = models.CharField(max_length=200)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'complexionmaster'  # Name of the table in your database

    def __str__(self):
        return self.complexion_id
    


class Profilecomplexion(models.Model):

    complexion_id    = models.SmallIntegerField(primary_key=True)
    complexion_desc = models.CharField(max_length=200)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'complexionmaster'  # Name of the table in your database

    def __str__(self):
        return self.complexion_id
    

class Profilecountry(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    is_active = models.SmallIntegerField()
   

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
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterstate'  # Name of the table in your database

    def __str__(self):
        return self.id
    

class Profilecity(models.Model):

    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    state_id = models.SmallIntegerField()  
    is_active = models.SmallIntegerField()
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterdistrict'  # Name of the table in your database

    def __str__(self):
        return self.id
    

class ProfileMaritalstatus(models.Model):

    StatusId = models.SmallIntegerField(primary_key=True)
    MaritalStatus = models.CharField(max_length=100)
   
   
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'maritalstatusmaster'  # Name of the table in your database

    def __str__(self):
        return self.StatusId 
    


    
class Parentoccupation(models.Model):

    id     = models.SmallIntegerField(primary_key=True)
    occupation = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterparentsoccupation'  # Name of the table in your database

    def __str__(self):

        print('masterparentsoccupation')
        return self.id
    

class Propertyworth(models.Model):

    id     = models.SmallIntegerField(primary_key=True)
    property = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterpropertyworth'  # Name of the table in your database

    def __str__(self):

        # print('masterpropertyworth')
        return self.id
    
class Highesteducation(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    degree = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterhighesteducation'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Ugdegree(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    degree = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterugdegree'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Annualincome(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    income = models.DecimalField(max_digits=10, decimal_places=2)   

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
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterlagnam'  # Name of the table in your database

    def __str__(self):
        return self.id
    
   
class Dasaname(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name  = models.CharField(max_length=100)
   

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
    image = models.ImageField(upload_to=upload_to_profile)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # Assuming this model is managed externally
        db_table = 'profile_images'

class Familytype(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    name  = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterfamilytype'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Familystatus(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    status  = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

   
    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterfamilystatus'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Familyvalue(models.Model):

    FamilyValueid = models.SmallIntegerField(primary_key=True)
    FamilyValue = models.CharField(max_length=100)

   
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
    
    


class Statepref(models.Model):

    id    = models.SmallIntegerField(primary_key=True)
    state  = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterstatepref'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Edupref(models.Model):

    RowId  = models.SmallIntegerField(primary_key=True)
    EducationLevel  = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'mastereducation'  # Name of the table in your database

    def __str__(self):
        return self.RowId
    
class Profespref(models.Model):

    RowId    = models.SmallIntegerField(primary_key=True)
    profession  = models.CharField(max_length=100)
   

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'masterprofession'  # Name of the table in your database

    def __str__(self):
        return self.RowId
    
class Horoscope(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)  
    time_of_birth = models.CharField(max_length=100)
    place_of_birth = models.CharField(max_length=100)
    birthstar_name = models.CharField(max_length=20)
    birth_rasi_name = models.CharField(max_length=20)  # Changed from CharField to TextField
    lagnam_didi = models.CharField(max_length=50)
    chevvai_dosaham = models.CharField(max_length=100)
    ragu_dosham = models.CharField(max_length=100)  # Changed from CharField to TextField
    nalikai = models.CharField(max_length=100)
    dasa_name = models.CharField(max_length=100)
    dasa_balance = models.CharField(max_length=100)  # Changed from CharField to TextField
    horoscope_hints = models.CharField(max_length=200)  # Changed from CharField to TextField
    rasi_kattam = models.CharField(max_length=1000)  # Changed from CharField to TextField
    amsa_kattam = models.CharField(max_length=1000)  # Changed from CharField to TextField
   # horoscope_file = models.TextField()
    horoscope_file = models.FileField(upload_to=upload_to_profile)
    horo_file_updated = models.CharField(max_length=100)

    calc_chevvai_dhosham = models.CharField(max_length=100)
    calc_raguketu_dhosham = models.CharField(max_length=100)


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


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_familydetails'  # Name of the table in your database

    def __str__(self):
        return self.id
    
class Edudetails(models.Model):
    id    =  models.AutoField(primary_key=True)
    profile_id = models.CharField(max_length=50)
    highest_education = models.CharField(max_length=100)
    ug_degeree = models.CharField(max_length=100)
    about_edu = models.CharField(max_length=100)
    profession = models.CharField(max_length=100)  # Changed from CharField to TextField
    anual_income = models.CharField(max_length=50)
    actual_income = models.CharField(max_length=100)
    work_country = models.CharField(max_length=100)  # Changed from CharField to TextField
    work_state = models.CharField(max_length=100)
    work_city = models.CharField(max_length=100)
    work_pincode = models.CharField(max_length=100)
    career_plans = models.CharField(max_length=100)  # Changed from CharField to TextField
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
            pm.plan_price,
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
        '''
        
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
    def get_profile_list(gender,profile_id,start, per_page , search_profile_id , order_by,search_profession,search_age,search_location):
        # query = '''SELECT l.*,pi.*,pp.*pf.*,ph.*,pe.* FROM logindetails l LEFT JOIN profile_edudetails pe ON pe.profile_id=l.ProfileId LEFT JOIN profile_familydetails pf ON pf.profile_id=l.ProfileId LEFT JOIN profile_horoscope ph ON ph.profile_id=l.ProfileId LEFT JOIN profile_images pi ON pi.profile_id=l.ProfileId LEFT JOIN profile_partner_pref pp ON pp.profile_id=l.ProfileId '''

        print('gender',gender)
        print('profile_id',profile_id)


        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences
            pref_annual_income = partner_pref.pref_anual_income

            print('pref_anual_income',pref_annual_income)
            
            
            
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
                print('min_income', min_income)
                print('max_income', max_income)
            else:
                print('No income data found for the provided IDs.')


            # print('partner_pref_porutham_star_rasi',partner_pref_porutham_star_rasi)

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
                print('female age cond')
                matching_age = current_age + age_difference
                age_condition_operator = ">"

            try:
                    base_query = """
                    SELECT a.*, f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income
                    FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.gender != %s AND a.ProfileId != %s
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s
                    AND h.income_amount BETWEEN %s AND %s
                    AND FIND_IN_SET(g.RowId,  %s) > 0
                    AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0
                    """

                    height_conditions = ""
                    # print('partner_pref_porutham_star_rasifgdgfdf',partner_pref_porutham_star_rasi)
                    # query_params = [gender, profile_id, matching_age, pref_annual_income, partner_pref_education,partner_pref_porutham_star_rasi]
                    query_params = [gender, profile_id, matching_age, min_income,max_income, partner_pref_education,partner_pref_porutham_star_rasi]

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
                        search_profile_id_cond = "AND a.ProfileId = %s"
                        query_params.append(search_profile_id)


                                # Add profession filter
                    if search_profession:
                        base_query += " AND f.profession = %s"
                        query_params.append(search_profession)

                    
                    if search_location:
                        base_query += " AND a.Profile_state = %s"
                        query_params.append(search_location)



                    orderby_cond ='ORDER BY a.DateOfJoin DESC'
                    if order_by:
                        orderby_cond = "ORDER BY a.DateOfJoin " + order_by
                        
                    # query = base_query.format(operator=age_condition_operator) + height_conditions
                    query = base_query.format(operator=age_condition_operator) + height_conditions + search_profile_id_cond + orderby_cond
                    count_query_params = query_params.copy()
                    
                    #count_query = f"SELECT COUNT(*) FROM ({query}) AS count_query"

                   
                    # Execute the COUNT query to get the total number of records
                    
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
                    
                    print('formatted_query',formatted_query)

                    cleaned_query1 = formatted_query.replace('\n', ' ').replace('  ', ' ').strip()

                    with connection.cursor() as cursor:
                        cursor.execute(query, query_params)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [col[0] for col in cursor.description]
                            results = [dict(zip(columns, row)) for row in rows]

                            return results , total_count , profile_with_indices
                        else:
                            # print('123')
                            # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': cleaned_query}, status=status.HTTP_404_NOT_FOUND)
                            return None , 0 , None

                    # except Exception as e:
                    #     # Log the exception
                    #     #print(f"An error occurred: {str(e)}")
                    #     return None ,0 ,None # Return 0 as the total count in case of an error

            except Exception as e:
                print(str(e),'weegger')
                # return JsonResponse({'status': 'failure1', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return None , 0 , None

        except Exception as e:
                # print('12357576')

                print(str(e))

                # return JsonResponse({'status': 'failure2', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return None , 0 , None
        
    @staticmethod
    def get_profile_match_count(gender,profile_id):
        # query = '''SELECT l.*,pi.*,pp.*pf.*,ph.*,pe.* FROM logindetails l LEFT JOIN profile_edudetails pe ON pe.profile_id=l.ProfileId LEFT JOIN profile_familydetails pf ON pf.profile_id=l.ProfileId LEFT JOIN profile_horoscope ph ON ph.profile_id=l.ProfileId LEFT JOIN profile_images pi ON pi.profile_id=l.ProfileId LEFT JOIN profile_partner_pref pp ON pp.profile_id=l.ProfileId '''

        print('gender',gender)
        print('profile_id',profile_id)


        try:
            profile = get_object_or_404(Registration1, ProfileId=profile_id)
            gender = profile.Gender
            current_age = calculate_age(profile.Profile_dob)

            partner_pref = get_object_or_404(Partnerpref, profile_id=profile_id)
            age_difference_str = partner_pref.pref_age_differences
            pref_annual_income = partner_pref.pref_anual_income
            pref_marital_status = partner_pref.pref_marital_status

           
            partner_pref_education = partner_pref.pref_education
            print('pref_annual_income',pref_annual_income)
            print('partner_pref_education',partner_pref_education)

            partner_pref_height_from = partner_pref.pref_height_from
            partner_pref_height_to = partner_pref.pref_height_to
            partner_pref_porutham_star_rasi= partner_pref.pref_porutham_star_rasi

            print('partner_pref_porutham_star_rasi',partner_pref_porutham_star_rasi)


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
            else:
                print('No income data found for the provided IDs.')

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
                    SELECT a.*, f.profession, 
                    f.highest_education, g.EducationLevel, d.star, h.income
                    FROM logindetails a 
                    JOIN profile_partner_pref b ON a.ProfileId = b.profile_id 
                    JOIN profile_horoscope e ON a.ProfileId = e.profile_id 
                    JOIN masterbirthstar d ON d.id = e.birthstar_name 
                    JOIN profile_edudetails f ON a.ProfileId = f.profile_id 
                    JOIN mastereducation g ON f.highest_education = g.RowId 
                    JOIN masterannualincome h ON h.id = f.anual_income
                    WHERE a.gender != %s AND a.ProfileId != %s
                    AND TIMESTAMPDIFF(YEAR, a.Profile_dob, CURDATE()) {operator} %s
                    AND h.income_amount BETWEEN %s AND %s
                    AND FIND_IN_SET(g.RowId,  %s) > 0
                    AND FIND_IN_SET(CONCAT(e.birthstar_name, '-', e.birth_rasi_name), %s) > 0
                    """

                    height_conditions = ""
                    # print('partner_pref_porutham_star_rasifgdgfdf',partner_pref_porutham_star_rasi)
                    query_params = [gender, profile_id, matching_age, min_income,max_income, partner_pref_education,partner_pref_porutham_star_rasi]

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
                    
                    print('formatted_query',formatted_query)

                    cleaned_query1 = formatted_query.replace('\n', ' ').replace('  ', ' ').strip()

                    with connection.cursor() as cursor:
                        cursor.execute(query, query_params)
                        rows = cursor.fetchall()

                        if rows:
                            columns = [col[0] for col in cursor.description]
                            results = [dict(zip(columns, row)) for row in rows]

                            return results
                        else:
                            # print('123')
                            # return JsonResponse({'status': 'failure', 'message': 'No records found.', 'query': cleaned_query}, status=status.HTTP_404_NOT_FOUND)
                            return None

            except Exception as e:
                # print('123567')
                # return JsonResponse({'status': 'failure1', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return None

        except Exception as e:
                # print('12357576')

                # print(str(e))

                # return JsonResponse({'status': 'failure2', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                 return None



    @staticmethod
    def get_profile_details(profile_ids):
        # query = '''SELECT l.*, pi.*, pp.*, pf.*, ph.*, pe.*
        #     FROM logindetails l 
        #     LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
        #     LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
        #     LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
        #     LEFT JOIN profile_images pi ON pi.profile_id = l.ProfileId 
        #     LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
        #     WHERE l.ProfileId IN %s  '''

        # Below query is without joining the birth start and rsi start tables
        # query = '''SELECT l.*, pp.*, pf.*, ph.*, pe.*
        #     FROM logindetails l 
        #     LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
        #     LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
        #     LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
        #     LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
        #     WHERE l.ProfileId IN %s  '''
        
        query = '''SELECT l.*, pp.*, pf.*, ph.*, pe.*,mr.name as rasi_name,mb.star as star_name
            FROM logindetails l 
            LEFT JOIN profile_edudetails pe ON pe.profile_id = l.ProfileId 
            LEFT JOIN profile_familydetails pf ON pf.profile_id = l.ProfileId 
            LEFT JOIN profile_horoscope ph ON ph.profile_id = l.ProfileId 
            LEFT JOIN profile_partner_pref pp ON pp.profile_id = l.ProfileId 
            LEFT JOIN masterrasi mr ON mr.id = ph.birth_rasi_name 
            LEFT JOIN masterbirthstar mb ON mb.id = ph.birthstar_name
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
    response_datetime = models.TextField() 
    response_message = models.TextField() 
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
    req_datetime = models.TextField()
    response_datetime = models.TextField() 
    to_message = models.TextField() 
    status = models.CharField(max_length=50)  #if status is 1  requestsent 2 is accepted 3 is rejected 0 is removed


    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'profile_vys_assist'  # Name of the table in your database

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
    photo = models.ImageField(upload_to='success_stories/photos/')
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
    image = models.ImageField(upload_to='awards/images/')
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
    user_image = models.ImageField(upload_to='testimonials/images/')
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
    

##################################################chat#####################################################




from django.db import models
from django.utils import timezone

class Room(models.Model):
    name = models.CharField(max_length=1000)

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


    class Meta:
        managed = False  # Django will not handle table creation/migration
        db_table = 'Message'  # Database table name

    def __str__(self):
        return self.value


