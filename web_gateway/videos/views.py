from django.shortcuts import render
from django.http import JsonResponse
from .tasks import process_video_pipeline
from .models import VideoProject # Nhập khẩu Bảng dữ liệu
from celery.result import AsyncResult
import json
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt # Tạm thời tắt check CSRF cho dễ test API
def create_video_task_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('product_url')
            
            # Tạo project mới trong DB
            project = VideoProject.objects.create(
                original_url=url,
                status='PENDING'
            )
            
            # Đẩy việc cho Celery
            task = process_video_pipeline.delay(str(project.id), url)
            
            # Trả về cả task_id (cho Celery) và project_id (cho Database)
            return JsonResponse({
                'status': 'success', 
                'task_id': task.id, 
                'project_id': str(project.id)
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def check_task_status(request, task_id):
    """
    API này nhận Task ID và đi hỏi Redis xem công việc làm đến đâu rồi.
    """
    task = AsyncResult(task_id)
    
    # Mặc định khi mới tạo
    response_data = {
        'state': task.state,
        'percent': 0,
        'message': 'Đang xếp hàng chờ xử lý...'
    }

    if task.state == 'PROGRESS':
        # Lấy dữ liệu ta vừa truyền vào self.update_state ở Bước 1
        response_data['percent'] = task.info.get('percent', 0)
        response_data['message'] = task.info.get('message', '')
    elif task.state == 'SUCCESS':
        response_data['percent'] = 100
        response_data['message'] = 'Video của bạn đã sẵn sàng!'
        # task.result chính là cái Dictionary mà mình return ở cuối process_video_pipeline, có chứa video_url nếu thành công
        if isinstance(task.result, dict):
            response_data['video_url'] = task.result.get('video_url', '')
    elif task.state == 'FAILURE':
        response_data['percent'] = 0
        # Xử lý lỗi nếu có
        error_info = task.info
        response_data['message'] = error_info.get('message', 'Đã xảy ra lỗi không xác định.') if isinstance(error_info, dict) else str(error_info)

    return JsonResponse(response_data)

from .tasks import process_video_pipeline, re_render_video_pipeline

@csrf_exempt
def get_project_script(request, task_id):
    """API dùng để Frontend lấy kịch bản cũ ra Form chỉnh sửa"""
    if request.method == 'GET':
        try:
            project = VideoProject.objects.get(id=task_id)
            if project.script_data:
                return JsonResponse({'status': 'success', 'script_data': project.script_data})
            return JsonResponse({'status': 'error', 'message': 'Chưa có kịch bản AI.'}, status=404)
        except VideoProject.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy dự án.'}, status=404)

@csrf_exempt
def update_and_rerender(request, task_id):
    """API nhận kịch bản đã sửa từ Frontend và kích hoạt render lại"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_script = data.get('script_data')
            
            project = VideoProject.objects.get(id=task_id)
            
            # Cập nhật kịch bản mới vào Database
            project.script_data = new_script
            project.status = 'PENDING' # Reset trạng thái về chờ xử lý
            project.save()
            
            # Gọi Task đi tắt (Re-render)
            task = re_render_video_pipeline.delay(str(project.id))
            
            # Trả về ID của Celery Task (Nó sẽ dùng chung ID của Project)
            return JsonResponse({
                'status': 'success', 
                'task_id': task.id, 
                'project_id': str(project.id)
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)