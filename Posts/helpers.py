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

def requested_user_profile(user,requested_user):
      
            user_connection = None
            requested_user_connection = None
            requested_user_post = None

            requested_user= UserProfile.objects.get(user_id = requested_user)

            if UserConnection.objects.filter(user=user,requested_user=requested_user).exists():
                user_connection = UserConnection.objects.get(user=user,requested_user=requested_user)
            if  UserConnection.objects.filter(user=requested_user,requested_user=user).exists():
                requested_user_connection =  UserConnection.objects.get(user=requested_user,requested_user=user)
            if UserPost.objects.filter(user = requested_user.user_id).exists():
                requested_user_post = UserPost.objects.filter(user = requested_user.user_id).values
                requested_user_post_id = UserPost.objects.filter(user = requested_user.user_id).values("post_id")
            return user_connection,requested_user_connection,requested_user_post,requested_user_post_id

def user_feed(user):
        if UserConnection.objects.filter(user=user, request_status=True).values_list("requested_user").exists():
            following = UserConnection.objects.filter(user=user, request_status=True).values_list("requested_user")
            requested_users_post = []
            requested_users_post_id = []
            if UserPost.objects.filter(user__in = following).exists():
                    requested_users_post = UserPost.objects.filter(user__in=following).order_by('-created_at')
                    requested_users_post_id = UserPost.objects.filter(user__in = following).values("post_id")
            return requested_users_post,requested_users_post_id
        else:
            requested_users_post=[]
            requested_users_post_id=[]
            return requested_users_post,requested_users_post_id
        
def user_liked_post(users_post,user):
        liked_posts = []
        if Like.objects.filter(post_id__in = users_post, follower = user).exists():
                liked_post = Like.objects.filter(post_id__in = users_post).values_list("post_id")
                liked_posts=[]
                for lp in liked_post:
                    liked_posts.append(lp[0])
        return liked_posts

def connection_requests_profiles(user):
        try:
            accepted_requests = UserConnection.objects.filter(requested_user=user)
            return accepted_requests
        except Exception as ex:
            print(ex)

def notifications(user):
        posts = UserPost.objects.filter(user = user)

        if Like.objects.filter(post_id__in = posts).exists():
            likes = Like.objects.filter(post_id__in = posts)
           
        if Comments.objects.filter(post_id__in = posts).exists():
            comments = Comments.objects.filter(post_id__in = posts) 

        connection_requests =   connection_requests_profiles(user)
        notifications = list(chain(likes, comments, connection_requests))
        sorted_notifications = sorted(notifications, key=attrgetter('updated_at'), reverse=True)
        notification_list=[]
        for notification in sorted_notifications:
                x = timezone.now() - notification.updated_at
                if x.total_seconds()  < 60:
                      notification.updated_at = str(round(x.total_seconds())) + "seconds ago"
                if x.total_seconds() / 60 >1 and x.total_seconds() / 60 < 60: 
                      notification.updated_at = str(round(x.total_seconds()/60)) + "minutes ago"
                if x.total_seconds() / 3600 > 1 and x.total_seconds() / 3600 < 24:
                      notification.updated_at = str(round(x.total_seconds()/3600)) + "hours ago"
                if x.total_seconds() / 86400 > 1 and x.total_seconds() / 86400 < 30:
                      notification.updated_at = str(round(x.total_seconds()/86400)) + "days ago"
                if x.total_seconds() / 2592000 > 1 and x.total_seconds() / 2592000 < 12:
                      notification.updated_at = str(round(x.total_seconds()/2592000)) + "months ago"
                if x.total_seconds() / 31104000 > 1:
                      notification.updated_at = str(round(x.total_seconds()/31104000)) + "years ago"

                notification_list.append(notification)

        return notification_list

# def notification(notification_category,user):
#         notifications = Notification()

#         print(notification_category)
#         if isinstance(notification_category, Like):
#             notifications.like = notification_category
            
#         if isinstance(notification_category, Comments):
#             notifications.comment = notification_category

#         if isinstance(notification_category, UserConnection):
#             notifications.connection = notification_category
        
#         notifications.user = user
#         notifications.save()

def get_post():
        public_users = UserProfile.objects.filter(is_private = False).values_list("user_id")
        requested_users_post=[]
        requested_users_post_id=[]
        if UserPost.objects.filter(user__in = public_users).exists():
            requested_users_post = UserPost.objects.filter().order_by('-created_at')
            requested_users_post_id = UserPost.objects.filter().values("post_id")
            return requested_users_post,requested_users_post_id
        else:
            requested_users_post=[]
            requested_users_post_id=[]
            return requested_users_post,requested_users_post_id