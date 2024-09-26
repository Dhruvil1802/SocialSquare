from django.db import models

from Registration.models import UserProfile
from UserProfile.models import Audit



class UserConnection(Audit):
    
    connection_id = models.AutoField(db_column="connection_id", primary_key=True, null=False)

    user = models.ForeignKey(UserProfile, db_column="user",  on_delete=models.CASCADE, related_name="uc_user")
    requested_user = models.ForeignKey(UserProfile, db_column="requested_user",  on_delete=models.CASCADE, related_name="requested_user")

    request_status = models.BooleanField(default = False)
    is_requested = models.BooleanField(default = False)
    is_blocked = models.BooleanField(default = False)
    is_notified = models.BooleanField(default = False)
    
    class Meta:
        db_table = "ss_user_connection"
