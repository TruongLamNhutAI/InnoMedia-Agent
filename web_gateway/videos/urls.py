from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # Đường dẫn gốc của app
    path('api/v1/task-status/<str:task_id>/', views.check_task_status, name='task_status'),
    path('api/v1/create-task/', views.create_video_task_ajax, name='create_task_ajax'),
    path('api/v1/get-script/<str:task_id>/', views.get_project_script, name='get_script'),
    path('api/v1/rerender/<str:task_id>/', views.update_and_rerender, name='rerender_video'),
]