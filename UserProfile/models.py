from django.db import models
from Registration.models import Audit, UserProfile



class UserActivity(Audit):
    useractivity_id = models.AutoField(db_column="useractivity_id", primary_key=True, null=False)
    user = models.ForeignKey(UserProfile, db_column="user", on_delete=models.CASCADE)
    active_time = models.IntegerField(db_column="active_time", default=0)

    class Meta:
        db_table = "ec_user_activity"
