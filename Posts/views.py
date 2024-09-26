
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

from Posts.helpers import get_post, user_feed
from UserProfile.helpers import   user_liked_post

# Create your views here.
from .models import  Comments, Like, UserPost, UserProfile
from django.urls import reverse
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone

from django.shortcuts import get_object_or_404


# get the data related to posts by following users and send it on the homepage 
class HomePage(View):
    @csrf_exempt
    def get(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
            requested_users_post , requested_users_post_id = user_feed(user)
            liked_posts = user_liked_post(requested_users_post_id,user)
            if len(requested_users_post) == 0:
                requested_users_post,requested_users_post_id = get_post()
                liked_posts = user_liked_post(requested_users_post_id,user)
            
            return render(request, 'homepage.html',{"user":user,"requested_user_post":requested_users_post,"liked_post":liked_posts, "currentpage":"homepage"})
        except Exception as ex:
            print(ex)

# get the data of the users posts (like and comments)
class ViewPost(View):
    @csrf_exempt
    def get(self, request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            user= UserProfile.objects.get(email = email)
            post_id = request.GET.get("post_id")
            post = UserPost.objects.get(post_id = post_id)

            comments=[]
            if Comments.objects.filter(post_id=post_id).exists():
                comments = Comments.objects.filter(post_id=post_id).order_by('-created_at')

            liked_posts=None
            if Like.objects.filter(post_id = post_id).exists():   

                    liked_post = Like.objects.filter(post_id = post.post_id).values_list("post_id")
                    liked_posts=[]
                    for lp in liked_post:
                        liked_posts.append(lp[0])

            return render(request, 'viewpost.html',{"comments":comments,"post":post,"liked_post":liked_posts,"user":user})
        except Exception as ex:
            print(ex)

# when the user like any post, it fetch the data with the help of ajax and update the model 
def like_post(request):
    
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        follower = request.POST.get("follower")
        color = request.POST.get("color")

        post = UserPost.objects.get(post_id=post_id)
        follower = UserProfile.objects.get(user_id =  follower)

        try:
            if Like.objects.filter(post_id=post, follower = follower).exists() and color=="white":
                like = Like.objects.get(post_id=post,follower = follower)
                like.delete()

                post = UserPost.objects.get(post_id = post_id)
                post.like_count = post.like_count - 1
                post.save()

            else:
                like = Like()
                like.post_id = post
                like.follower = follower
                like.save()

                post = UserPost.objects.get(post_id = post_id)
                post.like_count = post.like_count + 1
                post.save()

            return JsonResponse({'success': True, 'post_like_count':post.like_count})
        except Like.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Post not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# fetch the comment from viewpost.html, save it in the model and then redirect it to the viewpost
class commentpost(View):
    @csrf_exempt
    def post(self,request):
        try:
            if request.method == 'POST':
                if 'email' in request.session:
                    email = request.session['email']
                else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)

                post_id = request.POST.get('post_id')
                follower = request.POST.get("follower")
                comment = request.POST.get("comment")
                post = UserPost.objects.get(post_id=post_id)
                follower = UserProfile.objects.get(user_id =  follower)

                try:
                    comment_object = Comments()
                    comment_object.post_id = post
                    comment_object.follower = follower
                    comment_object.comment = comment
                    comment_object.save()
                    
                    redirect_url = f'../../Posts/viewpost/?post_id={post_id}'
                    return redirect(redirect_url)

                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)

# render createpost.html
def createpost(request):
    message = request.GET.get('message')
    return render(request, 'createpost.html', {'message':message,"currentpage":"createpost"})


# Fetch the post pic and caption from the createpost.html and save it in the database
class post(View):
    @csrf_exempt
    def post(self,request):
        try:
            if 'email' in request.session:
                    email = request.session['email']
            else:
                    redirect_url = f'../../Registration/login/?message=you are not logedin'
                    return redirect(redirect_url)
            
            user= UserProfile.objects.get(email = email)
    
            
            
            
            if "post_pic" not in request.FILES:
                redirect_url = f'../../Posts/createpost/?message=some required fields are missing'
                return redirect(redirect_url)
            user_post = UserPost()
            post_pic = request.FILES["post_pic"]
            
            user_post.user = user 
            user_post.post_pic = post_pic

            if "caption" in request.POST:
                caption = request.POST.get('caption')
                user_post.caption = caption    
            user_post.save()
            redirect_url = f'../../UserProfile/showuserprofile/'
            return redirect(redirect_url)

        except Exception as ex:
            print(ex)


