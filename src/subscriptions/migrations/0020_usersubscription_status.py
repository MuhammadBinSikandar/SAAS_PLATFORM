# Generated by Django 5.0.7 on 2024-09-08 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0019_usersubscription_current_period_end_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='status',
            field=models.CharField(blank=True, choices=[('active', 'Active'), ('cancelled', 'Cancelled'), ('incomplete', 'Incomplete'), ('incomplete_expired', 'Incomplete Expired'), ('past_due', 'Past Due'), ('trialing', 'Trialing'), ('unpaid', 'Unpaid'), ('paused', 'Paused')], max_length=120, null=True),
        ),
    ]
