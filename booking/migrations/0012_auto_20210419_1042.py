# Generated by Django 3.1.7 on 2021-04-19 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0011_auto_20210419_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
