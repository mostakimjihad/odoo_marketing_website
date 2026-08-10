from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse

from .models import SiteSettings, Service, ContactInquiry, ERPModule


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Singleton — only one row, no add/delete buttons."""

    fieldsets = (
        ("Hero section", {
            'fields': ('hero_title', 'hero_subtitle', 'hero_cta_text', 'hero_cta_secondary_text', 'hero_video'),
        }),
        ("About section", {
            'fields': ('about_title', 'about_body', 'profile_image', 'cv_file'),
        }),
        ("Identity", {
            'fields': ('full_name', 'tagline', 'phone', 'email', 'location'),
        }),
        ("Social", {
            'fields': ('linkedin', 'github', 'codeforces', 'fiverr_url'),
        }),
        ("Stats counters (homepage)", {
            'fields': ('years_experience', 'projects_completed', 'happy_clients'),
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Redirect straight to the (single) edit page.
        obj = SiteSettings.get_solo()
        return HttpResponseRedirect(reverse('admin:core_sitesettings_change', args=[obj.pk]))


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'slug')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service', 'budget', 'created_at', 'is_read')
    list_filter = ('is_read', 'service', 'budget', 'created_at')
    search_fields = ('name', 'email', 'company', 'message')
    readonly_fields = ('name', 'email', 'phone', 'company', 'service', 'budget', 'message', 'created_at')
    list_editable = ('is_read',)

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description="Mark selected inquiries as read")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description="Mark selected inquiries as unread")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)

    def has_add_permission(self, request):
        return False


@admin.register(ERPModule)
class ERPModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_tag', 'category', 'order', 'is_featured', 'is_published')
    list_display_links = ('name',)
    list_editable = ('order', 'is_featured', 'is_published')
    list_filter = ('category', 'is_featured', 'is_published')
    search_fields = ('name', 'tagline', 'description', 'industries')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'short_tag', 'category', 'order'),
        }),
        ('Tile content (homepage)', {
            'fields': ('tagline', 'industries', 'demo_code', 'thumbnail'),
            'description': 'demo_code picks the browser-frame mockup shown when no video is uploaded. Valid: pos, accounting, mrp, hr, ecommerce, crm, inventory, projects.',
        }),
        ('Detail page', {
            'fields': ('description', 'demo_video'),
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_published'),
        }),
    )