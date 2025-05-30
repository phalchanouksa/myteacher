from django.db import migrations, models
import django.db.models.deletion


def set_teacher_not_null(apps, schema_editor):
    # This function is empty because we're just changing the schema
    # The data migration in 0003_set_default_teacher already ensured all records have a teacher
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),  # Make sure this is the correct dependency
        ('assignments', '0003_set_default_teacher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='teacher',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='assignments_given',
                to='accounts.userprofile',
                null=False
            ),
        ),
    ]
