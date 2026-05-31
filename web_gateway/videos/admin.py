from django.contrib import admin
from .models import VideoProject

@admin.register(VideoProject)
class VideoProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('original_url',)