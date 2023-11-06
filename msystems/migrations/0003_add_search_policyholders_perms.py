# Generated by Django 3.2.21 on 2023-11-03 16:46

from django.db import migrations


POLICY_HOLDER_SEARCH_PERM = [150101, 150201, 150301]
ROLE_NAME_INSPECTOR = "Inspector"
ROLE_NAME_EMPLOYER = "Employer"


def add_rights(role_name, role_model, role_right_model):
    role = role_model.objects.get(name=role_name)
    for right_id in POLICY_HOLDER_SEARCH_PERM:
        if not role_right_model.objects.filter(validity_to__isnull=True, role=role, right_id=right_id).exists():
            _add_right_for_role(role, right_id, role_right_model)


def _add_right_for_role(role, right_id, role_right_model):
    role_right_model.objects.create(role=role, right_id=right_id, audit_user_id=1)


def remove_rights(role_id, role_right_model):
    role_right_model.objects.filter(
        role__is_system=role_id,
        right_id__in=POLICY_HOLDER_SEARCH_PERM,
        validity_to__isnull=True
    ).delete()


def on_migration(apps, schema_editor):
    role_model = apps.get_model("core", "role")
    role_right_model = apps.get_model("core", "roleright")
    add_rights(ROLE_NAME_INSPECTOR, role_model, role_right_model)
    add_rights(ROLE_NAME_EMPLOYER, role_model, role_right_model)


def on_reverse_migration(apps, schema_editor):
    role_right_model = apps.get_model("core", "roleright")
    remove_rights(ROLE_NAME_INSPECTOR, role_right_model)
    remove_rights(ROLE_NAME_EMPLOYER, role_right_model)


class Migration(migrations.Migration):

    dependencies = [
        ('msystems', '0002_add_roles'),
    ]

    operations = [
    ]
