from django.shortcuts import render
from .job104_spider import Job104Spider
from django.core.paginator import Paginator
import json
import subprocess

# Create your views here.
def index(request):
    total_count = request.session.get('total_count', 0)
    keyword = request.session.get('keyword', '')

    return render(request, 'analysis/index.html', {
        'total_count': total_count,
        'keyword': keyword
    })

def search(request):
    # Check if it's a new search or a pagination request
    if request.method == 'POST':
        # New search request
        keyword = request.POST.get('keyword')
        job_spider = Job104Spider()
        total_count, jobs = job_spider.search(keyword, max_num=100)
        transformed_jobs = [job_spider.search_job_transform(job) for job in jobs]

        # Store the search results in the session
        request.session['results'] = transformed_jobs
        request.session['total_count'] = total_count
        request.session['keyword'] = keyword
    else:
        # Pagination request, use the session-stored data
        transformed_jobs = request.session.get('results', [])
        total_count = request.session.get('total_count', 0)
        keyword = request.session.get('keyword', '')

    # Handle pagination
    paginator = Paginator(transformed_jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'analysis/index.html', {
        'page_obj': page_obj,
        'total_count': total_count,
        'keyword': keyword
    })

def run_job_fitter(request):
    if request.method == 'POST':
        skills = request.POST.get('skills')
        current_data = request.session.get('results', [])

        with open('current_jobs.json', 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)

        result = subprocess.run(
            ['python', 'analysis/job_fitter_doc2vec.py', skills, 'current_jobs.json'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Check if the result is empty or has errors
        if result.returncode != 0:
            return render(request, 'analysis/index.html', {
                'fitter_results': f"Error running job fitter: {result.stderr}"
            })
        
        # Check if the stdout contains valid JSON
        try:
            fitter_results = json.loads(result.stdout) if result.stdout else "No output from job fitter."
        except json.JSONDecodeError:
            fitter_results = f"Invalid JSON output: {result.stdout}"

        # Store the fitter results in the session
        request.session['fitter_results'] = fitter_results

        return render(request, 'analysis/index.html', {
            'fitter_results': fitter_results
        })
    else:
        return render(request, 'analysis/index.html')