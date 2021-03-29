# Generated by Django 3.1.7 on 2021-03-29 07:28

from django.db import migrations, models

def migrate_teachers(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Lesson = apps.get_model("booking", "Lesson")
    db_alias = schema_editor.connection.alias

    for lesson in Lesson.objects.using(db_alias).all():
        lesson.teachers.add(lesson.teacher)


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0005_auto_20210325_1021'),
    ]


    operations = [
        migrations.AddField(
            model_name='lesson',
            name='teachers',
            field=models.ManyToManyField(to='booking.Teacher'),
        ),
        migrations.RunPython(migrate_teachers),
        migrations.RemoveField(
            model_name='lesson',
            name='teacher',
        ),
    ]
