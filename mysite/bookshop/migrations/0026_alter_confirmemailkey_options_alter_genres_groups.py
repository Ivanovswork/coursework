# Generated by Django 5.1.1 on 2024-11-04 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0025_alter_purchases_options_alter_comments_rating_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='confirmemailkey',
            options={'verbose_name': 'Ключ подтверждения', 'verbose_name_plural': 'Ключи подтверждения'},
        ),
        migrations.AlterField(
            model_name='genres',
            name='groups',
            field=models.ManyToManyField(related_name='genres', to='bookshop.groups'),
        ),
    ]
