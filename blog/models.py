from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Post(models.Model):
    """A blog article."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True, help_text="Short summary shown in lists.")
    body = models.TextField(help_text="Main article content. Line breaks are preserved.")
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags.")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', args=[self.slug])

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]