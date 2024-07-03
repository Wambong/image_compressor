from django.urls import path
from . import views

urlpatterns = [
    path('upload_folder', views.upload_folder, name='upload'),
    path('', views.select_directory, name='select_directory'),
]
