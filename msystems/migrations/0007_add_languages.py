from django.db import migrations

language_code_ro = "ro"
language_code_ru = "ru"


def on_migration(apps, schema_editor):
    language_model = apps.get_model("core", "language")
    if not language_model.objects.filter(code=language_code_ro).exists():
        language_model(code=language_code_ro, name="Română").save()
    if not language_model.objects.filter(code=language_code_ru).exists():
        language_model(code=language_code_ru, name="Русский").save()


class Migration(migrations.Migration):
    dependencies = [
        ('msystems', '0006_add_bill_query_rights'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(on_migration, migrations.RunPython.noop),
    ]
