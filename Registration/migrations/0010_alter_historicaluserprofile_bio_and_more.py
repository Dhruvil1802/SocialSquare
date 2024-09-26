# Generated by Django 5.0.2 on 2024-04-03 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registration', '0009_alter_historicaluserprofile_profile_pic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='bio',
            field=models.CharField(db_column='bio', default='', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='profile_pic',
            field=models.TextField(db_column='profile_pic', default='Images/ProfilePic/Screenshot 2024-02-29 033331.png', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(db_column='bio', default='', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_pic',
            field=models.ImageField(db_column='profile_pic', default='Images/ProfilePic/Screenshot 2024-02-29 033331.png', null=True, upload_to='Images/ProfilePic'),
        ),
    ]
