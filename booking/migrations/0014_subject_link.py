# Generated by Django 3.2 on 2021-05-02 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0013_user_attended_questionnaire'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='link',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
