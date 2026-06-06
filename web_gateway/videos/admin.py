from django.contrib import admin
from .models import VideoProject

@admin.register(VideoProject)
class VideoProjectAdmin(admin.ModelAdmin):
    # Các cột sẽ hiển thị ra bảng
    list_display = ('short_id', 'short_url', 'status', 'created_at')
    
    # Bật bộ lọc (Filter) bên tay phải
    list_filter = ('status', 'created_at')
    
    # Thanh tìm kiếm (Tìm theo ID hoặc Link)
    search_fields = ('id', 'original_url')
    
    # Mặc định sắp xếp: Mới nhất lên đầu
    ordering = ('-created_at',)

    # Hàm tự tạo: Rút gọn ID cho đỡ rối mắt
    def short_id(self, obj):
        return str(obj.id)[:8].upper()
    short_id.short_description = "Mã Dự Án"

    # Hàm tự tạo: Hiển thị 40 ký tự đầu của Link Shopee
    def short_url(self, obj):
        if obj.original_url:
            return obj.original_url[:40] + "..." if len(obj.original_url) > 40 else obj.original_url
        return "N/A"
    short_url.short_description = "Link Sản Phẩm"