import uuid
from datetime import timedelta

from django.db import models
from django.utils.text import slugify
from django.utils import timezone


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
    tagline = models.CharField(
        max_length=200,
        default="ERP & Odoo Engineer · 2+ yrs building business systems",
    )
    phone = models.CharField(max_length=40, blank=True, default="+8801870460323")
    email = models.EmailField(blank=True, default="mostakimjihad652001@gmail.com")
    location = models.CharField(max_length=200, blank=True, default="Bawnia Bazar, Dhaka-1212, Bangladesh")
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    codeforces = models.URLField(blank=True)
    fiverr_url = models.URLField(blank=True, default="https://www.fiverr.com/your_gig")

    years_experience = models.PositiveIntegerField(default=2)
    projects_completed = models.PositiveIntegerField(default=8)
    happy_clients = models.PositiveIntegerField(default=10)

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
    image_url = models.URLField(
        blank=True,
        help_text="Optional hot-linked preview image (e.g. Unsplash) shown on the /modules/ tile. Falls back to the built-in mockup when empty.",
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

    @property
    def theme(self):
        """Map demo_code / category to a CSS theme class for visual variety on the
        products page. Returns one of: blue, green, purple, cyan, amber, rose,
        orange. Falls back to blue for unknown codes."""
        # Map by demo_code first (most specific)
        code_themes = {
            'pos':          'green',
            'inventory':    'cyan',
            'purchase':     'cyan',
            'mrp':          'orange',
            'accounting':   'purple',
            'hr':           'rose',
            'crm':          'blue',
            'ecommerce':    'green',
            'project':      'amber',
            'website':      'rose',
            'helpdesk':     'amber',
            'field-service':'blue',
            'subscriptions':'purple',
            'marketing':    'rose',
            'quality':      'orange',
            'expenses':     'amber',
        }
        if self.demo_code and self.demo_code in code_themes:
            return code_themes[self.demo_code]
        # Fallback to category
        cat_themes = {
            'operations':  'cyan',
            'sales':       'blue',
            'finance':     'purple',
            'people':      'rose',
            'web':         'green',
            'productivity':'amber',
        }
        return cat_themes.get(self.category, 'blue')


class PricingConfig(models.Model):
    """Singleton holding the pricing calculator catalog + exchange rate.

    `catalog` is a JSON blob: { tiers: [...], addons: [...] } so the
    owner can tweak prices from the admin without redeploying.
    """

    usd_to_bdt = models.DecimalField(
        max_digits=8, decimal_places=2, default=110,
        help_text="Exchange rate used by the calculator (1 USD = X BDT).",
    )
    intro_title = models.CharField(
        max_length=160,
        default="Estimate your project in under a minute",
    )
    intro_subtitle = models.TextField(
        blank=True,
        default="Transparent, competitive pricing. No hidden fees. Toggle USD ⇄ BDT to see both.",
    )
    catalog = models.JSONField(
        default=dict,
        help_text="Auto-seeded with default catalog on first save. Do not edit by hand unless you know the schema.",
    )

    class Meta:
        verbose_name = "Pricing Configuration"
        verbose_name_plural = "Pricing Configuration"

    def save(self, *args, **kwargs):
        self.pk = 1
        if not self.catalog:
            self.catalog = PricingConfig.default_catalog()
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Pricing Configuration"

    @staticmethod
    def default_catalog():
        return {
            "tiers": [
                {
                    "id": "small",
                    "name": "Small ERP",
                    "summary": "Up to 3 users · 1 company · core modules",
                    "price_usd": 590,
                    "popular": False,
                },
                {
                    "id": "medium",
                    "name": "Medium ERP",
                    "summary": "Up to 10 users · 1 company · standard modules",
                    "price_usd": 1490,
                    "popular": True,
                },
                {
                    "id": "large",
                    "name": "Large ERP",
                    "summary": "15+ users · multi-company · full suite",
                    "price_usd": 3490,
                    "popular": False,
                },
            ],
            "addons": [
                {"id": "deploy_community",  "name": "Odoo Community Deployment",   "summary": "Self-hosted on your server",                  "price_usd":  120, "unit": "flat"},
                {"id": "deploy_enterprise", "name": "Odoo Enterprise Deployment",  "summary": "SaaS / Odoo.sh setup + first 30 days",        "price_usd":  290, "unit": "flat"},
                {"id": "website",           "name": "Website / eCommerce pages",   "summary": "Theme + responsive pages",                    "price_usd":   35, "unit": "page"},
                {"id": "data_migration",    "name": "Data Migration",              "summary": "From Tally, QuickBooks, spreadsheets, etc.",  "price_usd":  190, "unit": "flat"},
                {"id": "consulting",        "name": "Functional Consulting",       "summary": "Discovery, gap analysis, blueprint",          "price_usd":   25, "unit": "hour"},
                {"id": "custom_module",     "name": "Custom Module Development",   "summary": "Bespoke Odoo module or automation",           "price_usd":  290, "unit": "module"},
                {"id": "training",          "name": "Team Training",               "summary": "Live walkthrough for end users",              "price_usd":   60, "unit": "session"},
                {"id": "maintenance",       "name": "Monthly Maintenance",         "summary": "Bug fixes, updates, minor changes",           "price_usd":  120, "unit": "month"},
            ],
            "discounts": [
                {"min_addons": 3, "percent": 10, "label": "Bundle 3+ add-ons"},
                {"min_addons": 5, "percent": 15, "label": "Bundle 5+ add-ons"},
            ],
        }


class QuoteLead(models.Model):
    """A lead captured from the /pricing/ calculator.

    Created when a user submits the customer form on the pricing page
    to download a PDF quote. Owner reviews these in Django admin and
    follows up. The full chosen items are stored as JSON so the admin
    can replay the exact configuration the user priced out.
    """

    STATUS_CHOICES = [
        ('new',       'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('won',       'Won'),
        ('lost',      'Lost'),
    ]

    CURRENCY_CHOICES = [('USD', 'USD'), ('BDT', 'BDT')]

    # Customer
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=160, blank=True)
    notes = models.TextField(blank=True, help_text="Optional message from the prospect.")

    # Quote configuration
    tier_id = models.CharField(max_length=40, blank=True)
    items = models.JSONField(default=list, help_text="[{id, name, qty, unit, unit_price_usd, line_total_usd}, ...]")
    subtotal_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.PositiveIntegerField(default=0)
    discount_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    usd_to_bdt = models.DecimalField(max_digits=8, decimal_places=2, default=110)

    # Generated PDF (re-renderable on demand; we also cache a copy)
    pdf = models.FileField(upload_to='quotes/', blank=True, null=True)

    # Tracking
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Quote lead"
        verbose_name_plural = "Quote leads"

    def __str__(self):
        return f"{self.name} — {self.currency} {self.total} ({self.get_status_display()})"

    @property
    def total(self):
        if self.currency == 'BDT':
            return f"৳{int(self.total_usd * self.usd_to_bdt):,}"
        return f"${int(self.total_usd):,}"

    def item_count(self):
        return len(self.items or [])


# ---------------------------------------------------------------------------
# Booking / Appointment system
# ---------------------------------------------------------------------------

class AvailabilityRule(models.Model):
    """Recurring weekly availability — one row per (weekday, time-range).

    Example: Sun-Thu 10:00-12:00 and 14:00-17:00 = 6 rows for those weekdays.
    """

    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['weekday', 'start_time']
        verbose_name = 'Availability rule'
        verbose_name_plural = 'Availability rules'

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time:%H:%M} – {self.end_time:%H:%M}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('start_time must be before end_time.')


