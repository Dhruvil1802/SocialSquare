from django.utils import timezone
from itertools import chain
from operator import attrgetter
from Connections.models import UserConnection
from Posts.models import Comments, Like, UserPost
from UserProfile.models import  UserProfile
from multiprocessing import context
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from requests import request
from django.db.models import Q

from UserProfile.views import Notification

def suggested_profiles(user):
        try:
            blocked_user =  UserConnection.objects.filter(Q(is_blocked=True,user=user.user_id)).values_list("requested_user")
            requested_user_ids=UserConnection.objects.filter(Q(request_status=True,user=user.user_id)).values_list("requested_user")

            user_blocked_by = UserConnection.objects.filter(Q(requested_user=user.user_id, is_blocked=True)).values_list("user")
            requested_private_user=UserConnection.objects.filter(Q(is_requested=True) ,Q(user=user.user_id)).values_list("requested_user")
            suggestions = UserProfile.objects.exclude(Q(user_id__in=requested_user_ids) | Q(user_id__in=user_blocked_by) | Q(user_id__in=blocked_user) | Q(user_id=user.user_id)).order_by('follower_count')
            rpu=[]
            for f in requested_private_user:
                 rpu.append(f[0])
            return suggestions, rpu
        except Exception as ex:
            print(ex)

def pending_requests_profiles(user):
        try:
            pending_requests = UserConnection.objects.filter(requested_user=user, is_requested=True, request_status=False)
            return pending_requests
        except Exception as ex:
            print(ex)

def get_follower(user):
        followers = UserConnection.objects.filter(requested_user=user, request_status=True)
        following = UserConnection.objects.filter(user=user, request_status=True).values_list('requested_user')
        requested_private_user=UserConnection.objects.filter(Q(is_requested=True) ,Q(user=user.user_id)).values_list("requested_user")
        rpu=[]
        for r in requested_private_user:
            rpu.append(r[0])
        fl=[]
        for f in following:
            fl.append(f[0])
        return followers,fl,rpu

def get_following(user):
        followers = UserConnection.objects.filter(requested_user=user, request_status=True, is_requested=False)
        following = UserConnection.objects.filter(user=user, request_status=True)
        
        return followers,following


def connection_requests_profiles(user):
        try:

            accepted_requests = UserConnection.objects.filter(requested_user=user)
            return accepted_requests
        except Exception as ex:
            print(ex)

      
def follow_request(user,requested_user,is_private):
            user_connection=None
            if UserConnection.objects.filter(user=user,requested_user=requested_user).exists():
                user_connection = UserConnection.objects.get(user=user,requested_user=requested_user)

            else:
                user_connection = UserConnection()

            if UserConnection.objects.filter(user=requested_user,requested_user=user).exists():
                pass
            else:
                requested_user_connection = UserConnection()
                requested_user_connection.user = requested_user
                requested_user_connection.requested_user = user
                requested_user_connection.save()
           
            user_connection.user = user
            user_connection.requested_user = requested_user
            user_connection.is_requested = True
           
            
            if is_private=='False':
                user_connection.request_status = True
                user_connection.is_requested = False
                user.following_count= user.following_count + 1
                requested_user.follower_count = requested_user.follower_count + 1
                if requested_user.follower_count>=1000:
                    requested_user.is_verified = True
                requested_user.save()
                user.save() 
            user_connection.save()
           

def accept_request(user,follower):
            user_connection = UserConnection.objects.get(user= follower ,requested_user = user)
            user_connection.request_status = True
            user_connection.is_requested = False
            user_connection.save()
            user.follower_count = user.follower_count + 1
            if user.follower_count >= 1000:
                  user.is_verified = True
            follower.following_count = follower.following_count + 1
            follower.save()
            user.save()

def decline_request(email,requested_user_id):
        user= UserProfile.objects.get(email = email) 
        requested_user= UserProfile.objects.get(user_id = requested_user_id)

        user_connection = UserConnection.objects.get(user= requested_user ,requested_user = user)
        user_connection.is_requested = False
        user_connection.save()
  
