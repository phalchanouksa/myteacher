from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0007_update_joining_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='department',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='designation',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='qualification',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='joining_date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
