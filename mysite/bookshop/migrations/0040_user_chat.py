# Generated by Django 5.1.1 on 2024-11-15 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0039_rename_parent_comments_authors_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chat',
            field=models.BooleanField(default=True, verbose_name='Возможность использовать комментарии'),
        ),
    ]