def unfollow(email,requested_user_id):
        
        user= UserProfile.objects.get(email = email)
        if UserProfile.objects.filter(user_id = requested_user_id).exists():
            requested_user= UserProfile.objects.get(user_id = requested_user_id)

        if UserConnection.objects.filter(requested_user=requested_user, user = user, request_status=True).exists():
                user_connection = UserConnection.objects.get(requested_user=requested_user, user = user, request_status=True)
                user_connection.request_status = False
                user_connection.is_requested = False
                user_connection.save()

        user.following_count= user.following_count - 1
        requested_user.follower_count = requested_user.follower_count - 1
        if requested_user.follower_count<1000:
              requested_user.is_verified = False
        user.save() 
        requested_user.save()

def remove_follower(email,requested_user_id):
            user= UserProfile.objects.get(email = email)
            if UserProfile.objects.filter(user_id = requested_user_id).exists():
                requested_user= UserProfile.objects.get(user_id = requested_user_id)
            if UserConnection.objects.filter(requested_user=user, user = requested_user, request_status=True).exists():
                follower = UserConnection.objects.get(requested_user=user, user = requested_user, request_status=True)
                follower.request_status = False
                follower.is_requested = False
                follower.save()

            requested_user.following_count = requested_user.following_count - 1
            user.follower_count = user.follower_count - 1
            if user.follower_count<1000:
               user.is_verified = False
            user.save() 
            requested_user.save()
      
def cancel_request(email,requested_user_id):
            user= UserProfile.objects.get(email = email)
            requested_user= UserProfile.objects.get(user_id = requested_user_id)

            if UserConnection.objects.filter(requested_user=requested_user, user = user, is_requested=True).exists():
                user_connection = UserConnection.objects.get(requested_user=requested_user, user = user, is_requested=True)
                user_connection.request_status = False
                user_connection.is_requested = False
                user_connection.save()

def block(email,requested_user_id):
            user= UserProfile.objects.get(email = email)
            requested_user= UserProfile.objects.get(user_id = requested_user_id)
            if UserConnection.objects.filter(requested_user=requested_user, user=user).exists():
                user_connection = UserConnection.objects.get(requested_user=requested_user, user = user)
                if user_connection.request_status == True:
                    user.following_count= user.following_count - 1
                    requested_user.follower_count = requested_user.follower_count - 1
                    user_connection.request_status = False
                    

                user_connection.is_requested = False
                user_connection.is_blocked = True
                user_connection.save()
            else:
                user_connection = UserConnection()
                user_connection.user = user
                user_connection.requested_user = requested_user
                user_connection.is_blocked = True
                user_connection.save()


            if UserConnection.objects.filter(requested_user=user, user = requested_user).exists():
                requested_user_connection = UserConnection.objects.get(requested_user=user, user = requested_user)
                if requested_user_connection.request_status == True:
                    requested_user.following_count= requested_user.following_count - 1
                    user.follower_count = user.follower_count - 1
                    requested_user_connection.request_status = False
                requested_user_connection.is_requested = False
                requested_user_connection.save()
            else:
                requested_user_connection = UserConnection()
                requested_user_connection.user = requested_user
                requested_user_connection.requested_user = user
                requested_user_connection.is_blocked = False
                requested_user_connection.save()

            user.save() 
            requested_user.save()

def unblock(email,requeste_user_id):
            user= UserProfile.objects.get(email = email)

            
            if UserProfile.objects.filter(user_id = requeste_user_id).exists():
                requested_user= UserProfile.objects.get(user_id = requeste_user_id)
           
            if UserConnection.objects.filter(requested_user=requested_user, user=user).exists():
               
                user_connection = UserConnection.objects.get(requested_user=requested_user, user = user)
                user_connection.is_blocked = False
                user_connection.save()
