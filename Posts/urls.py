
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import  HomePage, ViewPost, commentpost, createpost,like_post, post
urlpatterns = [

    path('createpost/', view = createpost),
    path('post/', view = post.as_view()),

     path("homepage/", view = HomePage.as_view()),

    path('like_post/', view = like_post, name='like_post'),
    path('commentpost/', view = commentpost.as_view(), name='commentpost'),
    path('viewpost/',view = ViewPost.as_view()),



]   
