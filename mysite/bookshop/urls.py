from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import AuthorsViewSet, CompaniesViewSet, BookCommentsViewSet, AuthorCommentsViewSet, \
    AuthorComplaintsViewSet, BookComplaintsViewSet, CommentComplaintsViewSet, UserViewSet, BookViewSet, BasketViewSet, \
    PurchasesViewSet, PersonalLibraryViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r'author', AuthorsViewSet)
router.register(r'company', CompaniesViewSet)
router.register(r'book_comment', BookCommentsViewSet)
router.register(r'author_comment', AuthorCommentsViewSet)
router.register(r'author_complaint', AuthorComplaintsViewSet, basename="author_complaint")
router.register(r'book_complaint', BookComplaintsViewSet, basename="book_complaint")
router.register(r'comment_complaint', CommentComplaintsViewSet, basename="comment_complaint")
router.register(r'user', UserViewSet)
router.register(r'book', BookViewSet)
router.register(r'basket', BasketViewSet)
router.register(r'library', PersonalLibraryViewSet, basename="library")
router.register(r'purchases', PurchasesViewSet)

urlpatterns = [
    # path("upload/", views.upload_file, name="upload"),
    # path("download_file/<id>/", views.download_file, name="download_file"),
    path("user/confirm/<key>/", views.confirm_email, name="email confirmation"),
    path("user/reg/", views.RegistrUserView.as_view(), name="registration"),
    path("user/login/", views.login, name="login"),
    path("user/logout/", views.logout, name="logout"),
    path("user/change_password/", views.change_password, name="change_password"),
    path("user/user_staff/", views.make_it_staff, name="make_user_staff"),
    path("user/delete_staff_status/", views.delete_staff_status, name="delete_staff_status"),
    path("group/", views.GroupView.as_view(), name="group"),
    path("genre/", views.GenresView.as_view(), name="genre"),
    path("genre_to_group/", views.add_genre_to_group, name="genre_to_group"),
    path("group_genre/", views.group_genre, name="group_genre"),
    path("genre_from_group/", views.delete_genre_from_group, name="genre_from_group"),
    path("favorite_genres/", views.FavoriteGTView.as_view(), name="favorite_genres"),
    path("favorite_authors/", views.FavoriteAuthorsView.as_view(), name="favorite_authors"),
    path("support_message/", views.SupportMessagesView.as_view(), name="support_message"),
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]