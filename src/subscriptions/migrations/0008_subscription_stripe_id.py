# Generated by Django 5.0.7 on 2024-09-04 00:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_usersubscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
