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

def search(request):
    keyword = request.POST.get('keyword')
    job_spider = Job104Spider()
    total_count, jobs = job_spider.search(keyword, max_num=100)
    transformed_jobs = [job_spider.search_job_transform(job) for job in jobs]

    # Store the search results in the session
    request.session['results'] = transformed_jobs
    request.session['total_count'] = total_count
    request.session['keyword'] = keyword

    return render(request, 'analysis/index.html', {
        'results': transformed_jobs,
        'total_count': total_count,
        'keyword': keyword
    })
