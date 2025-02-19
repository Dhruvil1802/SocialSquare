# Generated by Django 5.0.2 on 2024-03-30 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registration', '0002_historicaluserprofile_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='bio',
            field=models.CharField(db_column='bio', default=None, max_length=256),
        ),
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='date_of_birth',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='profile_pic',
            field=models.TextField(db_column='profile_pic', default=None, max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(db_column='bio', default=None, max_length=256),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_pic',
            field=models.ImageField(db_column='profile_pic', default=None, upload_to='Images/ProfilePic'),
        ),
    ]
