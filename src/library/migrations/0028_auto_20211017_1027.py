# Generated by Django 3.2.8 on 2021-10-17 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0027_alter_member_uid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='name',
            field=models.CharField(help_text='Enter a natural languages name (e.g. English, French, Japanese etc.)', max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='preferred_language',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='library.language'),
        ),
    ]
