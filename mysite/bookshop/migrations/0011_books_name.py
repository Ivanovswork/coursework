# Generated by Django 5.1.1 on 2024-10-07 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0010_books'),
    ]

    operations = [
        migrations.AddField(
            model_name='books',
            name='name',
            field=models.CharField(max_length=20, null=True, verbose_name='Название'),
        ),
    ]
