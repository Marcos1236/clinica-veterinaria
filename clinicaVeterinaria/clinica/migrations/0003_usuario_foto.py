# Generated by Django 5.1.1 on 2024-10-12 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinica', '0002_alter_citas_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='usuarios_fotos/'),
        ),
    ]
