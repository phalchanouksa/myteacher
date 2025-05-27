from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_fix_user_id_field'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP TABLE IF EXISTS accounts_userprofile;
            """,
            reverse_sql="""
            -- No reverse SQL needed
            """
        ),
    ]
