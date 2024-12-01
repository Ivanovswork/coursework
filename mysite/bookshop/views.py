import ast
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Books, User, ConfirmEmailKey, Groups, Genres, Authors, Companies, Support_Messages, Comments, \
    Comments_Books, Comments_Authors, Relations_books, Purchases
from .email_class import Email
from .permissions import IsStaff, IsSuperuser
from .serializers import UserChangePasswordSerializer, UserToStaffSerializer, UserDeleteStaffStatusSerializer, \
    GroupSerializer, PatchGroupSerializer, PostDeleteGroupSerializer, GenreSerializer, PostDeleteGenreSerializer, \
    PatchGenreSerializer, AddGenreToGroupSerializer, DeleteGenreFromGroupSerializer, AuthorSerializer, \
    CompaniesSerializer, PatchAuthorSerializer, PatchCompanySerializer, MessageSerializer, BookCommentsSerializer, \
    CommentSerializer, AuthorCommentsSerializer, BooksCommentsSerializer, AuthorsCommentsSerializer, \
    AuthorComplaintSerializer, BookComplaintSerializer, CommentComplaintSerializer, \
    CommentComplaintPresentationSerializer, UserSerializer, BookSerializer, GetBookSerializer, PatchBookSerializer, \
    AddBookAuthorSerializer, DeleteBookAuthorSerializer, DeleteBookGenreSerializer, AddBookGenreSerializer, \
    CreateBasketSerializer, BasketPositionSerializer, DeleteBasketSerializer, CreatePurchaseSerializer, \
    PurchaseSerializer

from .serializers import UserRGSTRSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# import threading
# import datetime
#
#
# def my_function():
#     print(f"Функция выполнена в {datetime.datetime.now()}")
#     # Запускаем таймер снова
#     start_timer()
#
#
# def start_timer():
#     # Устанавливаем интервал в 60 секунд
#     interval = 60
#     timer = threading.Timer(interval, my_function)
#     timer.start()
#
#
# # Запускаем таймер при старте приложения
# start_timer()


def is_owner(request):
    try:
        email = request.data.get("email")
        if email == request.user.email:
            return True
        return False
    except Exception as e:
        return False


def is_staff_this_company(request):
    try:
        company = request.data.get("company")
        print(company)
        print(request.user.company)
        if company == request.user.company.pk:
            return True
        return False
    except Exception as e:
        return False


