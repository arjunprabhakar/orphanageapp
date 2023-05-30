from datetime import date
from hashlib import sha256
from io import BytesIO
import math,random
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.core.mail import send_mail
from CredentialApp.models import tbl_login
from OrphanageApp.models import *

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from decimal import Decimal
from django.db.models import Avg, Sum
from typing import List, Tuple

from django.db.models import Count
from django.urls import reverse
#  ********************************************* COMMON FUBCTIONS ****************************************


# Index Page 
def index(request):
    request.session.flush()
    return render(request,"common/index.html")

    
# User Login Function
def login(request):
    request.session.flush()
    if 'email' in request.session:
        return redirect(index)
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        password2=sha256(password.encode()).hexdigest()
        user=tbl_login.objects.filter(email=email,password=password2)
        if user:
            user_type=tbl_login.objects.get(email=email,password=password2)
            type=user_type.type
            email=user_type.email
            request.session['email']=email
            if type == 1:
                return redirect('Orphanage_Home')
            elif type == 2:
                return redirect('Donor_Home')
            else:
                return redirect('Volunteer_Home')
        else:
            print("invalid")
            messages.success(request,"Invalid login Credentials")
            return redirect(login)
    return render(request, 'common/login.html')


# Function for OTP Generation
def generateOTP() :
     digits = "0123456789"
     OTP = ""
     for i in range(4) :
         OTP += digits[math.floor(random.random() * 10)]
         a=OTP
     return OTP

# User Registration
def register(request):
    if request.method == 'POST':
        type=request.POST.get('type')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        passwords=sha256(pass2.encode()).hexdigest()
        if tbl_login.objects.filter(email=email,status=True).exists():
            messages.success(request,'Email already Exist....!')
            return redirect('login')
        elif tbl_login.objects.filter(email=email,status=False).exists():
            user=tbl_login.objects.get(email=email) 
            o=generateOTP()
            htmlgen = '<p>Your OTP is:'+o+'</p>'
            send_mail('OTP request',o,'orphanage management',[email], fail_silently=False, html_message=htmlgen)
            user.otp=o;
            user.save()
            messages.success(request, 'Email already exist..Please Verify Email!!!!')
            request.session['email']=email 
            return redirect('verify_otp') 
        else:
            o=generateOTP()
            htmlgen = '<p>Your OTP is:'+o+'</p>'
            send_mail('OTP request',o,'orphanage management',[email], fail_silently=False, html_message=htmlgen)
            tbl_login(email=email,password=passwords,otp=o,type=type).save()
            # messages.success(request,"registered successfully")
            request.session['email']=email 
            return redirect('verify_otp')
    return render(request, 'common/register.html')



# Otp Verification
def verify_otp(request):
    if 'email' in request.session:
        if request.method=='POST':
            otps = request.POST.get('otp');
            email = request.POST.get('email');
            session=request.session['email']
            if tbl_login.objects.filter(email=email,otp=otps): 
                user=tbl_login.objects.get(email=email)
                user.status=True;
                user.save()
                messages.success(request, 'Email is verified')
                return redirect('login')
            else:
                messages.success(request, 'Invalid Otp!!')
                return redirect('verify_otp')
        
        session=request.session['email']
        context={'session':session}
        return render(request, 'common/otp.html',context)
    else:
        return redirect(login)



# Forgot Password
def forgotpassword(request):
    if request.method =="POST":
        email=request.POST.get('email')
        if tbl_login.objects.filter(email=email).exists():
            user=tbl_login.objects.get(email=email) 
            o=generateOTP()
            htmlgen = '<p>Your OTP is:'+o+'</p>'
            send_mail('OTP request',o,'Smart Store',[email], fail_silently=False, html_message=htmlgen)
            user.otp=o;
            user.save()
            request.session['email']=email 
            messages.success(request, 'OTP is send to ..'+email+'...Please Verify')
            return redirect('verify_forgot_otp')
        else:
            messages.success(request, 'Email Not Exist ...')
            return redirect(login)

    return render(request,'common/forgotpassword.html')


# Verify forgot password OTP
def verify_forgot_otp(request):
    if 'email' in request.session:
        if request.method=='POST':
            otps = request.POST.get('otp');
            email = request.POST.get('email');
            if tbl_login.objects.filter(email=email,otp=otps):
                messages.success(request, 'OTP is Verified..Please Enter New Password...')
                return redirect(new_password)
            else:
                 messages.success(request, 'Incorrect OTP...')
    session=request.session['email']
    context={'session':session}
    return render(request,'common/verify_forgot_otp.html',context)

# New Password via Forgot Password
def new_password(request):
    if 'email' in request.session:
        if request.method=='POST':
            password = request.POST.get('pswd');
            pswd=sha256(password.encode()).hexdigest()
            email = request.POST.get('email');
            user=tbl_login.objects.get(email=email)
            user.password=pswd
            user.save()
            messages.success(request, 'Password Updated Successfully ...')
            return redirect(login)
    session=request.session['email']
    context={'session':session,}
    return render(request,'common/newpassword.html',context)

# User Logout Function
def logout(request):
    if 'email' in request.session:
        request.session.flush()
    return redirect(index)




# ************************************************* ORPHANAGE MODULE FUNCTIONS ******************************************

