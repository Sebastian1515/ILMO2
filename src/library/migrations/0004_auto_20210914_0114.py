# Generated by Django 3.2.7 on 2021-09-13 23:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_auto_20210913_1814'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('date_of_death', models.DateField(blank=True, null=True, verbose_name='Died')),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a book genre (e.g. Science Fiction)', max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='book',
            name='aquired_date',
        ),
        migrations.RemoveField(
            model_name='book',
            name='label',
        ),
        migrations.AddField(
            model_name='book',
            name='isbn',
            field=models.CharField(default=1234567890123, help_text='ISBN number (13 Characters)', max_length=13, unique=True, verbose_name='ISBN'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='book',
            name='summary',
            field=models.TextField(default='No summary', help_text='Enter a brief description of the book', max_length=1000),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='BookInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=20)),
                ('available', models.BooleanField()),
                ('book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='library.book')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(help_text='Select a genre for this book', to='library.Genre'),
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='library.author'),
        ),
        migrations.AlterField(
            model_name='loan',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='library.bookinstance'),
        ),
    ]
