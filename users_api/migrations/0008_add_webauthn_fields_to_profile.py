from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users_api', '0005_customuser_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='webauthn_credential_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='webauthn_public_key',
            field=models.TextField(blank=True, null=True),
        ),
    ]
