from .models import Bidang

def bidang_context(request):
    return {
        'bidang_list': Bidang.objects.all()
    }
