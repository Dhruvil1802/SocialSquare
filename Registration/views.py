from datetime import datetime,timedelta
from itertools import chain
from multiprocessing import context
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from requests import request

from django.core import mail
import smtplib
import random

from Connections.models import UserConnection
from Posts.models import Like, UserPost


# Create your views here.
from .models import UserProfile
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone

from django.shortcuts import get_object_or_404





# render to registration.html
def registerhere(request):
    return render(request, 'registration.html')   

# render to login.html
def login(request):
     message = request.GET.get('message')
     return render(request, 'login.html',{"message": message})   

# render to upadatepassword.html
def updatepassword(request):
    return render(request, 'updatepassword.html') 


# this view get the data from registration.html and save it in the database
class Registration(View):

    @csrf_exempt
    def post(self,request):
        try:
            if "username" not in request.POST or "password" not in request.POST or "email" not in request.POST :
                return render(request, 'registration.html',{"message":"some required fields are missing"})
            
            username = request.POST.get('username')
            password = request.POST.get('password')
            email    = request.POST.get('email')

            if UserProfile.objects.filter(email = email).exists():
                return render(request, 'registration.html',{"message":"user is already registered"})
            else:                  
                registration = UserProfile()
                registration.username = username
                registration.password = password
                registration.email = email

                if "date_of_birth" not in request.POST:
                    date_of_birth = request.POST.get('date_of_birth')
                    registration.date_of_birth = date_of_birth
                if "bio" not in request.POST:    
                    bio = request.POST.get('bio')
                    registration.bio = bio
                if "account_type" in request.POST:
                    account_type = request.POST.get('account_type')
                    if account_type == 'public':
                        is_private = False
                    if account_type == 'private':
                        is_private = True     
                    registration.is_private = is_private 
                if "profile_pic" in request.FILES:
                    profile_pic = request.FILES["profile_pic"]
                    registration.profile_pic = profile_pic
                registration.save()
                return redirect(login)     
        except Exception as ex:
            print(ex)

# render to forgotpassword.html and get the email from the user
def forgotpassword(request):
    message = request.GET.get('message')

    return render(request, 'forgotpassword.html',{"message": message})
       
# this view fetch the email address, checks that it exists in database or not then generate otp send the otp on that email address as well as stor it in the session
class SendOTP(View):
    @csrf_exempt
    def post(self,request):
        try:
            email = request.POST.get('email')
            if email == '':
                redirect_url = f'../../Registration/forgotpassword/?message=some required fields are missing'
                return redirect(redirect_url)
            request.session["email_for_otpverification"] = email
            
            if UserProfile.objects.filter(email = email).exists():

                otp = str(random.randint(1000, 9999))
                request.session['otp'] = otp

                with mail.get_connection() as connection:
                  mail.EmailMessage(
                    "OTP verification for password change",
                    otp,
                    "dhruvilphotos06@gmail.com",
                    [email],
                    connection=connection,).send()
                return render(request, 'otpverification.html')
            else:
                redirect_url = f'../../Registration/login/?message=user does not exists'
                return redirect(redirect_url)
        except Exception as ex:
            print(ex)

# fetch the otp entered by user, compare it to the otp stored in the session and if they matches then user is allowed to reset his password
def editpassword(request):
    otp = request.GET.get('otp')
    saved_otp = request.session['otp'] 
    if otp == "":
        return render(request, 'otpverification.html',{"message":"some required fields are missing"})

    if otp==saved_otp:
        return render(request, 'editpassword.html')
    

# fetch the new_password from editpassword.html and update the password in the UserProfile model
class UpdatePassword(View):
    @csrf_exempt
    def post(self,request):
        try:
            email = request.session["email_for_otpverification"]
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get("confirm_password")
            if new_password == "" or confirm_password=="":
                redirect_url = f'../../Registration/editpassword/?message=some required fields are missing'
                return redirect(redirect_url)
                #return render(request, 'editpassword.html',{"message":"passwords doesn't match"})
            if new_password !=confirm_password:
                redirect_url = f'../../Registration/editpassword/?message=some required fields are missing'
                return redirect(redirect_url)
                #return render(request, 'editpassword.html',{"message":"passwords doesn't match"})
            user_profile = UserProfile.objects.get(email = email)
            user_profile.password = new_password
            user_profile.save()
                
            redirect_url = f'../../Registration/login/?message=password updated'
            return redirect(redirect_url)
            #return render(request, 'login.html',context={"message":"password updated"})
        except Exception as ex:
            print(ex)
            
# render to resetpassword.html
class resetpassword(View):
    @csrf_exempt
    def get(self,request):
      try:
        if 'email' in request.session:
                    email = request.session['email']
        else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
        return render(request, 'resetpassword.html')
      except Exception as ex:
            print(ex)
    
# fetch the email and password from resetpassword.html and update it in the UserProfile model
class CheckCredentials(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            password = request.POST.get('old_password')
            email = request.POST.get('email')
            new_password = request.POST.get('new_password')
            if password == "" or email == "" or new_password == "":
                redirect_url = f'../../Registration/resetpassword/?message=some required fields are missing'
                return redirect(redirect_url)
            
            if UserProfile.objects.filter(email = email, password = password).exists():
                user_profile = UserProfile.objects.get(email = email)
                user_profile.password = new_password
                user_profile.save()
                redirect_url = f'../../Registration/login/?message=password updated'
                return redirect(redirect_url)
            
            else:
                redirect_url = f'../../Registration/resetpassword/?message=wrong credentials'
                return redirect(redirect_url)

        except Exception as ex:
            print(ex)
            
# fetch the credentials from login.html and redirect to the homepage     
class LoginCredentials(View):
    @csrf_exempt
    def post(self,request):
        try:
            password = request.POST.get('password')
            email = request.POST.get('email')

            if password =="" or email =="":
                redirect_url = f'../../Registration/login/?message=some required fields are missing'
                return redirect(redirect_url)

            if UserProfile.objects.filter(email = email, password = password).exists():
                request.session['email'] = email
                redirect_url = f'../../Posts/homepage/'
                return redirect(redirect_url)      
                      
            else:
                return redirect('../login/?message=wrong+credentials')
            
        except Exception as ex:
            print(ex)

# delet the email stored in session for logout 
class Logout(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            del request.session['email']
            return redirect('../login/?message=logout+successfully')
            #return render(request, 'login.html',context={"message":"logedout successfully"})
        except Exception as ex:
            print(ex)
