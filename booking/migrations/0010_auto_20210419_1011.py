# Generated by Django 3.1.7 on 2021-04-19 05:11

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_auto_20210415_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
        migrations.RemoveField(
            model_name='event',
            name='user',
        ),
        migrations.AddField(
            model_name='event',
            name='from_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 19, 5, 11, 58, 737430, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='event',
            name='special',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='to_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 4, 19, 5, 11, 58, 737471, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='EventMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responsible', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
