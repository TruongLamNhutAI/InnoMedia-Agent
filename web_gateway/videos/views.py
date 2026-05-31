from django.shortcuts import render
from django.http import JsonResponse
from .tasks import process_video_pipeline
from .models import VideoProject # Nhập khẩu Bảng dữ liệu

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            # 1. Tạo 1 dòng mới trong Database (Nó sẽ tự có ID và trạng thái PENDING)
            project = VideoProject.objects.create(original_url=url)
            
            # 2. Gửi ID (kèm url) cho Celery xử lý
            process_video_pipeline.delay(str(project.id), url)
            
            # Trả về ID cho người dùng để sau này họ có thể tra cứu
            return JsonResponse({
                'status': 'success', 
                'task_id': str(project.id), 
                'message': 'Đã tạo dự án và đưa vào hàng đợi!'
            })
        return JsonResponse({'status': 'error', 'message': 'URL không hợp lệ'})
        
    return render(request, 'videos/index.html')