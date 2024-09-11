from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('run_job_fitter/', views.run_job_fitter, name='run_job_fitter'),
]