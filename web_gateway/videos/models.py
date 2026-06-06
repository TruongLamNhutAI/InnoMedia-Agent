import uuid
from django.db import models

class VideoProject(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Đang chờ xử lý'),
        ('PROCESSING', 'Đang tạo Video'),
        ('SUCCESS', 'Hoàn tất'),
        ('FAILED', 'Thất bại'),
    ]

    # Tạo một ID ngẫu nhiên và an toàn cho mỗi dự án (tránh bị đoán URL)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lưu link gốc người dùng dán vào
    original_url = models.URLField(max_length=500)
    
    # Trạng thái hiện tại
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # ---> BỔ SUNG TRƯỜNG NÀY: Nơi lưu trữ toàn bộ kịch bản AI trả về <---
    script_data = models.JSONField(null=True, blank=True, verbose_name="Kịch bản AI (JSON)")
    
    # Đường dẫn file video sau khi render xong (lúc đầu sẽ trống)
    final_video_path = models.CharField(max_length=500, blank=True, null=True)
    
    # Lưu lại mã lỗi nếu có để dễ debug
    error_message = models.TextField(blank=True, null=True)
    
    # Thời gian tạo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.status}"