# Generated by Django 4.1.12 on 2023-11-04 08:15

import datetime
from django.db import migrations, models
import djongo.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Posts',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('orginal_creator_user_id', models.CharField(max_length=255)),
                ('creator_user_id', models.CharField(max_length=255)),
                ('text', models.TextField()),
                ('images', djongo.models.fields.JSONField(default=list)),
                ('likes', djongo.models.fields.JSONField(default=list)),
                ('comments', djongo.models.fields.JSONField(default=list)),
                ('kewords', djongo.models.fields.JSONField(default=list)),
                ('is_shared', models.BooleanField(default=False)),
                ('share_count', models.IntegerField(default=0)),
                ('original_post_id', models.CharField(max_length=255, null=True)),
                ('created_dateTime', models.DateTimeField(default=datetime.datetime.now)),
            ],
        ),
    ]
