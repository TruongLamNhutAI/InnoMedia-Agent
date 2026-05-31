import os
from celery import Celery

# Báo cho Celery biết file cấu hình của Django nằm ở đâu
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Nạp toàn bộ cấu hình có tiền tố 'CELERY_' từ settings.py vào Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động quét và tìm các file 'tasks.py' trong các App của Django
app.autodiscover_tasks()