# Generated by Django 5.1.1 on 2024-11-10 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0033_alter_authors_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companies',
            name='name',
            field=models.CharField(max_length=40, null=True, verbose_name='Название'),
        ),
    ]
