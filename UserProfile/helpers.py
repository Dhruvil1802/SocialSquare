from django.utils import timezone
from itertools import chain
from operator import attrgetter
from Connections.models import UserConnection
from Posts.models import Comments, Like, UserPost
from UserProfile.models import UserActivity, UserProfile
from multiprocessing import context
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from requests import request
from django.db.models import Q




def requested_user_profile(user,requested_user):
      
            user_connection = None
            requested_user_connection = None
            requested_user_post = []
            requested_user_post_id=[]
            requested_user= UserProfile.objects.get(user_id = requested_user)

            if UserConnection.objects.filter(user=user,requested_user=requested_user).exists():
                user_connection = UserConnection.objects.get(user=user,requested_user=requested_user)
            else:
                user_connection = UserConnection()
                user_connection.user = user
                user_connection.requested_user = requested_user
                user_connection.save()

                requested_user_connection = UserConnection()
                requested_user_connection.user = requested_user
                requested_user_connection.requested_user = user
                requested_user_connection.save()

                user_connection = UserConnection.objects.get(user=user,requested_user=requested_user)
                
            if  UserConnection.objects.filter(user=requested_user,requested_user=user).exists():
                requested_user_connection =  UserConnection.objects.get(user=requested_user,requested_user=user)
            if UserPost.objects.filter(user = requested_user.user_id).exists():
                requested_user_post = UserPost.objects.filter(user = requested_user.user_id)
                requested_user_post_id = UserPost.objects.filter(user = requested_user.user_id).values("post_id")
            return user_connection,requested_user_connection,requested_user_post,requested_user_post_id

        
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
        likes=[]
        comments=[]
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
      
def post_analytics(likes_list,post_list,comments_list,user):
    if UserPost.objects.filter(user=user).exists():
                posts = UserPost.objects.filter(user=user).order_by('created_at')
                i=1
                for post in posts:
                    if Like.objects.filter(post_id = post.post_id).exists():
                        number_of_likes_on_post = Like.objects.filter(post_id = post.post_id).count()
                        likes_list.append(int(number_of_likes_on_post))
                    else:
                        likes_list.append(0)


                    if Comments.objects.filter(post_id = post.post_id).exists():
                        number_of_comments_on_post = Comments.objects.filter(post_id = post.post_id).count()
                        comments_list.append(int(number_of_comments_on_post))
                    else:
                        comments_list.append(0)

                    post_list.append(i)

                    i = i+1
    return likes_list,post_list,comments_list,user

def time_spent(user,start_time_obj,next_day,user_activity_per_day,user_activity_on_day):

                            time_spent(user,start_time_obj,next_day,user_activity_per_day,user_activity_on_day)
                            day_activity = UserActivity.objects.filter(user = user, updated_at__range = [start_time_obj,next_day])
                            total_miliseconds=0
                            for i in day_activity:
                                total_miliseconds = total_miliseconds + i.active_time

                            total_time = str(round(total_miliseconds/60000))
                            unit = "minutes"

                        
                            user_activity_per_day.append(int(total_time))
                            user_activity_on_day.append(int(start_time_obj.day))

def save_time(active_time):
            email = request.session['email']
            user= UserProfile.objects.get(email = email) 
            user_activity = UserActivity()
            user_activity.active_time = active_time
            user_activity.user = user
            user_activity.save()