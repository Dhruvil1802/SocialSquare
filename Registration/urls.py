
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from UserProfile.views import save_active_time
from .views import CheckCredentials, LoginCredentials,  Logout, Registration, SendOTP, UpdatePassword, editpassword, forgotpassword, login,  registerhere, resetpassword

urlpatterns = [

    path('registerhere/', view = registerhere),
    path('login/', view = login),
    path('registration/', view = Registration.as_view()),
    path('logincredentials/', view = LoginCredentials.as_view()),
    path('logout/', view = Logout.as_view()),
    path('forgotpassword/', view = forgotpassword),
    path('editpassword/', view = editpassword),
    path('sendotp/', view = SendOTP.as_view()),
    path('updatepassword/', view = UpdatePassword.as_view()),
    path('resetpassword/', view = resetpassword.as_view()),
    path('checkcredentials/', view = CheckCredentials.as_view()),

    path('save_active_time/', view = save_active_time, name='save_active_time'),


]   
if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL,
                            document_root=settings.MEDIA_ROOT)