class RegistrUserView(APIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRGSTRSerializer

    def post(self, request, *args, **kwargs):
        user = UserRGSTRSerializer(data=request.data)

        if user.is_valid():
            user = user.save()
            key = ConfirmEmailKey(user=user)
            key.save()

            Email.send_email(key.key, user.email)

            return Response(
                {"status": "Registration has been done"}, status=status.HTTP_200_OK
            )
        return Response(user.errors)


@api_view()
def confirm_email(request, key, *args, **kwargs):
    user_key = ConfirmEmailKey.objects.filter(key=key).first()
    if user_key:
        user = user_key.user
        user.is_active = True
        user.save()
        return Response(
            {"status": "email has been confirmed"}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"status": "User with this key not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request, *args, **kwargs):
    if request.method == "POST":
        try:
            email, password = request.data.get("email"), request.data.get("password")
        except Exception as e:
            return Response(
                {"status": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(email=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)

        return Response(
            {"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request, *args, **kwargs):
    if request.method == "POST":
        try:
            request.user.auth_token.delete()
            return Response(
                {"status": "Logout has been completed"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"status": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request, *args, **kwargs):
    user = UserChangePasswordSerializer(data=request.data)
    if request.method == "PUT":
        if user.is_valid() and is_owner(request):
            try:
                user.save()
                return Response(
                    {"status": "Changing password has been completed"}, status=status.HTTP_200_OK
                )
            except ValidationError:
                pass

    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
def make_it_staff(request):
    user = UserToStaffSerializer(data=request.data)
    if request.method == 'POST' and user.is_valid():
        user.save()
        return Response({"status": "User is staff now"}, status=status.HTTP_200_OK)
    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_staff_status(request):
    user = UserDeleteStaffStatusSerializer(data=request.data)
    if request.method == 'POST' and user.is_valid():
        user.save()
        return Response({"status": "Now user is not staff"}, status=status.HTTP_200_OK)
    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperuser]

    def create(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk=None, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, pk=None, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch'], detail=True)
    def block(self, request, pk=None, *args, **kwargs):
        try:
            user = self.queryset.filter(pk=pk).first()
            user.chat = False
            user.save()
            return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def unblock(self, request, pk=None, *args, **kwargs):
        try:
            user = self.queryset.filter(pk=pk).first()
            user.chat = True
            user.save()
            return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        else:
            return [IsSuperuser()]

    def get(self, request):
        groups = Groups.objects.all()
        serializer = GroupSerializer(groups, many=True).data
        # print(serializer)
        # response = {}
        # for i in range(len(serializer)):
        #     response[serializer[i]["id"]] = serializer[i]["name"]
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request):
        group = PostDeleteGroupSerializer(data=request.data)
        if group.is_valid():
            group.save()
            return Response(group.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        group = PatchGroupSerializer(data=request.data)

        if group.is_valid(raise_exception=True):
            group.save()
            return Response(group.data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        group = PostDeleteGroupSerializer(data=request.data)
        if group.is_valid():
            group = Groups.objects.filter(name=request.data["name"])
            if group.exists():
                group.delete()
                return Response({"status": "Group is deleted"}, status=status.HTTP_200_OK)
            return Response({"status": "Group with this name is not exist"}, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class GenresView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        else:
            return [IsSuperuser()]

    def get(self, request):
        genres = Genres.objects.all()
        serializer = GenreSerializer(genres, many=True).data
        # print(serializer)
        # response = {}
        # for i in range(len(serializer)):
        #     response[serializer[i]["id"]] = serializer[i]["name"]
        return Response(serializer, status=status.HTTP_200_OK)

    def post(self, request):
        genre = PostDeleteGenreSerializer(data=request.data)
        if genre.is_valid():
            genre.save()
            return Response(genre.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        genre = PatchGenreSerializer(data=request.data)

        if genre.is_valid(raise_exception=True):
            genre.save()
            return Response(genre.data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        genre = PostDeleteGroupSerializer(data=request.data)
        if genre.is_valid():
            genre = Genres.objects.filter(name=request.data["name"])
            if genre.exists():
                genre.delete()
                return Response({"status": "Genre is deleted"}, status=status.HTTP_200_OK)
            return Response({"status": "Genre with this name is not exist"}, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
def add_genre_to_group(request):
    genre = AddGenreToGroupSerializer(data=request.data)
    if request.method == 'POST' and genre.is_valid():
        genre.save()
        return Response({"status": "Genre added to the group"}, status=status.HTTP_200_OK)
    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def group_genre(request):
    groups = Groups.objects.all()
    response = []
    for group in groups:
        res = {}
        service = {}
        print(group)
        print(group.genres.all())
        for genre in group.genres.all():
            service[f"{genre.pk}"] = genre.name
        res[group.name] = service
        response.append(res)
    # return JsonResponse(response, status=status.HTTP_200_OK, json_dumps_params={'ensure_ascii': False})
    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
def delete_genre_from_group(request):
    genre = DeleteGenreFromGroupSerializer(data=request.data)
    if request.method == 'POST' and genre.is_valid():
        genre.save()
        return Response({"status": "Genre deleted to the group"}, status=status.HTTP_200_OK)
    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class AuthorsViewSet(viewsets.ModelViewSet):
    queryset = Authors.objects.all()
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsStaff()]
        elif self.action in ["partial_update", "delete"]:
            return [IsAuthenticated(), IsSuperuser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return PatchAuthorSerializer
        return AuthorSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.is_superuser:
            serializer.validated_data["status"] = "active"
            serializer.save()
        else:
            serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, **kwargs):
        author = get_object_or_404(self.queryset, pk=pk)
        if author.status != "active" and request.user:
            if request.user.is_superuser:
                serializer = self.get_serializer(author)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            if author.status in ["rejected", "blocked", "request"]:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        if request.user:
            if request.user.is_superuser:
                query = self.queryset.all()
                serializer = self.get_serializer(query, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        query = self.queryset.filter(status="active")
        serializer = self.get_serializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            author = get_object_or_404(self.queryset, pk=pk)
            serializer = self.get_serializer(author, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            author = get_object_or_404(self.queryset, pk=pk)
            author.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['patch'])
    def block(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            author = get_object_or_404(self.queryset, pk=pk)
            if author.status != "active":
                return Response({"status": "Author status is not active"}, status=status.HTTP_403_FORBIDDEN)
            author.status = "blocked"
            author.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['patch'])
    def unblock(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            author = get_object_or_404(self.queryset, pk=pk)
            if author.status != "blocked":
                return Response({"status": "Author status is not request"}, status=status.HTTP_403_FORBIDDEN)
            author.status = "active"
            author.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['patch'])
    def accept(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            author = get_object_or_404(self.queryset, pk=pk)
            if author.status != "request":
                return Response({"status": "Author status is not request"}, status=status.HTTP_403_FORBIDDEN)
            author.status = "active"
            author.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            if request.data["reason"]:
                author = get_object_or_404(self.queryset, pk=pk)
                if author.status != "request":
                    return Response({"status": "Author status is not request"}, status=status.HTTP_403_FORBIDDEN)
                author.status = "rejected"
                author.reason = request.data["reason"]
                author.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CompaniesViewSet(viewsets.ModelViewSet):
    queryset = Companies.objects.all()
    permission_classes = [IsAuthenticated, IsSuperuser]

    def get_serializer_class(self):
        if self.action == "partial_update":
            return PatchCompanySerializer
        return CompaniesSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.data["name"] and request.data["status"]:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, **kwargs):
        if request.user.is_superuser:
            company = get_object_or_404(self.queryset, pk=pk)
            serializer = self.get_serializer(company)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            query = self.queryset.all()
            serializer = self.get_serializer(query, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            company = get_object_or_404(self.queryset, pk=pk)
            serializer = self.get_serializer(company, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            company = get_object_or_404(self.queryset, pk=pk)
            company.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FavoriteGTView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        genres = user.favorite_g.all()
        serializer = GenreSerializer(genres, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        print(user)
        try:
            genre = request.data["genre_name"]
            user.favorite_g.add(Genres.objects.filter(name=genre).first())
            user.save()
            return Response({"status": "Genre added"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        print(user)
        try:
            genre = request.data["genre_name"]
            user.favorite_g.remove(Genres.objects.filter(name=genre).first())
            user.save()
            return Response({"status": "Genre deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class FavoriteAuthorsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        authors = user.favorite_a.all()
        serializer = GenreSerializer(authors, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        print(user)
        try:
            author = request.data["author_id"]
            user.favorite_a.add(Authors.objects.filter(pk=author).first())
            user.save()
            return Response({"status": "Author added"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        print(user)
        try:
            author = request.data["author_id"]
            user.favorite_a.remove(Authors.objects.filter(pk=author).first())
            user.save()
            return Response({"status": "Author deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class SupportMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_superuser:
            print("a")
            try:
                chat_owner = User.objects.filter(pk=request.data["owner"]).first()
                text = request.data["text"]
                print(chat_owner)
                message = Support_Messages.objects.create(user=user, owner=chat_owner, text=text)
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                text = request.data["text"]
                print(text)
                message = Support_Messages.objects.create(user=user, owner=user, text=text)
                print(message)
                serializer = MessageSerializer(message)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        user = request.user
        if user.is_superuser:
            try:
                chat_owner = User.objects.filter(pk=request.data["owner"]).first()
                messages = Support_Messages.objects.filter(owner=chat_owner).order_by("date_time")
                serializer = MessageSerializer(messages, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                messages = Support_Messages.objects.filter(owner=user).order_by("date_time")
                serializer = MessageSerializer(messages, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class BookCommentsViewSet(viewsets.ModelViewSet):
    queryset = Comments_Books.objects.all()
    q = Comments.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookCommentsSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid(raise_exception=True):
            serializer = CommentSerializer(serializer.save(user=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.is_superuser:
            try:
                comment = Comments_Books.objects.select_related("comment").filter(pk=pk,
                                                                                  comment__type="feedback").first()
                # print(comment)
                if comment:
                    serializer = BooksCommentsSerializer(comment)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            comment = get_object_or_404(self.q, pk=pk)
            if request.user == comment.user or request.user.is_superuser:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def comments_by_book(self, request, pk=None, *args, **kwargs):
        try:
            book = pk
            if Books.objects.filter(pk=book).exists():
                comments = Comments_Books.objects.select_related("comment").filter(book=book,
                                                                                   comment__type="feedback")
                # print(comments)
                serializer = BooksCommentsSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def comments_book_by_user(self, request, pk=True, *args, **kwargs):
        if request.user.is_superuser:
            try:
                user = pk
                if User.objects.filter(id=user).exists():
                    comments = Comments_Books.objects.select_related("comment").filter(comment__user=user,
                                                                                       comment__type="feedback")
                    # print(comments)
                    serializer = BooksCommentsSerializer(comments, many=True)
                    # print(serializer.data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AuthorCommentsViewSet(viewsets.ModelViewSet):
    queryset = Comments_Authors.objects.all()
    q = Comments.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AuthorCommentsSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid(raise_exception=True):
            serializer = CommentSerializer(serializer.save(user=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.is_superuser:
            try:
                comment = Comments_Authors.objects.select_related("comment").filter(pk=pk,
                                                                                    comment__type="feedback").first()
                # print(comment)
                if comment:
                    serializer = AuthorsCommentsSerializer(comment)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            comment = get_object_or_404(self.q, pk=pk)
            if request.user == comment.user or request.user.is_superuser:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def comments_by_author(self, request, pk=True, *args, **kwargs):
        try:
            author = pk
            if Authors.objects.filter(pk=author).exists():
                comments = Comments_Authors.objects.select_related("comment").filter(author=author,
                                                                                     comment__type="feedback")
                # print(comments)
                serializer = AuthorsCommentsSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def comments_author_by_user(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            try:
                user = pk
                if User.objects.filter(id=user).exists():
                    comments = Comments_Authors.objects.select_related("comment").filter(comment__user=user,
                                                                                         comment__type="feedback")
                    # print(comments)
                    serializer = AuthorsCommentsSerializer(comments, many=True)
                    # print(serializer.data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class AuthorComplaintsViewSet(viewsets.ModelViewSet):
    queryset = Comments_Authors.objects.all()
    q = Comments.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AuthorComplaintSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid(raise_exception=True):
            serializer = CommentSerializer(serializer.save(user=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.is_superuser:
            try:
                comment = Comments_Authors.objects.select_related("comment").filter(pk=pk,
                                                                                    comment__type="complaint").first()
                # print(comment)
                if comment:
                    serializer = AuthorsCommentsSerializer(comment)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            comment = get_object_or_404(self.q, pk=pk)
            if request.user == comment.user or request.user.is_superuser:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def complaints_by_author(self, request, pk=None, *args, **kwargs):
        try:
            author = pk
            if Authors.objects.filter(pk=author).exists():
                comments = Comments_Authors.objects.select_related("comment").filter(author=author,
                                                                                     comment__type="complaint")
                # print(comments)
                serializer = AuthorsCommentsSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def complaints_author_by_user(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            try:
                user = pk
                if User.objects.filter(id=user).exists():
                    comments = Comments_Authors.objects.select_related("comment").filter(comment__user=user,
                                                                                         comment__type="complaint")
                    # print(comments)
                    serializer = AuthorsCommentsSerializer(comments, many=True)
                    # print(serializer.data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class BookComplaintsViewSet(viewsets.ModelViewSet):
    queryset = Comments_Books.objects.all()
    q = Comments.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookComplaintSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid(raise_exception=True):
            serializer = CommentSerializer(serializer.save(user=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.is_superuser:
            try:
                comment = Comments_Books.objects.select_related("comment").filter(pk=pk,
                                                                                  comment__type="complaint").first()
                # print(comment)
                if comment:
                    serializer = BooksCommentsSerializer(comment)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            comment = get_object_or_404(self.q, pk=pk)
            if request.user == comment.user or request.user.is_superuser:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def complaints_by_book(self, request, pk=None, *args, **kwargs):
        try:
            book = pk
            if Books.objects.filter(pk=book).exists():
                comments = Comments_Books.objects.select_related("comment").filter(book=book,
                                                                                   comment__type="complaint")
                # print(comments)
                serializer = BooksCommentsSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def complaints_book_by_user(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            try:
                user = pk
                if User.objects.filter(id=user).exists():
                    comments = Comments_Books.objects.select_related("comment").filter(comment__user=user,
                                                                                       comment__type="complaint")
                    # print(comments)
                    serializer = BooksCommentsSerializer(comments, many=True)
                    # print(serializer.data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentComplaintsViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CommentComplaintSerializer

    def create(self, request, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid(raise_exception=True):
            serializer = CommentComplaintPresentationSerializer(serializer.save(user=request.user))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.user.is_superuser:
            try:
                comment = Comments.objects.filter(pk=pk, type="complaint").first()
                # print(comment)
                if comment:
                    # print(comment)
                    serializer = CommentComplaintPresentationSerializer(comment)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        if not request.user.chat:
            return Response({"status": "Comments is blocked"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        try:
            comment = Comments.objects.filter(pk=pk, type="complaint").first()
            if request.user == comment.user or request.user.is_superuser:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def complaints_by_comment(self, request, pk=None, *args, **kwargs):
        try:
            comment_id = pk
            if Comments.objects.filter(pk=comment_id).exists():
                comments = Comments.objects.filter(parent=comment_id, type="complaint")
                # print(comments)
                serializer = CommentComplaintPresentationSerializer(comments, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def complaints_comment_by_user(self, request, pk=None, *args, **kwargs):
        if request.user.is_superuser:
            try:
                user = pk
                if User.objects.filter(id=user).exists():
                    comments = Comments.objects.filter(user=user, type="complaint")
                    # print(comments)
                    serializer = CommentComplaintPresentationSerializer(comments, many=True)
                    # print(serializer.data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all()
    serializer_class = GetBookSerializer

    def get_permissions(self):
        if self.action in ["create", "retrieve", "company_requests", "requests"]:
            return [IsAuthenticated(), IsStaff()]
        elif self.action in ["partial_update"]:
            return [IsAuthenticated(), IsSuperuser()]
        else:
            return [AllowAny()]

    def create(self, request, *args, **kwargs):
        user = request.user
        print(user.is_superuser)
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if user.is_superuser:
                try:
                    serializer = GetBookSerializer(serializer.save(company_id=request.data["company_id"]))
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except Exception:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = GetBookSerializer(serializer.save(user=user))
                return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        book = get_object_or_404(self.queryset, pk=pk)

        user = request.user

        if user.is_superuser or (user.is_staff and user.company == book.company):
            serializer = GetBookSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif book.status not in ["request", "blocked", "rejected"]:
            serializer = GetBookSerializer(book)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def list(self, request, *args, **kwargs):
        page = request.GET.get("page")
        books = Books.objects.filter(status__in=["released", "coming soon"]).order_by("priority")

        book_paginator = Paginator(books, 4)

        result = []
        try:
            page_book = book_paginator.page(page)
        except PageNotAnInteger:
            page_book = book_paginator.page(1)
        except EmptyPage:
            page_book = book_paginator.page(book_paginator.num_pages)

        for elem in page_book.object_list.values():
            result.append(GetBookSerializer(Books.objects.filter(pk=elem["id"]).first()).data)

        return JsonResponse({
            'objects': result,
            'current_page': page_book.number,
            'total_pages': book_paginator.num_pages,
            'has_next': page_book.has_next(),
            'has_previous': page_book.has_previous(),
        },
            json_dumps_params={'ensure_ascii': False})

    def partial_update(self, request, pk=None, *args, **kwargs):
        book = get_object_or_404(self.queryset, pk=pk)
        serializer = PatchBookSerializer(book, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = GetBookSerializer(serializer.save())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
        Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, pk=None, *args, **kwargs):
        Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get'], detail=False)
    def requests(self, request):
        user = request.user

        if user.is_superuser:
            books = Books.objects.filter(status="request")
            serializer = GetBookSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.is_staff:
            books = Books.objects.filter(status="request", company=user.company)
            serializer = GetBookSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get'], detail=True)
    def company_requests(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            if not Companies.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

            company = Companies.objects.filter(pk=pk).first()
            books = Books.objects.filter(status="request", company=company)
            serializer = GetBookSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['get'], detail=True)
    def company_books(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            if not Companies.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

            company = Companies.objects.filter(pk=pk).first()
            books = Books.objects.filter(company=company)
            serializer = GetBookSerializer(books, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.is_staff:
            if not Companies.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            company = Companies.objects.filter(pk=pk).first()
            if user.company == company:
                books = Books.objects.filter(company=company)
                serializer = GetBookSerializer(books, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch'], detail=True)
    def accept_book(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            if not Books.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            book = Books.objects.filter(pk=pk).first()
            if book.status in ["released", "coming soon", "blocked", "rejected"]:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            if book.file:
                book.status = "released"
            else:
                book.status = "coming soon"
            authors = book.authors.all()
            print(authors)
            for author in authors:
                author.status = "active"
                author.save()
            print(authors)
            book.save()
            return Response(GetBookSerializer(book).data, status=status.HTTP_200_OK)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch'], detail=True)
    def reject_book(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            if not Books.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            book = Books.objects.filter(pk=pk).first()
            if book.status in ["released", "coming soon", "blocked", "rejected"]:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reason = request.data["reason"]
                book.reason = reason
                book.status = "rejected"
                book.save()
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(GetBookSerializer(book).data, status=status.HTTP_200_OK)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch'], detail=True)
    def block_book(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            if not Books.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            book = Books.objects.filter(pk=pk).first()
            if book.status in ["rejected", "blocked", "request"]:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reason = request.data["reason"]
                book.reason = reason
                book.status = "blocked"
                book.save()
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(GetBookSerializer(book).data, status=status.HTTP_200_OK)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch'], detail=True)
    def unblock_book(self, request, pk=None):
        user = request.user
        if user.is_superuser:
            if not Books.objects.filter(pk=pk).exists():
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            book = Books.objects.filter(pk=pk).first()
            if book.status in ["released", "coming soon", "rejected", "request"]:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            if book.file:
                book.status = "released"
            else:
                book.status = "coming soon"
            book.reason = None
            book.save()
            return Response(GetBookSerializer(book).data, status=status.HTTP_200_OK)
        return Response({"status": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['patch'], detail=True)
    def upload_file(self, request, pk=None):
        user = request.user
        if request.method == 'PATCH':
            try:
                book = Books.objects.filter(pk=pk).first()
            except Exception:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
            if book and book.company == user.company and book.status in ["request", "coming soon"]:
                print(request.FILES)
                file = request.FILES['file']
                file_str = file.read()
                book.file = file_str
                if book.status == "coming soon":
                    book.status = "released"
                book.save()
                return Response({"status": "Ok"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def add_author(self, request, pk=None):
        user = request.user
        try:
            book = Books.objects.filter(pk=pk).first()
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        if book and user and user.is_superuser:
            serializer = AddBookAuthorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer = serializer.save(book=book)
            return Response(GetBookSerializer(serializer).data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def delete_author(self, request, pk=None):
        user = request.user
        try:
            book = Books.objects.filter(pk=pk).first()
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        if book and user and user.is_superuser:
            serializer = DeleteBookAuthorSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer = serializer.save(book=book)
            return Response(GetBookSerializer(serializer).data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def add_genre(self, request, pk=None):
        user = request.user
        try:
            book = Books.objects.filter(pk=pk).first()
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        if book and user and user.is_superuser:
            serializer = AddBookGenreSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer = serializer.save(book=book)
            return Response(GetBookSerializer(serializer).data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def delete_genre(self, request, pk=None):
        user = request.user
        try:
            book = Books.objects.filter(pk=pk).first()
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        if book and user and user.is_superuser:
            serializer = DeleteBookGenreSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer = serializer.save(book=book)
            return Response(GetBookSerializer(serializer).data, status=status.HTTP_200_OK)
        return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class BasketViewSet(viewsets.ModelViewSet):
    queryset = Relations_books.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = CreateBasketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = BasketPositionSerializer(serializer.save(user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user = request.user
        basket = Relations_books.objects.filter(user=user, type="basket")
        serializer = BasketPositionSerializer(basket, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=False)
    def del_position(self, request, *args, **kwargs):
        user = request.user
        serializer = DeleteBasketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = BasketPositionSerializer(serializer.save(user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def basket_by_user(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            if user.is_superuser:
                basket = Relations_books.objects.filter(user==User.objects.filter(pk=pk).first(), type="basket")
                return Response(BasketPositionSerializer(basket, many=True).data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def count_of_basket_position_by_book(self, request, pk, *args, **kwargs):
        book = Books.objects.filter(pk=pk).first()
        user = request.user
        try:
            if user.is_superuser or user.is_staff and book.company == user.company:
                count = len(Relations_books.objects.filter(book=book.pk))
                return Response({"count": f"{count}"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class PurchasesViewSet(viewsets.ModelViewSet):
    queryset = Purchases.objects.all()
    permission_classes = [IsAuthenticated]

    @action(methods=['post'], detail=False)
    def purchase(self, request, *args, **kwargs):
        user = request.user
        serializer = CreatePurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer = PurchaseSerializer(serializer.save(user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=False)
    def pay(self, request, *args, **kwargs):
        user = request.user
        purchase = Purchases.objects.filter(user=user, type="waiting")
        if purchase.exists() and len(purchase) == 1:
            purchase = purchase.first()

            basket = user.relations.all()
            for book in purchase.books.all():
                if book in basket:
                    relation = Relations_books.objects.filter(user=user, book=book).first()
                    relation.type = "personal_library"
                    relation.save()
                else:
                    Relations_books.objects.create(user=user, book=book, type="personal_library")
            purchase.type = "purchase"
            purchase.save()

        return Response(PurchaseSerializer(purchase).data, status=status.HTTP_202_ACCEPTED)

    @action(methods=['patch'], detail=False)
    def deviation(self, request, *args, **kwargs):
        user = request.user
        purchase = Purchases.objects.filter(user=user, type="waiting").first()
        purchase.type = "rejected"
        purchase.save()
        return Response(PurchaseSerializer(purchase).data, status=status.HTTP_202_ACCEPTED)

    @action(methods=['get'], detail=True)
    def purchase_by_user(self, request, pk, *args, **kwargs):
        user = User.objects.filter(pk=pk).first()
        try:
            if user.is_superuser:
                purchase = Purchases.objects.filter(user=user, type="purchase")
                return Response(PurchaseSerializer(purchase, many=True).data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def count_of_purchase_by_book(self, request, pk, *args, **kwargs):
        book = Books.objects.filter(pk=pk).first()
        user = request.user
        try:
            if user.is_superuser or user.is_staff and book.company == user.company:
                count = len(Purchases.objects.prefetch_related('books').values("books").filter(books=book.pk))
                return Response({"count": f"{count}"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


class PersonalLibraryViewSet(viewsets.ModelViewSet):
    queryset = Relations_books.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        library = Relations_books.objects.filter(user=user, type="personal_library")
        serializer = BasketPositionSerializer(library, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def library_by_user(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            if user.is_superuser:
                print(pk)
                library = Relations_books.objects.filter(
                    user=User.objects.filter(pk=pk).first(), type="personal_library")
                return Response(BasketPositionSerializer(library, many=True).data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except Exception:
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def favorite_book(self, request, pk, *args, **kwargs):
        user = request.user
        if not Books.objects.filter(pk=pk).exists():
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            book = Books.objects.filter(pk=pk).first()
            relation = Relations_books.objects.filter(user=user, book=book, type="personal_library")
            if relation.exists():
                relation = relation.first()
                if relation.is_favorite:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
                relation.is_favorite = True
                relation.save()
                return Response(BasketPositionSerializer(relation, many=False).data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=True)
    def unfavorite_book(self, request, pk, *args, **kwargs):
        user = request.user
        if not Books.objects.filter(pk=pk).exists():
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            book = Books.objects.filter(pk=pk).first()
            relation = Relations_books.objects.filter(user=user, book=book, type="personal_library")
            if relation.exists():
                relation = relation.first()
                if not relation.is_favorite:
                    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
                relation.is_favorite = False
                relation.save()
                return Response(BasketPositionSerializer(relation, many=False).data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)\


    @action(methods=['get'], detail=False)
    def favorite_books(self, request, *args, **kwargs):
        user = request.user
        library = Relations_books.objects.filter(user=user, type="personal_library", is_favorite=True)
        serializer = BasketPositionSerializer(library, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def download_file(self, request, pk=None):
        user = request.user
        if not Books.objects.filter(pk=pk).exists():
            return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            book = Books.objects.filter(pk=pk).first()
            relation = Relations_books.objects.filter(user=user, book=book, type="personal_library")
            if relation.exists() or user.is_superuser:
                file_model = Books.objects.filter(pk=pk).first()
                print(file_model.pk)
                if file_model:
                    file_data = file_model.file
                    response = HttpResponse(
                        ast.literal_eval(file_data),
                        content_type="application/pdf")
                    response['Content-Disposition'] = 'attachment; filename="file.pdf"'
                    return response
                else:
                    return Response('No file found in database')
            else:
                return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)