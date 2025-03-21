from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'mastercountry'

class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, related_name='states', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterstate'

class District(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, related_name='districts', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterdistrict'

class Religion(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterreligion'

class Caste(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'mastercaste'

class ProfileHolder(models.Model):
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)  # daughter, son, friend, etc.

    def __str__(self):
        return f"{self.name} ({self.relation})"

    class Meta:
        db_table = 'masterprofileholder'

class MaritalStatus(models.Model):
    MaritalStatus = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.MaritalStatus

    class Meta:
        db_table = 'maritalstatusmaster'

class Height(models.Model):
    height_desc = models.DecimalField(max_digits=5, decimal_places=2, primary_key=True)

    def __str__(self):
        return str(self.height_desc)

    class Meta:
        db_table = 'heightmaster'

class Complexion(models.Model):
    complexion_desc = models.CharField(max_length=50)

    def __str__(self):
        return self.complexion_desc

    class Meta:
        db_table = 'complexionmaster'

class ParentsOccupation(models.Model):
    occupation = models.CharField(max_length=100)

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
    degree = models.CharField(max_length=100)

    def __str__(self):
        return self.degree

    class Meta:
        db_table = 'masterugdegree'

class AnnualIncome(models.Model):
    income = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.income)

    class Meta:
        db_table = 'masterannualincome'

class PlaceOfBirth(models.Model):
    place = models.CharField(max_length=100)

    def __str__(self):
        return self.place

    class Meta:
        db_table = 'masterplaceofbirth'

class BirthStar(models.Model):
    star = models.CharField(max_length=100)

    def __str__(self):
        return self.star

    class Meta:
        db_table = 'masterbirthstar'

class Rasi(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterrasi'

class Lagnam(models.Model):
    name = models.CharField(max_length=100)

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

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'masterfamilytype'

class FamilyStatus(models.Model):
    status = models.CharField(max_length=100)

    def __str__(self):
        return self.status

    class Meta:
        db_table = 'masterfamilystatus'


class FamilyValue(models.Model):
    FamilyValue = models.CharField(max_length=100)

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


class LoginDetails(models.Model):
    ProfileId = models.CharField(max_length=50, unique=True, primary_key=True, null=False, blank=False)
    temp_profileid = models.CharField(max_length=100)
    Gender = models.CharField(max_length=10)
    Mobile_no = models.CharField(max_length=15)
    EmailId = models.EmailField()
    Password = models.CharField(max_length=100)
    Profile_marital_status = models.CharField(max_length=50)
    Profile_dob = models.DateField()
    Profile_complexion = models.CharField(max_length=50)
    Profile_address = models.TextField()
    Profile_country = models.CharField(max_length=100)
    Profile_state = models.CharField(max_length=100)
    Profile_city = models.CharField(max_length=100)
    Profile_pincode = models.CharField(max_length=10)  # Corrected here

    class Meta:
        db_table = 'logindetails'

class ProfileFamilyDetails(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True, null=False, blank=False)
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    about_self = models.TextField()
    hobbies = models.TextField()
    blood_group = models.CharField(max_length=10)
    Pysically_changed = models.CharField(max_length=10)  # Corrected here
    property_details = models.TextField()
    property_worth = models.CharField(max_length=100)
    suya_gothram = models.CharField(max_length=100)
    uncle_gothram = models.CharField(max_length=100)
    ancestor_origin = models.TextField()
    about_family = models.TextField()

    class Meta:
        db_table = 'profile_familydetails'

class ProfileEduDetails(models.Model):
    profile_id = models.CharField(max_length=50, unique=True, primary_key=True, null=False, blank=False)
    highest_education = models.CharField(max_length=100)
    ug_degeree = models.CharField(max_length=100)
    # profession = models.CharField(max_length=100)
    about_edu = models.TextField()
    anual_income = models.CharField(max_length=100)
    actual_income = models.CharField(max_length=100)  # Corrected here
    work_country = models.CharField(max_length=100)
    work_state = models.CharField(max_length=100)
    work_pincode = models.CharField(max_length=10)  # Corrected here
    career_plans = models.TextField()

    class Meta:
        db_table = 'profile_edudetails'


class ProfilePartnerPref(models.Model):
    profile_id = models.CharField(max_length=50)
    pref_age_differences = models.CharField(max_length=10)
    # from_month = models.CharField(max_length=10)
    # from_year = models.CharField(max_length=10)
    # age_pref = models.CharField(max_length=10)
    pref_height_from = models.CharField(max_length=10)
    pref_education = models.CharField(max_length=100)
    pref_profession = models.CharField(max_length=100)
    pref_chevvai = models.CharField(max_length=10)
    pref_anual_income = models.CharField(max_length=100)
    pref_ragukethu = models.CharField(max_length=10)
    pref_marital_status = models.CharField(max_length=100)
    pref_foreign_intrest = models.CharField(max_length=100)
    # family_value_pref = models.CharField(max_length=100)
    # place_of_stay_pref = models.CharField(max_length=100)
    # city_pref = models.CharField(max_length=100)

    class Meta:
        db_table = 'profile_partner_pref'
