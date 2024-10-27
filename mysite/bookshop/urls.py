from django.urls import path

from . import views


urlpatterns = [
    path("upload/", views.upload_file, name="upload"),
    path("download_file/<id>/", views.download_file, name="download_file"),
    path("confirm/<key>/", views.confirm_email, name="email confirmation"),
    path("reg/", views.RegistrUserView.as_view(), name="registration"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("change_password/", views.change_password, name="change_password"),
    path("make_user_staff/", views.make_it_staff, name="make_user_staff"),
    path("delete_staff_status/", views.delete_staff_status, name="delete_staff_status"),
    path("group/", views.GroupView.as_view(), name="group")
]