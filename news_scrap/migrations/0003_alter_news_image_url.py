# Generated by Django 4.2.10 on 2024-02-28 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news_scrap', '0002_news_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='image_url',
            field=models.URLField(default='https://www.google.com/url?sa=i&url=https%3A%2F%2Fid.pinterest.com%2Fsichydoubleyou%2Fquestion-mark%2F&psig=AOvVaw2x2acJYiIjtoiCIEXjmORK&ust=1709193740223000&source=images&cd=vfe&opi=89978449&ved=0CBMQjRxqFwoTCPDX6YPJzYQDFQAAAAAdAAAAABAE'),
        ),
    ]
