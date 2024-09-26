

from datetime import datetime, timedelta
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

from Posts.models import UserPost

from .helpers import accept_request, block, cancel_request, decline_request, follow_request, get_follower, get_following,  pending_requests_profiles, remove_follower, suggested_profiles, unblock, unfollow

from .models import UserConnection, UserProfile
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone

from django.shortcuts import get_object_or_404

import requests
from django.http import HttpResponse

# when user hit the follow button, this view fetch the requested_user_id
#if the requested user is private then it will send the follow request to the user and if the requested user is not private then he will be automatically followed by user
class FollowRequest(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
                #return render(request, 'login.html',context={"message":"you are not logedin"})
            user= UserProfile.objects.get(email = email)

            requested_user_id = request.POST.get("requested_user_id")
            requested_user= UserProfile.objects.get(user_id = requested_user_id)
            is_private = request.POST.get("is_private")

            follow_request(user,requested_user,is_private)

            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)
            
            if request.POST.get('name') == 'suggestions':
                redirect_url = f'../../Connections/suggestions/'
                return redirect(redirect_url)
                
            if request.POST.get('name') == 'follow back':
                redirect_url = f'../../Connections/getfollowers/?user={user.user_id}'
                return redirect(redirect_url)
    
        except Exception as ex:
            print(ex)

# This view fetch all the users from the connection model who sent request to the user and then this data will be sent to pendingrequest.html
class PendingRequest(View):
    @csrf_exempt
    def get(self,request): 
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
            pending_requests = pending_requests_profiles(user)

            return render(request, 'pendingrequests.html',{"pending_requests":pending_requests, "currentpage":"pendingrequests"})
        except Exception as ex:
            print(ex)

# whenever user accept someone's request, this view is called and it will increase 1 follower of user and 1 following of request_sender
class AcceptRequest(View):
    @csrf_exempt
    def post(self,request):
        try:
            
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)

            follower_id = request.POST.get("requested_user_id")
            follower= UserProfile.objects.get(user_id = follower_id)

            accept_request(user,follower)

            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)
            
            if request.POST.get('requested_user_id') and request.POST.get('notification') == "notification":
                redirect_url = f'../../UserProfile/notification/'
                return redirect(redirect_url)
               
            redirect_url = f'../../Connections/pendingrequests/?user={user}'
            return redirect(redirect_url)

        except Exception as ex:
            print(ex)

# when user hit the decline button, this view is called and it fetch the user connection between user and request_sender and set the is_requested field to false
class DeclineRequest(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            requested_user_id = request.POST.get("requested_user_id")

            decline_request(email,requested_user_id)

            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)   
            
            redirect_url = f'../../Connections/pendingrequests/'
            return redirect(redirect_url)

        except Exception as ex:
            print(ex)

# this view fetch all the followers of the users and send them to following-follower.html
class GetFollowers(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
           
            user_id = request.GET.get('user') 
            user= UserProfile.objects.get(user_id = user_id)
            followers,fl,requested_private_user = get_follower(user)

            return render(request, 'follower-following.html' ,{"followers":followers,"following":fl,"requested_private_user":requested_private_user,"flag":"follower"})
        except Exception as ex:
            print(ex)

# this view fetch all the followings of the users and send them to following-follower.html
class GetFollowing(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            user_id = request.GET.get('user') 
            user= UserProfile.objects.get(user_id = user_id)
            followers,following = get_following(user)
            following = UserConnection.objects.filter(user=user, request_status=True)

            return render(request, 'follower-following.html' ,{"followers":followers,"following":following,"flag":"following"})
        except Exception as ex:
            print(ex)
        
# when user hit unfollow button this view is called and it removes 1 following from user and 1 follower from unfollowed_user
class UnFollow(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            

            requested_user_id = request.POST.get("requested_user_id")
            unfollow(email,requested_user_id)
            
            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)   

            user= UserProfile.objects.get(email = email)
            redirect_url = f'../../Connections/getfollowing/?user={user.user_id}' 
            return redirect(redirect_url) 
            # followers,following = get_following(user)
            # return render(request, 'follower-following.html' ,{"followers":followers,"following":following,"flag":"following"})
        except Exception as ex:
            print(ex)

# this view fetch all other users profile from UserProfile model and show it on the suggestions.html
class suggestions(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)

            suggestions, requested_private_user = suggested_profiles(user)
            
            return render(request,'suggestions.html',{"suggestions":suggestions,"requested_private_user":requested_private_user,"currentpage":"suggestions"})
        except Exception as ex:
            print(ex)


# when user removes any follower, this method is called and it will deduct 1 follower of user and deduct 1 following from that follower 
class RemoveFollower(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)

            requested_user_id = request.POST.get("requested_user_id")

            remove_follower(email,requested_user_id)

            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
            redirect_url = f'../../Connections/getfollowers/?user={user.user_id}' 
            return redirect(redirect_url)
        
        except Exception as ex:
            print(ex)

# when user already sent follow request to someone then he has an option to cancel that requestand when he hits cancel request button then the this fetch the userconnection data having both this users and set "is_requested" field to false
class CancelRequest(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            
            requested_user_id = request.POST.get("requested_user_id")
            cancel_request(email,requested_user_id)

            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)
            
            if request.POST.get('name') == 'suggestions':

                redirect_url = f'../../Connections/suggestions/'
                return redirect(redirect_url)
            
            if request.POST.get('name') == 'follow back':

                user= UserProfile.objects.get(email = email)
                redirect_url = f'../../Connections/getfollowers/?user={user.user_id}'
                return redirect(redirect_url)
        except Exception as ex:
            print(ex)

# if user blocked someone then this view will set "is_blocked" field from userconnection to true
class Block(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            
            requested_user_id = request.POST.get("requested_user_id")
            block(email,requested_user_id)

            redirect_url = f'../../UserProfile/showuserprofile/'
            return redirect(redirect_url)
        except Exception as ex:
            print(ex)

# this view fetch all the users whose is_blocked field is already true in userconnection with user
class BlockedUsers(View):
     @csrf_exempt
     def get(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
               
            blocked_user_connection = UserConnection.objects.filter(is_blocked=True, user = user)
            print(blocked_user_connection)
        
            return render(request,'blockedusers.html',{'blocked_user_connection':blocked_user_connection}) 
        except Exception as ex:
            print(ex)

# when user wants to unblock any blocked user then this view is called which sets 'is_blocked' field of userconnection to false
class UnBlock(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                email = request.session['email']
            else:
                redirect_url = f'../../Registration/login/?message=you are not logedin'
                return redirect(redirect_url)
            
            requeste_user_id = request.POST.get("requested_user_id")
            unblock(email,requeste_user_id)

            if request.POST.get('requested_user_id') and request.POST.get("requested_user_profile")=="requested_user_profile":
                requested_user_id = request.POST.get('requested_user_id')
                redirect_url = f'../../UserProfile/showuserprofile/?requested_user_id={requested_user_id}'
                return redirect(redirect_url)

            redirect_url = f'../../Connections/blockeduser/'
            return redirect(redirect_url)
            # return render(request,'blockedusers.html',{'blocked_user_connection':blocked_user_connection}) 

        except Exception as ex:
            print(ex)