# Orphanage Registration Page Function
def Orphanage_Home(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_orphanage.objects.filter(email_id=email)
        if user:
            user=tbl_orphanage.objects.get(email_id=email)
            status=user.status
            if status == 1:
                user=tbl_orphanage.objects.get(email_id=email)
                children=tbl_children.objects.filter(email_id=email).count()
                data={'email':email,'user':user,'children':children}
                return render(request,"orphanage/O-index.html",data)
            else:
                return redirect(orphanage_verification)
        else:
            if request.method == 'POST':
                email=request.POST.get('email')
                name=request.POST.get('name')
                id=request.POST.get('oid')
                mobile=request.POST.get('mobile')
                district=request.POST.get('district')
                city=request.POST.get('city')
                address=request.POST.get('address')
                pin=request.POST.get('pin')
                date=request.POST.get('date')
                tbl_orphanage(email_id=email,name=name,orphanage_id=id,mobile=mobile,district_id=district,city=city,address=address,pin=pin,date=date).save()
                return redirect(orphanage_verification)
            district=tbl_District.objects.all()
            data={'email':email,'district':district}
            return render(request,"orphanage/OrphanageRegistration.html",data)
    else:
        return redirect(login)


# Orphanage Verification Page Function
def orphanage_verification(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_orphanage.objects.filter(email_id=email)
        if user:
            user=tbl_orphanage.objects.get(email_id=email)
            status=user.status
            user=tbl_orphanage.objects.get(email_id=email)
            if status == 0:
                return render(request,"orphanage/O-Verification.html",{'user':user})
            else:
                return redirect(Orphanage_Home)
        else:
            return redirect(Orphanage_Home)
    else:
        return redirect(login)



# Orphanage Profile Function
def O_Profile(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_orphanage.objects.get(email=email)
        district=tbl_District.objects.all()
        data={'user':user,'district':district}
        return render(request, 'orphanage/profile.html',data)
    else:
        return redirect(login)

# Orphanage Profile Edit Function
def O_Profile_edit(request):
    if 'email' in request.session:
        if request.method == 'POST':
            email=request.POST.get('email')
            name=request.POST.get('name')
            id=request.POST.get('oid')
            mobile=request.POST.get('mobile')
            district=request.POST.get('district')
            city=request.POST.get('city')
            address=request.POST.get('address')
            pin=request.POST.get('pin')
            date=request.POST.get('date')
            user=tbl_orphanage.objects.get(email=email)
            user.name=name
            user.orphanage_id=id
            user.mobile=mobile
            user.district_id=district
            user.city=city
            user.address=address
            user.pin=pin
            user.date=date
            user.save()
            return redirect(O_Profile)
    else:
        return redirect(login)

# Orphanage Change Password
def change_password(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.get(email=email)
        if request.method =="POST":
            old_password=request.POST.get('oldpass')
            new_password=request.POST.get('pass')
            new_pswd=sha256(new_password.encode()).hexdigest()
            pswd=sha256(old_password.encode()).hexdigest()
            if pswd == user.password:
                user.password=new_pswd
                user.save()
                print("Password updated Successfully")
                messages.success(request, 'Password updated Successfully...')
                return redirect(O_Profile)
            else:
                messages.success(request, 'Incorrect Password ...')
                print("Incorrect Password")
                return redirect(O_Profile)
    else:
        return redirect(login)


# Orphan Details Add Function
def children_add(request):
    if 'email' in request.session:
        email=request.session['email']
        if request.method =="POST":
            fname=request.POST.get('fname')
            gender=request.POST.get('gender')
            dob=request.POST.get('dob')
            doj=request.POST.get('doj')
            imgs=request.FILES.get('img')
            district=request.POST.get('district')
            city=request.POST.get('city')
            address=request.POST.get('address')
            pin=request.POST.get('pin')
            tbl_children(email_id=email,fname=fname,gender=gender,date_birth=dob,date_join=doj,image=imgs,
                        district=district,city=city,address=address,pin=pin).save()
            return redirect(children_list)
        return render(request,"orphanage/addchild.html")
    else:
        return redirect(login)

# function for deleting orphans 
def delete_children(request,id):
    if 'email' in request.session:
        email=request.session['email']
        tbl_children.objects.get(id=id,email_id=email).delete()
        return redirect(children_list)
    else:
        return redirect(login)


# Orphans list Function
def children_list(request):
    if 'email' in request.session:
        email=request.session['email']
        children=tbl_children.objects.filter(email_id=email)
        count=tbl_children.objects.filter(email_id=email).count()
        data={'children':children,
                'count':count}
        return render(request,"orphanage/children_list.html",data)
    else:
        return redirect(login)


# View Individual Orphan Details & Add Education Details  
def children_details(request,id):
    if 'email' in request.session:
        email=request.session['email']
        if request.method =="POST":
            college=request.POST.get('college')
            course=request.POST.get('course')
            spec=request.POST.get('spec')
            cgpa=request.POST.get('cgpa')
            start_date=request.POST.get('start_date')
            end_date=request.POST.get('end_date')
            tbl_children_Education(email_id=email,child_id_id=id,college=college,course=course,cgpa=cgpa,
                                   specialization=spec,date_join=start_date,date_end=end_date).save()
            return redirect(children_details,id=id)
        user=tbl_children.objects.get(id=id)
        education=tbl_children_Education.objects.filter(child_id_id=id,email_id=email)
        data={'user':user,'education':education}
        return render(request,"orphanage/children_details.html",data)
    else:
        return redirect(login)


# function for deleting orphans education
def delete_education(request,id):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_children_Education.objects.get(id=id,email_id=email)
        tbl_children_Education.objects.get(id=id,email_id=email).delete()
        return redirect(children_details,id=user.child_id_id)
    else:
        return redirect(login)


# Orphans list Function
def volunteer_list(request):
    if 'email' in request.session:
        email=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=email)
        id=orphanage.id
        volunteer=tbl_volunteer.objects.filter(orphanage_id=id)
        count=tbl_volunteer.objects.filter(orphanage_id=id).count()
        data={'volunteer':volunteer,
                'count':count}
        return render(request,"orphanage/volunteer_list.html",data)
    else:
        return redirect(login)


# Accept Volunteer Request
def Accept_Volunteer_Request(request,id):
    if 'email' in request.session:
        volunteer=tbl_volunteer.objects.get(id=id)
        volunteer.status=1
        volunteer.save()
        return redirect(volunteer_list)
    else:
        return redirect(login)


# function for deleting Volunteer 
def delete_volunteer(request,id):
    if 'email' in request.session:
        email=request.session['email']
        tbl_volunteer.objects.get(id=id).delete()
        return redirect(volunteer_list)
    else:
        return redirect(login)


# View Individual Volunteer Details 
def volunteer_details(request,id):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_volunteer.objects.get(id=id)
        tbl_volunteer.objects.get(id=id)
        data={'user':user}
        return render(request,"orphanage/volunteer_details.html",data)
    else:
        return redirect(login)

def add_category(request):
    if 'email' in request.session:
        email=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=email)
        if request.method =="POST":
            category=request.POST.get('category')
            tbl_category(orphanage_id=orphanage.id,category=category).save()
            return redirect(Add_Donation)
        user=tbl_orphanage.objects.get(email_id=email)
        data={'user':user}
        return render(request,"orphanage/add_category.html",data)
    else:
        return redirect(login)

# Add Donations
def Add_Donation(request):
    if 'email' in request.session:
        user=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=user)
        if request.method =="POST":

            first_name=request.POST.get('first_name')
            second_name=request.POST.get('second_name')
            third_name=request.POST.get('third_name')
            fourth_name=request.POST.get('fourth_name')

            first_category=request.POST.get('first_category')
            second_category=request.POST.get('second_category')
            third_category=request.POST.get('third_category')
            fourth_category=request.POST.get('fourth_category')


            # for the add other options
            first_other_category=request.POST.get('first_other_category')
            second_other_category=request.POST.get('second_other_category')
            third_other_category=request.POST.get('third_other_category')
            fourth_other_category=request.POST.get('fourth_other_category')

            
            if first_name !='' and first_other_category =='' and second_name =='' and third_name=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()

            elif first_name !='' and first_other_category !='' and second_name =='' and third_name=='' and fourth_name == '' :
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()

            elif first_name=='' and second_name !='' and second_other_category=='' and third_name=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()

            elif first_name=='' and second_name !='' and second_other_category !='' and third_name=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category=='' and third_name=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category!='' and third_name=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()


            elif first_name=='' and second_name =='' and third_name !='' and third_other_category=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()

            elif first_name=='' and second_name =='' and third_name !='' and third_other_category !='' and fourth_name == '':
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category =='' and second_name =='' and third_name !='' and third_other_category =='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()

            elif first_name !='' and first_other_category !='' and second_name =='' and third_name !='' and third_other_category !='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category !='' and second_name =='' and third_name !='' and third_other_category =='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()

            elif first_name !='' and first_other_category =='' and second_name =='' and third_name !='' and third_other_category !='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name=='' and second_name =='' and third_name =='' and fourth_name != '' and fourth_other_category =='':
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()

            elif first_name=='' and second_name =='' and third_name =='' and fourth_name != '' and fourth_other_category !='':
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name =='' and third_name =='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()

            elif first_name !='' and first_other_category!='' and second_name =='' and third_name =='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name !='' and first_other_category!='' and second_name =='' and third_name =='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name =='' and third_name =='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()
                

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category=='' and third_name !='' and third_other_category=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category!='' and third_name !='' and third_other_category!='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category=='' and third_name !='' and third_other_category=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category!='' and third_name !='' and third_other_category=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category=='' and third_name !='' and third_other_category!='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category !='' and second_name !='' and second_other_category !='' and third_name !='' and third_other_category=='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()

            elif first_name !='' and first_other_category !='' and second_name !='' and second_other_category =='' and third_name !='' and third_other_category!='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category =='' and second_name !='' and second_other_category !='' and third_name !='' and third_other_category!='' and fourth_name == '':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category=='' and third_name =='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category!='' and third_name =='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category!='' and third_name =='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category=='' and third_name =='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category!='' and third_name =='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()


            elif first_name !='' and first_other_category=='' and second_name =='' and third_name !='' and third_other_category=='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()

            elif first_name !='' and first_other_category!='' and second_name =='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name !='' and first_other_category!='' and second_name =='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name !='' and first_other_category!='' and second_name =='' and third_name !='' and third_other_category=='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            
            elif first_name !='' and first_other_category=='' and second_name =='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name=='' and second_name !='' and second_other_category=='' and third_name !='' and third_other_category=='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()

            elif first_name=='' and second_name !='' and second_other_category!='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name=='' and second_name !='' and second_other_category!='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()

            elif first_name=='' and second_name !='' and second_other_category!='' and third_name !='' and third_other_category=='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name=='' and second_name !='' and second_other_category=='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

            elif first_name !='' and first_other_category=='' and second_name !='' and second_other_category=='' and third_name !='' and third_other_category=='' and fourth_name != '' and fourth_other_category=='':
                donationtype(orphanage_id=user,name=first_name,category=first_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()

            elif first_name !='' and first_other_category!='' and second_name !='' and second_other_category!='' and third_name !='' and third_other_category!='' and fourth_name != '' and fourth_other_category!='':
                donationtype(orphanage_id=user,name=first_name,category=first_other_category).save()
                donationtype(orphanage_id=user,name=second_name,category=second_other_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_other_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_other_category).save()
                tbl_category(orphanage=orphanage,category=first_other_category).save()
                tbl_category(orphanage=orphanage,category=second_other_category).save()
                tbl_category(orphanage=orphanage,category=third_other_category).save()
                tbl_category(orphanage=orphanage,category=fourth_other_category).save()

# ///////////////////////////////////////////////////////////////////////////////
            elif first_name =='' and second_name !='' and third_name !='' and fourth_name == '':
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
            elif first_name =='' and second_name !='' and third_name =='' and fourth_name != '':
                donationtype(orphanage_id=user,name=second_name,category=second_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()
            elif first_name =='' and second_name =='' and third_name !='' and fourth_name != '':
                donationtype(orphanage_id=user,name=third_name,category=third_category).save()
                donationtype(orphanage_id=user,name=fourth_name,category=fourth_category).save()
            return redirect(View_Item)
        
        category=tbl_category.objects.filter(orphanage_id=orphanage)
        data={'category':category}
        return render(request,"orphanage/Add_Donations.html",data)
    else:
        return redirect(login)


# View category Added By Orphange
def View_category(request):
    if 'email' in request.session:
        user=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=user)
        item=tbl_category.objects.filter(orphanage_id=orphanage.id)
        data={'item':item,
                'user':user
        }
        return render(request,"orphanage/view_category.html",data)
    else:
        return redirect(login)


# Delete category
def delete_category(request,id):
    if 'email' in request.session:
        user=request.session['email']
        item=tbl_category.objects.get(id=id).delete()
        return redirect(View_category)
    else:
        return redirect(login)

# View Items Added By Orphange
def View_Item(request):
    if 'email' in request.session:
        user=request.session['email']
        item=donationtype.objects.filter(orphanage_id=user)
        data={'item':item,
                'user':user
        }
        return render(request,"orphanage/View_Items.html",data)
    else:
        return redirect(login)


# Delete Item
def delete_Item(request,id):
    if 'email' in request.session:
        user=request.session['email']
        item=donationtype.objects.get(id=id).delete()
        return redirect(View_Item)
    else:
        return redirect(login)


from django.db.models import Sum
def View_amount(request):      
    if 'email' in request.session:
        email=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=email)
        amount=tbl_amount_donations.objects.filter(orphanage_id=orphanage.id)
        data=[]
        for i in amount:
            donor = tbl_donor.objects.filter(email_id=i.email_id).first()
            data.append({
                'email': i.email_id,
                'phone': donor.mobile if donor else '',
                'amount': i.amount,
            })
        sum=0
        for i in amount:
            sum=sum+i.amount
        context = {
            'data': data,
            'sum': sum,
        }
        return render(request,'orphanage/view_donation_amout.html', context)
    else:
        return redirect(login)


import csv
from django.http import HttpResponse

def download_donations_csv(request):
    if 'email' in request.session:
        email=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=email)
        amount=tbl_amount_donations.objects.filter(orphanage_id=orphanage.id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="donations.csv"'
        writer = csv.writer(response)
        writer.writerow(['Sl no','Email','amount'])
        total=0
        for i,donation in enumerate(amount,start=1):
            total +=donation.amount
            writer.writerow([i,donation.email_id, donation.amount])
        writer.writerow(['Total Amount','',total])
        return response
    else:
        return redirect(login)

# Add Donations
def Add_Data(request):
    if 'email' in request.session:
        user=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=user)
        if request.method =="POST":
            name=request.POST.get('name')
            mark=request.POST.get('qty')
            marks(orphanage_id=orphanage.id,name=name,mark=mark).save()
            return redirect(View_Data)
        return render(request,"orphanage/Add_Data.html")
    else:
        return redirect(login)


