from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('accounts', '0005_reset_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('teacher', 'Teacher'), ('student', 'Student')], default='student', max_length=10)),
                ('identifier', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('department', models.CharField(blank=True, max_length=100)),
                ('designation', models.CharField(blank=True, max_length=100)),
                ('qualification', models.CharField(blank=True, max_length=200)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True)),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('joining_date', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
        ),
    ]
