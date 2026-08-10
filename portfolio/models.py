from django.db import models
from django.utils.text import slugify


class CaseStudy(models.Model):
    """A detailed client success story."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    client_name = models.CharField(max_length=160)
    industry = models.CharField(max_length=120, blank=True)
    problem = models.TextField()
    solution = models.TextField()
    results = models.TextField(blank=True, help_text="Measurable outcomes: time saved, costs reduced, etc.")
    cover_image = models.ImageField(upload_to='case_studies/', blank=True, null=True)
    technologies = models.CharField(max_length=300, blank=True, help_text="Comma-separated tech tags, e.g. Odoo, Python, PostgreSQL")
    duration = models.CharField(max_length=80, blank=True, help_text="e.g. '3 months'")
    completed_at = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show on the home page.")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-completed_at', '-created_at']
        verbose_name_plural = "Case studies"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_tech_list(self):
        return [t.strip() for t in self.technologies.split(',') if t.strip()]


class SuccessProject(models.Model):
    """A delivered project/portfolio entry (own work or open-source)."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='projects/', blank=True, null=True)
    project_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    technologies = models.CharField(max_length=300, blank=True)
    completed_at = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-completed_at']
        verbose_name_plural = "Success projects"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_tech_list(self):
        return [t.strip() for t in self.technologies.split(',') if t.strip()]


class Client(models.Model):
    """A client you've worked with."""

    name = models.CharField(max_length=160)
    logo = models.ImageField(upload_to='clients/', blank=True, null=True, help_text="Square logo works best.")
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    testimonial = models.TextField(blank=True)
    testimonial_author = models.CharField(max_length=120, blank=True, help_text="Name of the person who gave the testimonial.")
    testimonial_role = models.CharField(max_length=120, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Show on the home page strip.")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Certification(models.Model):
    """A professional certification, e.g. from Odoo."""

    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=160, default="Odoo")
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=120, blank=True)
    credential_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='certifications/', blank=True, null=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-issue_date']

    def __str__(self):
        return f"{self.title} ({self.issuer})"