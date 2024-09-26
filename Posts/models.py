from django.db import models

from Registration.models import UserProfile
from UserProfile.models import Audit



class UserPost(Audit):
    post_id = models.AutoField(db_column="post_id", primary_key=True,
                               null=False)
    user = models.ForeignKey(UserProfile, db_column="user",on_delete=models.CASCADE)
    caption = models.CharField(db_column="caption", max_length=256, default=None,null=True)
    post_pic =  models.FileField(upload_to='Images/PostPic', max_length=100)
    #post_pic =  models.ImageField(upload_to='Images/PostPic', height_field=None, width_field=None, max_length=100)
    like_count = models.IntegerField(db_column="like_count", default=0)
    comment_count = models.IntegerField(db_column="comment_count", default=0)
    is_archived = models.BooleanField(default = False)
    class Meta:
        db_table = "ss_post"

class Like(Audit):
    
    like_id = models.AutoField(db_column="like_id", primary_key=True, null=False)
    post_id = models.ForeignKey(UserPost, db_column="post_id",  on_delete=models.CASCADE)
    follower = models.ForeignKey(UserProfile, db_column="follower",  on_delete=models.CASCADE)
    
    is_notified = models.BooleanField(default = False)
    class Meta:
        db_table = "ec_like"

class Comments(Audit):
    
    comment_id = models.AutoField(db_column="comment_id", primary_key=True, null=False)
    post_id = models.ForeignKey(UserPost, db_column="post_id",  on_delete=models.CASCADE)
    follower = models.ForeignKey('Registration.UserProfile', db_column="follower",  on_delete=models.CASCADE)
    comment = models.CharField(db_column="comment", max_length=256,  default=None)
    
    is_notified = models.BooleanField(default = False)
    
    class Meta:
        db_table = "ec_comment"