# Upload Marks As CSV
def upload_marks(request):

    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        if not csv_file.name.endswith('.csv'):
            messages.warning(request, 'The uploaded file is not a CSV file.')

            return redirect('Add_Data')

        # Decode the CSV file data and split it into rows
        csv_data = csv_file.read().decode("utf-8").splitlines()

        # Iterate through each row and create Pass_mark objects
       
        for row in csv_data:
            user=request.session['email']
            orphanage=tbl_orphanage.objects.get(email_id=user)
            orphanage_id = orphanage.id
            row_data = row.split(",")
            if len(row_data) != 3:  # Assuming each row has 4 columns
                messages.warning(request, 'Invalid data in CSV file.')
                return redirect('Add_Data')

           
            student, mark1, mark2= row_data
            try:
                student = float(student)
                mark1 = float(mark1)
                mark2 = float(mark2)
            except (ValueError, TypeError):
                messages.warning(request, 'Invalid data in CSV file.')
                print("*********************")

                return redirect('Add_Data')
            user=request.session['email']
            orphanage=tbl_orphanage.objects.get(email_id=user)
            orphanage_id = orphanage.id
            # Assuming that the email in the CSV file is the primary key of the related tbl_login object
            child=marks.objects.filter(student_id=student)
            if child:
                
                messages.success(request,"data already exist")
                return redirect(View_Data)
            else:
                pass_mark = marks(orphanage_id=orphanage_id,student_id=student, mark1=mark1, mark2=mark2)
                pass_mark.save()

            mark = [pass_mark.mark1, pass_mark.mark2]
           
        return redirect('View_Data')


