
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import AcceptRequest, Block, BlockedUsers, CancelRequest, DeclineRequest, FollowRequest, GetFollowers, GetFollowing, PendingRequest, RemoveFollower, UnBlock, UnFollow, suggestions

urlpatterns = [
#path('admin/', admin.site.urls),
    
    # path('registerhere/', view = registerhere),
    # path('loginhere/', view = loginhere),
    # path('registration/', view = Registration.as_view()),
    # path('login/', view = Login.as_view()),
    # path('logout/', view = Logout.as_view()),
    # path('forgotpassword/', view = forgotpassword),
    # path('editpassword/', view = editpassword),
    # path('sendotp/', view = SendOTP.as_view()),
    # path('updatepassword/', view = UpdatePassword.as_view()),
    # path('resetpassword/', view = resetpassword),
    # path('checkcredentials/', view = CheckCredentials.as_view()),
    # path('showuserprofile/', view = ShowUserProfile.as_view()),
    # path('createpost/', view = createpost),
    # path('post/', view = post.as_view()),
    path('suggestions/', view = suggestions.as_view()),
    path("followrequest/",view= FollowRequest.as_view()), 
    #path("followingfollower/",view= FollowingFollower.as_view()),
    path("pendingrequests/", view = PendingRequest.as_view()),
    path("acceptrequest/", view = AcceptRequest.as_view()),
    #path("homepage/", view = HomePage.as_view()),
    path("getfollowers/", view = GetFollowers.as_view()),
    path("getfollowing/", view = GetFollowing.as_view()),
    path("unfollow/", view = UnFollow.as_view()),
    path("remove/", view = RemoveFollower.as_view()),
    path("cancelrequest/", view = CancelRequest.as_view()),
    path("block/", view = Block.as_view()),
    path("unblock/", view = UnBlock.as_view()),
    path("blockeduser/", view = BlockedUsers.as_view()),
    path("declinerequest/", view = DeclineRequest.as_view()),
    # path("getprofiledata/", view = GetProfileData.as_view()),
    # path("updateprofile/", view = UpdateProfile.as_view()),
    # path('like_post/', view = like_post, name='like_post'),
    # path('commentpost/', view = commentpost.as_view(), name='commentpost'),
    # path('viewpost/',view = ViewPost.as_view()),
    # path('notification/',view = Notification.as_view()),
    # path('userinsights/',view = UserInsights.as_view()),
    # path('save_active_time/', view = save_active_time, name='save_active_time'),


]   
if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL,
                            document_root=settings.MEDIA_ROOT)
