# Generated by Django 3.1.7 on 2021-04-13 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_teachersubject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teachersubject',
            name='level',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
