from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at', 'created_at')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'body', 'excerpt', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')