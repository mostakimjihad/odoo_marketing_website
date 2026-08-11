from django.db import models
from django.utils.text import slugify


class SiteSettings(models.Model):
    """Singleton model for global site settings. Only one row should exist."""

    hero_title = models.CharField(max_length=200, default="Odoo & ERP Expert for Hire")
    hero_subtitle = models.TextField(blank=True, default="From small business ERP rollouts to complex custom modules — I deliver clean, reliable Odoo solutions that fit your business.")
    hero_cta_text = models.CharField(max_length=50, default="Hire Me on Fiverr")
    hero_cta_secondary_text = models.CharField(max_length=50, default="View Services")
    hero_video = models.FileField(
        upload_to='hero/', blank=True, null=True,
        help_text="Short looping MP4/WebM shown behind the hero. Muted, autoplay. Best: under 5 MB, 720p or lower, ~10s loop.",
    )
    about_title = models.CharField(max_length=200, default="Hi, I'm Mostakim Jihad")
    about_body = models.TextField(blank=True, help_text="Markdown not supported — line breaks render as paragraphs.")
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    cv_file = models.FileField(upload_to='cv/', blank=True, null=True, help_text="PDF resume visitors can download.")

    full_name = models.CharField(max_length=120, default="Mostakim Jihad")
    tagline = models.CharField(max_length=200, default="Senior ERP & Odoo Engineer · Functional · Technical · Deployment · Data Migration")
    phone = models.CharField(max_length=40, blank=True, default="+8801870460323")
    email = models.EmailField(blank=True, default="mostakimjihad652001@gmail.com")
    location = models.CharField(max_length=200, blank=True, default="Bawnia Bazar, Dhaka-1212, Bangladesh")
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    codeforces = models.URLField(blank=True)
    fiverr_url = models.URLField(blank=True, default="https://www.fiverr.com/your_gig")

    years_experience = models.PositiveIntegerField(default=4)
    projects_completed = models.PositiveIntegerField(default=20)
    happy_clients = models.PositiveIntegerField(default=15)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton — only allow row id=1 to exist.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site Settings"


class Service(models.Model):
    """A service offered to clients (listed on /services/)."""

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    short_description = models.CharField(max_length=255)
    icon = models.CharField(max_length=120, default="apps.svg", help_text="Filename in static/images/icons/, e.g. 'apps.svg' or 'repair.svg'.")
    description = models.TextField(blank=True, help_text="Full description shown on the service detail page.")
    features = models.TextField(blank=True, help_text="One feature per line; rendered as a bullet list on the detail page.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_features_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class ContactInquiry(models.Model):
    """A message submitted through the contact form."""

    BUDGET_CHOICES = [
        ('under_500', 'Under $500'),
        ('500_1500', '$500 – $1,500'),
        ('1500_5000', '$1,500 – $5,000'),
        ('5000_plus', '$5,000+'),
        ('discuss', "Let's discuss"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=120, blank=True)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.email}"


class ERPModule(models.Model):
    """An Odoo/ERP module showcased on the homepage (POS, Accounting, MRP, ...).

    Each module has its own detail page with a looping demo video/GIF
    (uploaded via admin) and a hire-me CTA.
    """

    CATEGORY_CHOICES = [
        ('operations', 'Operations'),
        ('sales',      'Sales & Commerce'),
        ('finance',    'Finance & Accounting'),
        ('people',     'People & HR'),
        ('web',        'Web & Marketing'),
        ('productivity','Productivity'),
    ]

    name = models.CharField(max_length=80, help_text="Module name, e.g. 'Point of Sale', 'Accounting', 'Manufacturing'.")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    short_tag = models.CharField(max_length=20, help_text="Short code shown on the tile, e.g. 'POS', 'ACC', 'MRP'.", default="")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='operations')
    tagline = models.CharField(max_length=160, help_text="One-line summary shown on the homepage tile.", blank=True)
    description = models.TextField(help_text="Full description shown on the module detail page.", blank=True)

    # Optional assets the owner can upload later
    demo_video = models.FileField(
        upload_to='modules/videos/', blank=True, null=True,
        help_text="Looping screen recording (MP4/WebM) shown on the detail page.",
    )
    thumbnail = models.ImageField(
        upload_to='modules/thumbs/', blank=True, null=True,
        help_text="Static preview image used as a fallback if no video is uploaded.",
    )

    industries = models.CharField(
        max_length=255, blank=True,
        help_text="Comma-separated industry tags, e.g. 'Retail, Restaurants, Hospitality'.",
    )

    # The "demo_code" controls which browser-frame mockup is shown on the
    # homepage tile when no video is uploaded. Recognised values:
    # pos, accounting, mrp, hr, ecommerce, crm, inventory, projects
    demo_code = models.CharField(max_length=40, default='pos')

    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=True, help_text="Show on the homepage module grid.")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_industries_list(self):
        return [s.strip() for s in self.industries.split(',') if s.strip()]