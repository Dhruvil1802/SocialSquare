# Generated by Django 5.0.2 on 2024-03-31 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registration', '0004_alter_historicaluserprofile_date_of_birth_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='bio',
            field=models.CharField(db_column='bio', default=None, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(db_column='bio', default=None, max_length=256, null=True),
        ),
    ]
