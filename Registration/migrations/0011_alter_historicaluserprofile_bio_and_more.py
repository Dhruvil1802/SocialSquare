# Generated by Django 5.0.2 on 2024-04-03 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Registration', '0010_alter_historicaluserprofile_bio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluserprofile',
            name='bio',
            field=models.CharField(db_column='bio', max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.CharField(db_column='bio', max_length=256, null=True),
        ),
    ]