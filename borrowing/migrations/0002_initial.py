# Generated by Django 4.0.4 on 2024-06-16 10:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('borrowing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowing',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowings', to=settings.AUTH_USER_MODEL),
        ),
    ]