# Function for ploting the graph 
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from django.shortcuts import render
import pandas as pd



def plot_graphs(request,id):
    # Assuming your 'marks' table is stored in a variable named 'marks_list'
    # First, extract the required data from the list of marks
    marks_list=marks.objects.filter(student_id=id)
    mark1_list = [mark.mark1 for mark in marks_list]
    mark2_list = [mark.mark2 for mark in marks_list]
    predicted_pass_list = [mark.predicted_passpercentage for mark in marks_list]
    name_list = [mark.student.fname for mark in marks_list]

    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create a bar plot for mark1
    x = np.arange(len(name_list))
    ax.bar(x, mark1_list, width=0.05, color='#F6451F', label='Mid-term exam1  %')

    # Create a bar plot for mark2
    ax.bar(x + 0.1, mark2_list, width=0.05, color='#31B817', label='Mid-term exam2 exam % ')

    # Create a bar plot for predicted_passpercentage
    ax.bar(x + 0.2, predicted_pass_list, width=0.05, color='#F8EB21', label='Predicted Pass %')

    # Set the x-ticks to the names of the students
    ax.set_xticks(x + 0.1)
    
    # Set the y-label to 'Marks'
    ax.set_ylabel('Percentage')

    # Add a legend
    ax.legend()

    # Save the plot image data to a BytesIO buffer
    buffer = BytesIO()
    fig.savefig(buffer, format='png')

    # Encode the plot image data as a base64 string
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Pass the plot image data as a context variable to the template
    user=marks.objects.filter(student_id=id)
    
    context = {'plot_data': plot_data,'user':user}
    # Render the user page template with the context variables
    return render(request, 'orphanage/performencegraph.html', context)


