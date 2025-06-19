import psutil
from django.http import JsonResponse

def get_system_usage(request):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    return JsonResponse({'cpu': cpu, 'memory': memory})
