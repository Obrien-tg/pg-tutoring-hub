from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_firebasetoken"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="clerk_id",
            field=models.CharField(max_length=128, null=True, blank=True, unique=True),
        ),
    ]
