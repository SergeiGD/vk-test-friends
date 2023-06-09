# Generated by Django 4.2.1 on 2023-05-06 06:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Дата создания')),
                ('date_confirmed', models.DateTimeField(blank=True, null=True, verbose_name='Дата принятия')),
                ('date_rejected', models.DateTimeField(blank=True, null=True, verbose_name='Дата отклонения')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outcoming_requests', related_query_name='outcoming_request', to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_requests', related_query_name='incoming_request', to=settings.AUTH_USER_MODEL, verbose_name='Адресат')),
            ],
        ),
    ]
