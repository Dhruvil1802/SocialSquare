
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ProfileData, Notification,  UpdateProfile, UserInsights, ShowUserProfile,  save_active_time

urlpatterns = [

    path('showuserprofile/', view = ShowUserProfile.as_view()),
    
    path("postprofiledata/", view = ProfileData.as_view()),
    path("updateprofile/", view = UpdateProfile.as_view()),
    
    path('notification/',view = Notification.as_view()),
    path('userinsights/',view = UserInsights.as_view()),
    path('save_active_time/', view = save_active_time),


]   
if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL,
                            document_root=settings.MEDIA_ROOT)
