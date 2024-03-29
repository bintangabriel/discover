from django.contrib.postgres.fields import ArrayField
from django.db import models
from urllib.parse import urlparse
from django.utils.text import slugify


class Sources(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=300)
    title = models.TextField()
    
    def save(self, *args, **kwargs):
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc

        self.name = domain
        super().save(*args, **kwargs)


class News(models.Model):
    slug = models.SlugField(default='', max_length=255)
    title = models.TextField()
    content = models.TextField()
    sources = models.ManyToManyField(Sources, blank=True)
    day = models.IntegerField()
    image_url = models.URLField(default='https://www.google.com/url?sa=i&url=https%3A%2F%2Fid.pinterest.com%2Fsichydoubleyou%2Fquestion-mark%2F&psig=AOvVaw2x2acJYiIjtoiCIEXjmORK&ust=1709193740223000&source=images&cd=vfe&opi=89978449&ved=0CBMQjRxqFwoTCPDX6YPJzYQDFQAAAAAdAAAAABAE')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
