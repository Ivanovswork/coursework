# Generated by Django 5.1.1 on 2024-12-04 09:50

import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0006_books_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='authors',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='books',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='authors',
            name='name',
            field=models.CharField(db_index=True, max_length=60, null=True, verbose_name='Имя'),
        ),
    ]
