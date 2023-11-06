from django.db import migrations

on_reverse_migration = migrations.RunPython.noop


def on_migration(apps, schema_editor):
    location_model = apps.get_model('location', 'Location')
    location_model.objects.filter(code='MM01').update(type='W')


class Migration(migrations.Migration):
    dependencies = [
        ('msystems', '0004_add_modal_right'),
    ]

    operations = [
        migrations.RunPython(on_migration, on_reverse_migration),
    ]
