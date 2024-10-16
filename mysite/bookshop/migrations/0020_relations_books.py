# Generated by Django 5.1.1 on 2024-10-15 19:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookshop', '0019_authors_user_favorite_a_genres_user_favorite_g_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relations_books',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_favorite', models.BooleanField(default=False, verbose_name='Является избранной')),
                ('type', models.CharField(choices=[('basket', 'Корзина'), ('personal_library', 'Личная библиотека')], default='basket', verbose_name='Тип')),
                ('status', models.CharField(choices=[('selected', 'Выбрано'), ('not_selected', 'Не выбрано'), ('read', 'Прочитано'), ('reading', 'Читаю')], default='not_selecte', verbose_name='Статус')),
                ('book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rel_books', to='bookshop.books', verbose_name='Книга')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rel_books', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