# View Items Added By Orphange
def View_Data(request):
    if 'email' in request.session:
        user=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=user)
        mark=marks.objects.filter(orphanage_id=orphanage.id)

        from django.db.models import Max, F

        if mark:
            #for retrive the student with highest mark 
            max_mark1 = marks.objects.aggregate(max_mark1=Max('mark1'))['max_mark1']
            student = marks.objects.filter(mark1=max_mark1).first().student
            student = marks.objects.get(student=student)
            data={'mark':mark,
                    'user':user,
                    'student':student
            }
            return render(request,"orphanage/View_Data.html",data)
        else:
            messages.success(request,"No records found.Add new data!")
            return redirect(Add_Data)
    else:
        return redirect(login)

def download_data_csv(request):
    if 'email' in request.session:
        email=request.session['email']
        orphanage=tbl_orphanage.objects.get(email_id=email)
        mark=marks.objects.filter(orphanage_id=orphanage.id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Sl no','Name','Mark1','Mark2'])
        for i,donation in enumerate(mark,start=1):
            writer.writerow([i,donation.name, donation.mark1, donation.mark2])
        return response
    else:
        return redirect(login)

# Delete mark
def delete_data(request,id):
    if 'email' in request.session:
        user=request.session['email']
        mark=marks.objects.get(id=id).delete()
        return redirect(View_Data)
    else:
        return redirect(login)




import matplotlib.pyplot as plt




def donation_graph(request):
    orphanage_donations = tbl_amount_donations.objects.values('orphanage_id__name').annotate(num_donations=Count('id'))
    donation_dict = {}
    for donation in orphanage_donations:
        donation_dict[donation['orphanage_id__name']] = donation['num_donations']
    plt.bar(donation_dict.keys(), donation_dict.values())
    plt.xlabel('Orphanage')
    plt.ylabel('Number of Donations')
    plt.title('Money Donations to Each Orphanage')
    plt.savefig('static/donation_graph.png')
    plt.close()
    return render(request, 'orphanage/donation_graph.html', {'graph_path': '/static/donation_graph.png'})

from datetime import date

def view_donation_item(request):
    if 'email' in request.session:
        email = request.session['email']
        user = tbl_orphanage.objects.get(email_id=email)
        item = donations.objects.filter(orphanage_id=user.id)
        volunteer = tbl_volunteer.objects.filter(orphanage_id=user.id)
        
        data = {'item': item, 'volunteer':volunteer,}
        return render(request, 'orphanage/View_Donation_Item.html', data)
    else:
        return redirect(login)


#downloading pdf of list of items donated
from io import BytesIO
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

def download_donations_pdf(request):
    if 'email' in request.session:
        email = request.session['email']
        user = tbl_orphanage.objects.get(email_id=email)
        item = donations.objects.filter(orphanage_id=user.id)

        # Extract only the necessary data from the donations model
        data = []
        for i in item:
            row = [i.id, i.user_id, i.item, i.donated_date]
            data.append(row)

        # Render the HTML template with the data
        template_path = 'orphanage/pdf_template.html'
        context = {'data': data}
        template = get_template(template_path)
        html = template.render(context)

        # Generate the PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="donations.pdf"'
        buffer = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer)
        if not pdf.err:
            response.write(buffer.getvalue())
            buffer.close()
            return response

        return HttpResponse('Error generating PDF file.', status=500)
    else:
        return redirect(login)




from django.shortcuts import get_object_or_404, redirect, render

from django.contrib import messages

def assign_volunteer(request, donation_id):
    donation = get_object_or_404(donations, id=donation_id)
    volunteer_id = request.POST.get('volunteer_id')
    if volunteer_id:
        volunteer = get_object_or_404(tbl_volunteer, id=volunteer_id)
        AssignedVolunteer.objects.create(donation=donation, volunteer=volunteer)
        volunteer=donations.objects.get(id=donation_id)
        volunteer.status=1
        volunteer.save()
        messages.success(request, 'Volunteer assigned.')
    else:
        messages.error(request, 'Please select a volunteer.')
    return redirect('view_donation_item')

from django.db.models import Q
def leave_list(request):
    if 'email' in request.session:
        email = request.session['email']
        volunteers = tbl_volunteer.objects.filter(Q(tbl_leave__isnull=False) & Q(tbl_leave__status=False)).distinct()
        data = {'volunteers': volunteers}
        return render(request, 'orphanage/leaves_requests.html', data)
    else:
        return redirect(login)


def leave_requests(request, volunteer_id):
    volunteer = get_object_or_404(tbl_volunteer, id=volunteer_id)
    leave_requests = tbl_leave.objects.filter(volunteer=volunteer,status=0)
    return render(request, 'orphanage/volunteer_leave_requests.html', {'volunteer': volunteer, 'leave_requests': leave_requests})



def approve_leave(request, volunteer_id):
    if request.method == 'POST':
        # Get all leave requests for the specified volunteer
        leave_requests = tbl_leave.objects.filter(volunteer__id=volunteer_id)

        # Loop through each leave request and set the status to True
        for leave_request in leave_requests:
            leave_request.status = True
            leave_request.save()

        # Redirect to the leave request list for the volunteer
        return redirect(leave_list)

   
def Accept_leaves(request,id):
    if 'email' in request.session:
        leaves=tbl_leave.objects.get(id=id)
        leaves.status=1
        leaves.save()
        id=leaves.volunteer_id
        return redirect(leave_requests,id)
    else:
        return redirect(login)


def orphanage_Accept_Volunteer_donations(request,id):
    if 'email' in request.session:
        volunteer=donations.objects.get(id=id)
        volunteer.status=1
        volunteer.save()
        return redirect(view_donation_item)
    else:
        return redirect(login)

