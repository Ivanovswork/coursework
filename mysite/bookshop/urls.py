from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import AuthorsViewSet, CompaniesViewSet

router = DefaultRouter()
router.register(r'author', AuthorsViewSet)
router.register(r'company', CompaniesViewSet)

urlpatterns = [
    # path("upload/", views.upload_file, name="upload"),
    # path("download_file/<id>/", views.download_file, name="download_file"),
    path("confirm/<key>/", views.confirm_email, name="email confirmation"),
    path("reg/", views.RegistrUserView.as_view(), name="registration"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("change_password/", views.change_password, name="change_password"),
    path("make_user_staff/", views.make_it_staff, name="make_user_staff"),
    path("delete_staff_status/", views.delete_staff_status, name="delete_staff_status"),
    path("group/", views.GroupView.as_view(), name="group"),
    path("genre/", views.GenresView.as_view(), name="genre"),
    path("genre_to_group/", views.add_genre_to_group, name="genre_to_group"),
    path("group_genre/", views.group_genre, name="group_genre"),
    path("genre_from_group/", views.delete_genre_from_group, name="genre_from_group"),
    path('', include(router.urls)),
]