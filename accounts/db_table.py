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
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.status

    class Meta:
        db_table = 'mastermaritalstatus'

class Height(models.Model):
    value = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.value)

    class Meta:
        db_table = 'masterheight'

class Complexion(models.Model):
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'mastercomplexion'

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
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value

    class Meta:
        db_table = 'masterfamilyvalue'
