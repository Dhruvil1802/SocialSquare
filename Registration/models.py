from django.utils import timezone
from django.db import models
from simple_history.models import HistoricalRecords


class Audit(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    


class UserProfile(Audit):
    user_id = models.AutoField(db_column="user_id", primary_key=True, null=False)
    username = models.CharField(db_column="username", max_length=256, default="")
    password = models.CharField(db_column="password", max_length=256, default="")
    email = models.CharField(db_column="email", max_length=256, default="")
    date_of_birth = models.DateField(default=None,null=True)
    profile_pic = models.ImageField(upload_to='Images/ProfilePic', db_column="profile_pic",default="Images/ProfilePic/Screenshot 2024-02-29 033331.png", height_field=None, width_field=None,null=True)
    is_verified = models.BooleanField(db_column="is_verified", default=False)
    is_private = models.BooleanField(db_column="is_private", default=False)
    follower_count = models.IntegerField(db_column="follower_count", default=0)
    following_count = models.IntegerField(db_column="following_count", default=0)
    bio = models.CharField(db_column="bio", max_length=256, default="" ,null=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "ss_user_profile"