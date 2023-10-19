from django.db import migrations


def get_or_create_location(location_model, code, name, type, parent=None):
    loc = location_model.objects.filter(
        code=code, validity_to__isnull=True).first()
    if not loc:
        loc = location_model.objects.create(
            code=code, name=name, type=type, audit_user_id=0, parent=parent)
    return loc


def add_global_locations(apps, schema_editor):
    location_model = apps.get_model("location", "Location")

    region = get_or_create_location(
        location_model,
        'MR01',
        'Moldova Regiune',
        'R')
    district = get_or_create_location(
        location_model,
        'MD01',
        'Moldova Raion',
        'D',
        region)
    municipality = get_or_create_location(
        location_model,
        'MM01',
        'Moldova Municipiu',
        'M',
        district)
    get_or_create_location(
        location_model,
        'MV01',
        'Moldova Oras/Sat',
        'V',
        municipality)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('location', '0018_auto_20230925_2243'),
    ]

    operations = [
        migrations.RunPython(add_global_locations, migrations.RunPython.noop),
    ]
