from django.db import models
from CredentialApp.models import tbl_login

from django.utils import timezone

# *************************************** ORPHANAGE MODULE TABLES ******************************************* 

# District Table
class tbl_District(models.Model):
    district= models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.district
    class Meta:
        verbose_name_plural = "Districts"

# OrphanageDetails Table
class tbl_orphanage(models.Model):
    email =models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=250,blank=True)
    orphanage_id = models.CharField(max_length=250,blank=True)
    mobile = models.CharField(max_length=250,blank=True)
    district= models.ForeignKey(tbl_District, on_delete=models.SET_NULL, blank=True, null=True)
    city= models.CharField(max_length=12, blank=True)
    address= models.CharField(max_length=12, blank=True)
    pin= models.CharField(max_length=12, blank=True)
    date = models.DateField(max_length=12, blank=True)
    status=models.BooleanField(default=False)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Orphanages"


# table for storing item donations
class donationtype(models.Model):
    orphanage =models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200,default=1,unique=True)
    category = models.CharField(max_length=200,default=1)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Donation items"
    

#Childrens Details Table
class tbl_children(models.Model):
    email =models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    fname = models.CharField(max_length=250,blank=True)
    # lname = models.CharField(max_length=250,blank=True)
    gender = models.CharField(max_length=250,blank=True)
    date_birth = models.DateField(max_length=12, blank=True)
    date_join = models.DateField(max_length=12, blank=True)
    image=models.ImageField(upload_to='Children_Image',blank=True)
    district= models.CharField(max_length=50, blank=True)
    city= models.CharField(max_length=12, blank=True)
    address= models.CharField(max_length=12, blank=True)
    pin= models.CharField(max_length=12, blank=True)
    status=models.BooleanField(default=True)
    class Meta:
        verbose_name_plural = "Children"



# for add student marks and perform linear regression
class marks(models.Model):
    orphanage =models.ForeignKey(tbl_orphanage, on_delete=models.SET_NULL, blank=True, null=True)
    student =models.ForeignKey(tbl_children, on_delete=models.SET_NULL, blank=True, null=True,unique=True)
    name=models.CharField(default=0,max_length=100)
    mark1= models.FloatField(default=0)
    mark2= models.FloatField(default=0)
    passpercentage=models.FloatField(default=0)
    predicted_passpercentage=models.FloatField(default=0)
    status=models.BooleanField(default=0)

    def calculate_pass_percentage(self):
        print("**********")
        return (self.mark1 + self.mark2)/2

    def save(self, *args, **kwargs):
        self.passpercentage = self.calculate_pass_percentage()
        super().save(*args, **kwargs)
 

    def save(self, *args, **kwargs):
        self.passpercentage = self.calculate_pass_percentage()
        self.predicted_passpercentage = self.predict_pass_percentage()
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Children marks"  
   



#Childrens Education Details Table
class tbl_children_Education(models.Model):
    email =models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    child_id =models.ForeignKey(tbl_children, on_delete=models.SET_NULL, blank=True, null=True)
    college = models.CharField(max_length=250,blank=True)
    course = models.CharField(max_length=250,blank=True)
    cgpa = models.CharField(max_length=250,blank=True)
    specialization = models.CharField(max_length=250,blank=True)
    date_join = models.DateField(max_length=12, blank=True)
    date_end = models.DateField(max_length=12, blank=True)
    class Meta:
        verbose_name_plural = "Children Education details"



class tbl_category(models.Model):
    orphanage =models.ForeignKey(tbl_orphanage, on_delete=models.SET_NULL, blank=True, null=True)
    category = models.CharField(max_length=250,blank=True)

# ************************************** VOLUNTEER MODULE TABLE'S *******************************************
   
# Volunteer Details(Registration) Table
class tbl_volunteer(models.Model):
    email=models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    orphanage =models.ForeignKey(tbl_orphanage, on_delete=models.SET_NULL, blank=True, null=True)
    fname = models.CharField(max_length=250,blank=True)
    lname= models.CharField(max_length=250,blank=True)
    gender = models.CharField(max_length=250,blank=True)
    mobile = models.CharField(max_length=250,blank=True)
    district= models.CharField(max_length=50, blank=True)
    city= models.CharField(max_length=50, blank=True)
    address= models.CharField(max_length=50, blank=True)
    pin= models.CharField(max_length=12, blank=True)
    date = models.DateField(auto_now_add=True)
    status=models.BooleanField(default=False)
    image=models.ImageField(upload_to='Children_Image',blank=True)
    def __str__(self):
        return self.fname
    class Meta:
        verbose_name_plural = "Volunteers"


class tbl_leave(models.Model):
    orphanage = models.ForeignKey(tbl_orphanage, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(tbl_volunteer, on_delete=models.CASCADE)
    date_applied = models.DateTimeField(default=timezone.now)
    leave_date = models.DateField()
    reason = models.CharField(max_length=250,blank=True,null=True)
    status = models.BooleanField(default=False)
    def __str__(self):
        return self.volunteer.fname
# ************************************** Donor MODULE TABLE'S *******************************************


# Donor Details Table
import phonenumbers

class tbl_donor(models.Model):
    email = models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    fname = models.CharField(max_length=250, blank=True)
    lname = models.CharField(max_length=250, blank=True)
    mobile = models.CharField(max_length=250, blank=True)
    district = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=50, blank=True)
    pin = models.CharField(max_length=12, blank=True)

    def save(self, *args, **kwargs):
        if self.mobile:
            try:
                # parse the phone number using the phonenumbers library
                parsed_number = phonenumbers.parse(self.mobile, "IN")

                # set the mobile field to the phone number with the country code
                self.mobile = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except phonenumbers.NumberParseException:
                pass
        super().save(*args, **kwargs)


# Donor Details Table
class tbl_donor_new_address(models.Model):
    email=models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    fname = models.CharField(max_length=250,blank=True)
    lname= models.CharField(max_length=250,blank=True)
    mobile = models.CharField(max_length=250,blank=True)
    district= models.CharField(max_length=50, blank=True)
    city= models.CharField(max_length=50, blank=True)
    address= models.CharField(max_length=50, blank=True)
    pin= models.CharField(max_length=12, blank=True)
    class Meta:
        verbose_name_plural = "Donor details"


# Donations Details Table
class tbl_amount_donations(models.Model):
    email=models.ForeignKey(tbl_login, on_delete=models.SET_NULL, blank=True, null=True)
    orphanage=models.ForeignKey(tbl_orphanage, on_delete=models.SET_NULL, blank=True, null=True)
    donated_date=models.DateTimeField(auto_now=True,null=True)
    amount= models.IntegerField(default=0)
    status= models.IntegerField(default=0)
    def __str__(self):
        return self.email
    class Meta:
        verbose_name_plural = "Donations details"


class donations(models.Model):
    user=models.ForeignKey(tbl_login,on_delete=models.CASCADE)    
    item=models.CharField(max_length=400,null=True)
    orphanage=models.ForeignKey(tbl_orphanage,on_delete=models.CASCADE,null=True)   
    address=models.ForeignKey(tbl_donor_new_address,on_delete=models.CASCADE,null=True)   
    otherdonations=models.CharField(max_length=200,null=True)
    date=models.DateField(null=True)
    status=models.BooleanField(default=False)
    donated_date=models.DateTimeField(auto_now=True,null=True)
    def __str__(self):
        return self.user.email
    class Meta:
        verbose_name_plural = "Donations Details"



class AssignedVolunteer(models.Model):
    donation = models.ForeignKey(donations, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(tbl_volunteer, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)
    status=models.BooleanField(default=False, null= True)
