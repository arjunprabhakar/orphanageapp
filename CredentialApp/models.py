from django.db import models

# Create your models here.

# Login Table
class tbl_login(models.Model):
    email = models.CharField(max_length=200, unique=True, primary_key=True)
    password = models.CharField(max_length=100)
    otp = models.IntegerField(default=1)
    status=models.BooleanField(default=False )
    type=models.IntegerField(default=False)
    class Meta:
        verbose_name_plural = "Login details"

    def str(self):
        return self.email