class BlockedDate(models.Model):
    """A specific date (or partial day) when the owner is unavailable.

    Used for holidays, vacations, conferences. is_full_day = True blocks the
    entire date; otherwise the row is treated as a full-day block for now
    (partial-day support intentionally omitted to keep the model simple).
    """

    date = models.DateField(unique=True)
    label = models.CharField(
        max_length=120, blank=True,
        help_text='Optional reason, e.g. "Public holiday" or "Vacation".',
    )
    is_full_day = models.BooleanField(default=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Blocked date'
        verbose_name_plural = 'Blocked dates'

    def __str__(self):
        return f"{self.date} — {self.label or 'Blocked'}"


class Appointment(models.Model):
    """A confirmed (or cancelled) booking made through the calendar modal.

    `start_datetime` / `end_datetime` are stored in the project timezone
    (settings.TIME_ZONE, default Asia/Dhaka) and are timezone-aware.
    The `timezone` field captures the visitor's detected IANA zone so the
    confirmation email can show the booking in their local time.
    """

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    # Customer
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    company = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True, help_text='What they want to discuss on the call.')

    # Schedule
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    timezone = models.CharField(
        max_length=64, default='Asia/Dhaka',
        help_text="The visitor's IANA timezone, e.g. 'Europe/London'.",
    )

    # Lifecycle
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='confirmed')
    cancel_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    # Tracking
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        indexes = [
            models.Index(fields=['start_datetime', 'status']),
            models.Index(fields=['status']),
        ]
        constraints = [
            # A confirmed appointment may not share its exact start_datetime
            # with another confirmed appointment (no double-booking).
            models.UniqueConstraint(
                fields=['start_datetime'],
                condition=models.Q(status='confirmed'),
                name='unique_confirmed_start',
            ),
        ]

    def __str__(self):
        return f"{self.name} — {self.start_datetime:%Y-%m-%d %H:%M} ({self.get_status_display()})"

    @property
    def duration_minutes(self):
        return int((self.end_datetime - self.start_datetime).total_seconds() // 60)

    @property
    def is_upcoming(self):
        return self.status == 'confirmed' and self.start_datetime > timezone.now()

    def cancel(self, reason=''):
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason[:2000]
        self.save(update_fields=['status', 'cancelled_at', 'cancellation_reason', 'updated_at'])


# ---------------------------------------------------------------------------
# Slot helpers — pure functions used by views. Keep models thin.
# ---------------------------------------------------------------------------

def get_available_slots(target_date, slot_minutes=30):
    """Return a sorted list of slot start-times (timezone-aware datetimes)
    for `target_date` that are NOT blocked or already booked.

    All datetimes returned are in the project timezone (settings.TIME_ZONE).
    Past slots (relative to now) and slots that overlap any confirmed
    Appointment or BlockedDate are dropped.
    """
    from django.conf import settings as dj_settings

    tz = timezone.get_current_timezone()
    weekday = target_date.weekday()

    rules = AvailabilityRule.objects.filter(
        weekday=weekday, is_active=True,
    ).order_by('start_time')

    if not rules.exists():
        return []

    # Bookings + blocked dates that intersect this calendar day.
    day_start = timezone.make_aware(
        timezone.datetime.combine(target_date, timezone.datetime.min.time()),
        tz,
    ) if timezone.is_naive(timezone.datetime.combine(target_date, timezone.datetime.min.time())) \
        else timezone.datetime.combine(target_date, timezone.datetime.min.time()).replace(tzinfo=tz)

    day_end = day_start + timedelta(days=1)

    booked = set(
        Appointment.objects.filter(
            status='confirmed',
            start_datetime__lt=day_end,
            end_datetime__gt=day_start,
        ).values_list('start_datetime', 'end_datetime')
    )

    is_blocked = BlockedDate.objects.filter(date=target_date, is_full_day=True).exists()

    if is_blocked:
        return []

    now = timezone.now()
    step = timedelta(minutes=slot_minutes)
    slots = []

    for rule in rules:
        cursor = timezone.make_aware(
            timezone.datetime.combine(target_date, rule.start_time), tz,
        ) if timezone.is_naive(
            timezone.datetime.combine(target_date, rule.start_time)
        ) else timezone.datetime.combine(target_date, rule.start_time).replace(tzinfo=tz)

        rule_end = timezone.make_aware(
            timezone.datetime.combine(target_date, rule.end_time), tz,
        ) if timezone.is_naive(
            timezone.datetime.combine(target_date, rule.end_time)
        ) else timezone.datetime.combine(target_date, rule.end_time).replace(tzinfo=tz)

        # Snap the cursor forward to the next step boundary relative to rule start.
        # We assume rule start_time is already on a slot boundary (admin enforces this).
        while cursor + step <= rule_end:
            slot_start = cursor
            slot_end = cursor + step

            # Skip past slots
            if slot_start <= now:
                cursor += step
                continue

            # Skip overlapping bookings
            overlaps = any(
                b_start < slot_end and b_end > slot_start
                for b_start, b_end in booked
            )
            if overlaps:
                cursor += step
                continue

            slots.append(slot_start)
            cursor += step

    return slots


def month_has_any_availability(year, month):
    """Cheap check: does this month have *any* availability at all?

    Used to dim out months in the calendar picker that are entirely empty.
    """
    from calendar import monthrange

    _, last_day = monthrange(year, month)
    for day in range(1, last_day + 1):
        try:
            d = timezone.datetime(year, month, day).date()
        except ValueError:
            continue
        if d.weekday() in set(
            AvailabilityRule.objects.filter(is_active=True).values_list('weekday', flat=True)
        ) and not BlockedDate.objects.filter(date=d, is_full_day=True).exists():
            return True
    return False

