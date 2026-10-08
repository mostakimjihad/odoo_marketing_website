"""Seed default weekly availability: Sun-Thu (Bangladesh work week) 10:00-12:00
and 14:00-17:00. Owner can edit/delete from admin after first run.
"""
from django.db import migrations


DEFAULT_RULES = [
    # (weekday, start, end) — Bangladesh standard work week, Sun-Thu
    (6, '10:00', '12:00'),  # Sunday
    (6, '14:00', '17:00'),
    (0, '10:00', '12:00'),  # Monday
    (0, '14:00', '17:00'),
    (1, '10:00', '12:00'),  # Tuesday
    (1, '14:00', '17:00'),
    (2, '10:00', '12:00'),  # Wednesday
    (2, '14:00', '17:00'),
    (3, '10:00', '12:00'),  # Thursday
    (3, '14:00', '17:00'),
]


def seed(apps, schema_editor):
    AvailabilityRule = apps.get_model('core', 'AvailabilityRule')
    if AvailabilityRule.objects.exists():
        return  # owner already customised — don't overwrite
    from datetime import time
    for weekday, start, end in DEFAULT_RULES:
        sh, sm = (int(x) for x in start.split(':'))
        eh, em = (int(x) for x in end.split(':'))
        AvailabilityRule.objects.create(
            weekday=weekday,
            start_time=time(sh, sm),
            end_time=time(eh, em),
            is_active=True,
        )


def unseed(apps, schema_editor):
    AvailabilityRule = apps.get_model('core', 'AvailabilityRule')
    AvailabilityRule.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_availabilityrule_blockeddate_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
