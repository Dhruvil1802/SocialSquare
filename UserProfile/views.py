from datetime import datetime,timedelta
from itertools import chain
from multiprocessing import context
from operator import attrgetter
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from requests import request

from django.core import mail
import smtplib
import random

from Posts.models import Comments, Like, UserPost
from UserProfile.helpers import  notifications, post_analytics,  requested_user_profile,  user_liked_post

# Create your views here.
from .models import  UserActivity,UserProfile
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone

from django.shortcuts import get_object_or_404

# This view get the data of profile for both user and and other users and redirect it to showuserprofile.html
class ShowUserProfile(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            user=UserProfile()
            email = request.session['email']
            user= UserProfile.objects.get(email = email)
            user_post = []
            liked_posts = []

            # profile data of other users
            if request.GET.get('requested_user_id') and str(user.user_id) != request.GET.get('requested_user_id') :
                requested_user_id = request.GET.get('requested_user_id')
                requested_user = UserProfile.objects.get(user_id = requested_user_id)
                user_connection,requested_user_connection,requested_user_post, requested_user_post_id = requested_user_profile(user,requested_user.user_id)
                liked_posts = user_liked_post(requested_user_post_id,user)
                print(user_connection,requested_user_connection,requested_user_post,requested_user_post_id)
                return render(request,'showuserprofile.html',{'uc':user_connection,'ruc':requested_user_connection,"requested_user_post":requested_user_post,"liked_post":liked_posts,"currentpage":"showuserprofile"})

            #profile data of user
            if UserPost.objects.filter(user = user.user_id).exists():
                user_post = UserPost.objects.filter(user = user.user_id).values
                user_post_id = UserPost.objects.filter(user = user.user_id).values("post_id")
                liked_posts = user_liked_post(user_post_id,user)

                        
            return render(request,'showuserprofile.html',{"user":user, 'user_post':user_post,"liked_post":liked_posts,"currentpage":"showuserprofile"})
        except Exception as ex:
            print(ex)

# This view gets the previous active time from html with the help of ajax and store it in the database
def save_active_time(request):
    if request.method == 'POST':
        try:
            active_time = request.POST.get('activeTime')
            email = request.session['email']
            user= UserProfile.objects.get(email = email)    
            user_activity = UserActivity()
            user_activity.active_time = active_time
            user_activity.user = user
            user_activity.save()

            return JsonResponse({'success': True})
        except Exception as ex:
            print(ex)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})

# This view collect the updates about user profile like new likes, comments and follow request and then sort it on the basis of updated_at
class Notification(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
            notification_list = notifications(user)
            return render(request, 'notification.html',{"notification_list":notification_list,"currentpage":"notifications"})
        except Exception as ex:
                print(ex)

# This view get the data from different models and convert it in the list for graphical representation
class UserInsights(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            user = UserProfile.objects.get(email = email)
            likes_list = [0]
            post_list = [0]
            comments_list = [0]

            # check that user want to see data related to post_analytics
            if request.GET.get("user_activity_option") == "post_analytics":

                likes_list,post_list,comments_list,user =post_analytics(likes_list,post_list,comments_list,user)

                return render(request,'userinsights.html',{"comments_list":comments_list,"post_list":post_list,"likes_list":likes_list,"currentpage":"userinsights"})
        
            if request.GET.get("start_time") and request.GET.get("end_time"):
                start_time = request.GET.get("start_time")
                end_time = request.GET.get("end_time")
                global followercount
                followercount = user.follower_count

                # unit = "seconds"
                if start_time != None and end_time != None:

                    date_str = start_time
                    date_format = '%Y-%m-%d'
                    start_time_obj = datetime.strptime(date_str, date_format)

                    date_str = end_time
                    date_format = '%Y-%m-%d'
                    end_time_obj = datetime.strptime(date_str, date_format)

                    next_day = start_time_obj + timedelta(days=1)

                    user_activity_per_day=[0]
                    user_activity_on_day=[0]
                    unit = "seconds"
                    follower_count = [0]
                    follower_count_on_day=[0]
                    
                                
                    
                    while start_time_obj<=end_time_obj:
                        
                        total_time=0
                        #getting user activity per day
                        if request.GET.get("user_activity_option") == "time_spent":

                                day_activity = UserActivity.objects.filter(user = user, updated_at__range = [start_time_obj,next_day])
                                total_miliseconds=0
                                for i in day_activity:
                                    total_miliseconds = total_miliseconds + i.active_time

                                total_time = str(round(total_miliseconds/60000))
                                unit = "minutes"

                            
                                user_activity_per_day.append(int(total_time))
                                user_activity_on_day.append(int(start_time_obj.day))
                        
                        #getting data related to connections
                        if request.GET.get("user_activity_option") == "connection_analytics":
                            instance = get_object_or_404(UserProfile, user_id=user.user_id)
                            if instance.history.filter(history_date__range = [start_time_obj,next_day]).exists():
                                historical_records = instance.history.filter(history_date__range = [start_time_obj,next_day])
                                followercount = historical_records[0].follower_count

                            follower_count.append(followercount)
                            follower_count_on_day.append(start_time_obj.day)

                        start_time_obj += timedelta(days=1)  
                        next_day += timedelta(days=1)
                    

                    return render(request,'userinsights.html',{"follower_count":follower_count,"follower_count_on_day":follower_count_on_day,"unit":unit,"user_activity_on_day":user_activity_on_day,"user_activity_per_day":user_activity_per_day,"currentpage":"userinsights"})
                return render(request,'userinsights.html',{"currentpage":"userinsights"})
            else:
                return render(request,'userinsights.html',{"message":"some required fields are missing"})
        except Exception as ex:
            print(ex)

class UpdateProfile(View):
    def get(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            user=UserProfile()
            user= UserProfile.objects.get(email = email)
            return render(request,'editprofile.html',{"user":user}) 
        except Exception as ex:
            print(ex)

#this view get the new data enter by user in updateproile and update it in the database
class ProfileData(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
            
            if "username" in request.POST: 
                username = request.POST.get('username')
                user.username = username
            if "bio" in request.POST:
                bio = request.POST.get('bio')
                user.bio = bio
            if "account_type" in request.POST:
                account_type = request.POST.get('account_type')
                if account_type == 'public':
                    is_private = False
                if account_type == 'private':
                    is_private = True     
                user.is_private = is_private      
            if "profile_pic" in request.FILES:
                profile_pic = request.FILES["profile_pic"]
                user.profile_pic = profile_pic

            user.save()

            redirect_url = f'../../UserProfile/showuserprofile/'
            return redirect(redirect_url)
                      
        except Exception as ex:
            print(ex)

