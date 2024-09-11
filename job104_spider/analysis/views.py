from django.shortcuts import render
from .job104_spider import Job104Spider

# Create your views here.
def index(request):
    total_count = request.session.get('total_count', 0)
    keyword = request.session.get('keyword', '')

    return render(request, 'analysis/index.html', {
        'total_count': total_count,
        'keyword': keyword
    })