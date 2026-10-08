from django.contrib import admin

from .models import CaseStudy, SuccessProject, Client, Certification


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'client_name', 'is_featured', 'is_published', 'completed_at', 'order')
    list_editable = ('is_featured', 'is_published', 'order')
    list_filter = ('is_published', 'is_featured', 'industry')
    search_fields = ('title', 'client_name', 'problem', 'solution')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'completed_at'


@admin.register(SuccessProject)
class SuccessProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_featured', 'is_published', 'completed_at', 'order')
    list_editable = ('is_featured', 'is_published', 'order')
    list_filter = ('is_published', 'is_featured')
    search_fields = ('title', 'description', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'completed_at'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    list_filter = ('is_featured', 'industry')
    search_fields = ('name', 'industry', 'testimonial')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'issue_date', 'order')
    list_editable = ('order',)
    list_filter = ('issuer',)
    search_fields = ('title', 'issuer', 'credential_id')
    date_hierarchy = 'issue_date'