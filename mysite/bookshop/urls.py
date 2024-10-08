from django.urls import path

from . import views


urlpatterns = [
    path("upload/", views.upload_file, name="upload"),
    path("download_file/<int:book_id>/", views.download_file, name="download_file"),
    path("download_cover/<int:book_id>/", views.download_cover, name="download_cover"),
]