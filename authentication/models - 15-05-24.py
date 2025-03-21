from django.db import models

class AuthUser(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Note: storing passwords as plain text is insecure

    class Meta:
        managed = False  # This tells Django not to handle database table creation/migration for this model
        db_table = 'auth_user'  # Name of the table in your database

    def __str__(self):
        return self.username
