# Generated by Django 5.0.1 on 2024-02-21 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketsystem', '0004_alter_user_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]