#      ******************************************* VOLUNTEER MODULE FUNCTIONS ****************************************
#  Load Orphanage  
def load_orphanages(request):
    district_id = request.GET.get('district')
    orphanages = tbl_orphanage.objects.filter(district_id=district_id).order_by('name')
    return render(request, 'volunteer/orphanage_dropdown.html', {'orphanages': orphanages})



# Volunteer Registration Page Function
def Volunteer_Home(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_volunteer.objects.filter(email=email)
        if user:
            user1=tbl_volunteer.objects.get(email=email)
            status=user1.status
            if status == 1:
                data={'email':email,'user':user1}
                return render(request,"volunteer/V-index.html",data)
            else:
                return redirect(volunteer_verification)
        else:
            if request.method == 'POST':
                id=request.POST.get('name')
                email=request.POST.get('email')
                fname=request.POST.get('fname')
                lname=request.POST.get('lname')
                gender=request.POST.get('gender')
                imgs=request.FILES.get('img')
                mobile=request.POST.get('mobile')
                district=request.POST.get('districts')
                city=request.POST.get('city')
                address=request.POST.get('address')
                pin=request.POST.get('pin')
                tbl_volunteer(email_id=email,orphanage_id=id,fname=fname,lname=lname,gender=gender,
                              mobile=mobile,district=district,city=city,address=address,pin=pin,image=imgs).save()
                return redirect(volunteer_verification)
        district=tbl_District.objects.all()
        orphanage=tbl_orphanage.objects.all()

        data={'email':email,
              'district':district,
              'orphanage':orphanage}

        return render(request,"volunteer/V-Registration.html",data)
    else:
        return redirect(login)


# Volunteer Verification Page Function
def volunteer_verification(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.filter(email=email,type=3)
        if user:
            user=tbl_volunteer.objects.filter(email_id=email)
            if user:
                user=tbl_volunteer.objects.get(email_id=email)
                status=user.status
                if status == 0:
                    return render(request,"volunteer/V-Verification.html",{'user':user})
                else:
                    return redirect(Volunteer_Home)
            else:
                    return redirect(Volunteer_Home)
        else:
            messages.success(request,"Request Accepted,Please Login")
            return redirect(login)
    else:
        return redirect(login)
   

# Volunteer Profile Function
def V_Profile(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_volunteer.objects.get(email=email)
        district=tbl_District.objects.all()
        data={'user':user,'district':district,'email':email}
        return render(request, 'volunteer/profile.html',data)
    else:
        return redirect(login)


# Volunteer Profile Edit Function
def V_Profile_edit(request):
    if 'email' in request.session:
        if request.method == 'POST':
            email=request.POST.get('email')
            fname=request.POST.get('fname')
            lname=request.POST.get('lname')
            mobile=request.POST.get('mobile')
            district=request.POST.get('district')
            city=request.POST.get('city')
            address=request.POST.get('address')
            pin=request.POST.get('pin')

            user=tbl_volunteer.objects.get(email=email)
            user.fname=fname
            user.lname=lname
            user.mobile=mobile
            user.district=district
            user.city=city
            user.address=address
            user.pin=pin
            user.save()
            return redirect(V_Profile)
    else:
        return redirect(login)


# Volunteer Orphanage Change Password
def volunteer_change_password(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.get(email=email)
        if request.method =="POST":
            old_password=request.POST.get('oldpss')
            new_password=request.POST.get('pass')
            new_pswd=sha256(new_password.encode()).hexdigest()
            pswd=sha256(old_password.encode()).hexdigest()
            if pswd == user.password:
                user.password=new_pswd
                user.save()
                print("Password updated Successfully")
                messages.success(request, 'Password updated Successfully...')
                return redirect(V_Profile)
            else:
                messages.success(request, 'Incorrect Password ...')
                print("Incorrect Password")
                return redirect(V_Profile)
    else:
        return redirect(login)



def volunteer_viewdonation(request):
    # get the orphanage_id of the volunteer
    if 'email' in request.session:
        email=request.session['email']
        volunteer = tbl_volunteer.objects.get(email=email)
        volunteer_id = volunteer.id

    # filter the donations for the volunteer's orphanage
        donation_list = AssignedVolunteer.objects.filter(volunteer_id=volunteer_id)

        context = {
            'donation_list': donation_list,
            'email':email,
            'user':volunteer,
        }
        return render(request, 'volunteer/volunteer_viewdonations.html', context)

from twilio.rest import Client
def Accept_Volunteer_donations(request,id):
    if 'email' in request.session:
        volunteer=AssignedVolunteer.objects.get(id=id)
        volunteer.status=1
        volunteer.save()

  
        user=volunteer.donation.user_id
        donor=tbl_donor.objects.get(email=user)
        phone_number = donor.mobile
        # set up the Twilio client
        account_sid = 'AC9ef64f85fda39987a64325f9836f51b9'
        auth_token = '866c835cef5bf6a6ea07ab9af894ecd6'
        client = Client(account_sid, auth_token)

        # send the SMS message
        message = client.messages.create(
            to=phone_number,
            from_='+12543554787',
            body='Thank you for your donation! Your donation has been accepted by our volunteer.'
        )

        return redirect(volunteer_viewdonation)
    else:
        return redirect(login)


from django.db import IntegrityError
from datetime import datetime

def apply_leave(request):
    if 'email' in request.session:
        email = request.session['email']
        user = tbl_volunteer.objects.get(email=email)
        district = tbl_District.objects.all()
        # Get the number of leaves taken by the volunteer
        leaves_taken = tbl_leave.objects.filter(volunteer=user.id).count()
        # Calculate the number of leaves left
        leaves_left = 15 - leaves_taken
        if leaves_left < 0:
            leaves_left = 0
        data = {'user':user,'district':district,'email':email,'leaves_left': leaves_left, 'leaves_taken': leaves_taken}
        volunteer = tbl_volunteer.objects.get(email=email)
        if request.method == 'POST':
            if leaves_taken > 15:
                # Prevent user from applying for more leaves
                message = 'Your permitted leaves are over'
                return render(request, 'volunteer/leave_demo.html', {'message': message})
            orphanage = volunteer.orphanage.id
            dates=request.POST.getlist('apply_date')
            for i in dates:     
                date_obj = datetime.strptime(i, '%m/%d/%Y')
                date_formatted = date_obj.strftime('%Y-%m-%d')
                reasons=request.POST.getlist('reason_'+i)
                for reason in reasons:
                    tbl_leave(orphanage_id=orphanage,volunteer_id=volunteer.id,leave_date=date_formatted,reason=reason).save()
            return redirect(volunteer_view_leaves)
        return render(request, 'volunteer/leave_demo.html', data)
    else:
        return redirect('login')




# Delete leave
def delete_leave(request,id):
    if 'email' in request.session:
        user=request.session['email']
        leave=tbl_leave.objects.filter(id=id,status=0).delete()
        return redirect(volunteer_view_leaves)
    else:
        return redirect(login)


def volunteer_view_leaves(request):
    # get the orphanage_id of the volunteer
    if 'email' in request.session:
        email=request.session['email']
        volunteer = tbl_volunteer.objects.get(email=email)
        orphanage_id = volunteer.orphanage.id
        leaves_taken = tbl_leave.objects.filter(volunteer=volunteer.id).count()
        
        # Calculate the number of leaves left
        leaves_left = 15 - leaves_taken
    # filter the donations for the volunteer's orphanage
        leaves = tbl_leave.objects.filter(volunteer_id=volunteer.id)

        context = {
            'leaves': leaves,
            'email':email,
            'user':volunteer,
            'leaves_left': leaves_left,
        }
        return render(request, 'volunteer/volunteer_view_leaves.html', context)

    #      ******************************************* DONOR MODULE FUNCTIONS ****************************************

# Donor Index Page
def Donor_Home(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.get(email=email,type=2)
        data={'user':user}
        return render(request,"donor/D-index.html",data)
    else:
        return redirect(login)

# Donor Profile Page
def D_Profile(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.get(email=email,type=2)
        details=tbl_donor.objects.filter(email_id=email)
        count=details.count()
        data={'user':user,'details':details,'count':count}
        return render(request,"donor/D-profile.html",data)
    else:
        return redirect(login)

# Donor new addresses Page
def D_newaddress_view(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.get(email=email,type=2)
        details=tbl_donor_new_address.objects.filter(email_id=email)
        # count=details.count()
        data={'user':user,'details':details}
        return render(request,"donor/view_address.html",data)
    else:
        return redirect(addnew_address)


# Donor Change Password
def donor_change_password(request):
    if 'email' in request.session:
        email=request.session['email']
        user=tbl_login.objects.get(email=email)
        if request.method =="POST":
            old_password=request.POST.get('oldpss')
            new_password=request.POST.get('pass')
            new_pswd=sha256(new_password.encode()).hexdigest()
            pswd=sha256(old_password.encode()).hexdigest()
            if pswd == user.password:
                user.password=new_pswd
                user.save()
                print("Password updated Successfully")
                messages.success(request, 'Password updated Successfully...')
                return redirect(D_Profile)
            else:
                messages.success(request, 'Incorrect Password ...')
                print("Incorrect Password")
                return redirect(D_Profile)
    else:
        return redirect(login)


# Donor  Details Add Function
def Donor_details(request):
    if 'email' in request.session:
        if request.method == 'POST':
            email=request.POST.get('email')
            fname=request.POST.get('fname')
            lname=request.POST.get('lname')
            mobile=request.POST.get('mobile')
            district=request.POST.get('district')
            city=request.POST.get('city')
            address=request.POST.get('address')
            pin=request.POST.get('pin')
            tbl_donor(email_id=email,fname=fname,lname=lname,mobile=mobile,district=district,city=city,address=address,pin=pin).save()
            return redirect(D_Profile)
        return redirect(D_Profile)


# Donor  new address Add Function
def addnew_address(request):
        if request.method == 'POST':
            fname=request.POST.get('fname')
            lname=request.POST.get('lname')
            mobile=request.POST.get('mobile')
            district=request.POST.get('district')
            city=request.POST.get('city')
            address=request.POST.get('address')
            pin=request.POST.get('pin')
            print(fname,"********************")
            if 'email' in request.session:
                user=request.session['email']
                reg=tbl_donor_new_address(fname=fname,lname=lname,mobile=mobile,district=district,city=city,address=address,pin=pin,email_id=user)
                reg.save()
                return redirect(D_newaddress_view)
        return render(request, 'donor/addnew_address.html')
        


# Donor  Details Add Function
def Delete_details(request,id):
    if 'email' in request.session:
        email=request.POST.get('email')
        tbl_donor.objects.get(id=id).delete()
        return redirect(D_Profile)
    else:
        return redirect(login)


# Select Orphanage Function
def selectdistrict(request):
    if 'email' in request.session:
        if request.method == 'POST':
            orphanage_id=request.POST.get('orphanage')
            email=request.session['email']
            amount=request.POST.get('amount')
            user=tbl_login.objects.get(email=email)
            orphanage=tbl_orphanage.objects.get(id=orphanage_id)
            tbl_amount_donations(orphanage_id=orphanage_id,amount=amount,email_id=email).save() 
            return redirect(orphanage_details)
        district= tbl_District.objects.all()
        email=request.session['email']
        user=tbl_login.objects.get(email=email)
        d = {'district': district,'name':email,'user':user}
        return render(request,'donor/selectdistrict.html',d)
    else:
        return redirect(login)

# Donor  View Orphanage For Donation
def orphanage_details(request):
    if 'email' in request.session:
        email=request.session['email']
        data=tbl_amount_donations.objects.filter(email=email,status=0)
        total=0
        for i in data:
            total=total+i.amount
        amount=total * 100
        content={'total':total,'data':data,'amount':amount}
        return render(request,"donor/vieworphanage.html",content)
    else:
        return redirect(login)

def payment_done(request):
    if 'email' in request.session:
        email=request.session['email']
        orp = tbl_amount_donations.objects.filter(email=email,status=0)
        # item = Product.objects.get(product=product, id=item_id)
        for o in orp:
            o.status=1
            o.save()
            messages.success(request,"payed successfully")
        return redirect(selectdistrict)
    else:
        return redirect(login)

# orphanage donated amount delete Function
def Delete_orphanage(request,id):
    if 'email' in request.session:
        email=request.POST.get('email')
        tbl_amount_donations.objects.get(id=id).delete()
        return redirect(orphanage_details)
    else:
        return redirect(login)


from django.db.models import Sum
def D_View_amount(request):      
    if 'email' in request.session:
        email=request.session['email']
        # user=tbl_login.objects.get(email=email)
        amount=tbl_amount_donations.objects.filter(email_id=email)
        sum=0
        for i in amount:
            sum=sum+i.amount
        data={'amount':amount,
                'sum':sum,}
        return render(request,'donor/D_view_donation_amout.html',data)
    else:
        return redirect(login)


def selectdistrict_items(request):
    district= tbl_District.objects.all()
    email=request.session['email']
    d = {'district': district,'name':email}
    return render(request,'donor/selectdistrict_items.html',d)

def load_orphanages_items(request):
    district_id = request.GET.get('district')
    orphanages = tbl_orphanage.objects.filter(district_id=district_id).order_by('name')
    return render(request, 'donor/orphanage_dropdown_list_options.html', {'orphanages': orphanages})


def orphanage_details_items(request):
     if request.method == 'POST':
        district_id = request.POST.get('district')
        orphanage_id = request.POST.get('orphanage')
        orphanage = tbl_orphanage.objects.filter(id=orphanage_id, district_id=district_id)
        context = {'orphanage': orphanage}
        return render(request, 'donor/orphanage_details_items.html', context)


def donation_items_save(request):
    if request.method == 'POST':
        opid=request.POST.get('opid')
        item=request.POST.get('item') 
        other=request.POST.get('other') 
        date=request.POST.get('date')
        address=request.POST.get('radio')
        print(address)
        print(date)
        print("**************************")
        if 'email' in request.session:
            user=request.session['email']
            donation=donations(item=item,otherdonations=other,date=date,orphanage_id=opid,address_id=address,user_id=user)
            donation.save()
            messages.success(request,"Donated successfully")
            return redirect(selectdistrict_items)
        return render(request, 'donor/donate_items.html')
        


def donate_items(request,id):
    orphanage=tbl_orphanage.objects.get(id=id)
    items=donationtype.objects.filter(orphanage_id=orphanage.email_id)
    email=request.session['email']
    address=tbl_donor_new_address.objects.filter(email_id=email)
    id=tbl_donor_new_address.objects.all()
    return render(request, 'donor/donate_items.html',{'items':items,'name':email,'orphanage':orphanage,'address':address,'id':id})


def donor_viewdonations(request):
    if 'email' in request.session:
        email=request.session['email']
        user_donations = donations.objects.filter(user_id=email)
        return render(request, 'donor/donor_viewdonations.html', {'user_donations': user_donations})



# Function for analysing the donations in admin
def donation_analysys(request):
    type1 = request.GET.get('category_option')
    type2 = request.GET.get('single_option')
    type3 = request.GET.get('custom_option')
    orphanage = request.GET.get('orphanage')
    sinle_date = request.GET.get('single_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if orphanage == '1000' :
        orders = tbl_amount_donations.objects.all()
    else:
        orders = tbl_amount_donations.objects.filter(orphanage_id=orphanage)


    product_data = {}
    for order in orders:
        product_name = order.orphanage.name
        product_total = order.amount
        if product_name in product_data:
            product_data[product_name]['quantity'] += order.amount
            product_data[product_name]['total'] += product_total
        else:
            product_data[product_name] = {
                'quantity': order.amount,
                'total': product_total,
            }

    data = []
    for name, values in product_data.items():
        data.append({
            'name': name,
            'quantity': values['quantity'],
            'total': values['total'],
        })

    total_sales = sum([item['total'] for item in data])
    datas=1
    orphanage=tbl_orphanage.objects.all()
    context = {
        'product_data': data,
        'total_sales': total_sales,
        'data':datas,
        'orphanage':orphanage,
    }
    return render(request, 'donation_analysis.html', context) 


    
def orpanage_donation_analysys(request):
    if 'email' in request.session:
        user=request.session['email']
        user=tbl_orphanage.objects.get(email_id=user)
        type1 = request.GET.get('category_option')
        type2 = request.GET.get('single_option')
        type3 = request.GET.get('custom_option')
        orphanage = request.GET.get('orphanage')
        sinle_date = request.GET.get('single_date')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
       
        orders = tbl_amount_donations.objects.filter(orphanage_id=user)
      
        product_data = {}
        for order in orders:
            product_name = order.email_id
            product_total = order.amount
            if product_name in product_data:
                product_data[product_name]['quantity'] += order.amount
                product_data[product_name]['total'] += product_total
            else:
                product_data[product_name] = {
                    'quantity': order.amount,
                    'total': product_total,
                }

        data = []
        for name, values in product_data.items():
            data.append({
                'name': name,
                'quantity': values['quantity'],
                'total': values['total'],
            })

        total_sales = sum([item['total'] for item in data])
        datas=1
        orphanage=tbl_orphanage.objects.all()
        context = {
            'product_data': data,
            'total_sales': total_sales,
            'data':datas,
            'orphanage':orphanage,
        }
        return render(request, 'orphanage/Orphanage_Donation_Analysys.html', context) 
    else:
        return redirect(login)