# Generated by Django 4.2.10 on 2024-02-28 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_scrap', '0007_alter_news_title_alter_sources_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sources',
            name='url',
            field=models.URLField(max_length=300),
        ),
    ]
