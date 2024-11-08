import ast
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Books, User, ConfirmEmailKey, Groups, Genres, Authors, Companies
from .email_class import Email
from .permissions import IsStaff, IsSuperuser
from .serializers import UserChangePasswordSerializer, UserToStaffSerializer, UserDeleteStaffStatusSerializer, \
    GroupSerializer, PatchGroupSerializer, PostDeleteGroupSerializer, GenreSerializer, PostDeleteGenreSerializer, \
    PatchGenreSerializer, AddGenreToGroupSerializer, DeleteGenreFromGroupSerializer, AuthorSerializer, \
    CompaniesSerializer

from .serializers import UserRGSTRSerializer


# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsStaff])
# def upload_file(request):
#     if request.method == 'POST' and is_staff_this_company(request):
#         # file = request.FILES['file']
#         # file_str = file.read()
#         # file_model = Books.objects.create(file=file_str)
#         return HttpResponse('File saved to database')
#
#     return HttpResponse('Invalid request method')
#
#
# @csrf_exempt
# @api_view(['GET'])
# def download_file(request, id):
#     file_model = Books.objects.filter(pk=id).first()
#     print(file_model.pk)
#     if file_model:
#         file_data = file_model.file
#         response = HttpResponse(
#             ast.literal_eval(file_data),
#             content_type="application/pdf")
#         response['Content-Disposition'] = 'attachment; filename="file.pdf"'
#         return response
#     else:
#         return HttpResponse('No file found in database')

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
    if request.method == "POST" and is_owner(request):
        try:
            request.user.auth_token.delete()
            return Response(
                {"status": "Logout has been completed"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"status": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

        if group.is_valid():
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

        if genre.is_valid():
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
        elif self.action in ["update", "delete"]:
            return [IsAuthenticated(), IsSuperuser()]
        return [AllowAny()]

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
        if author.status == "request" and request.user:
            if request.user.is_superuser:
                serializer = self.get_serializer(author)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        if request.user:
            if request.user.is_superuser:
                query = self.queryset
                serializer = self.get_serializer(query, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        query = self.queryset.filter(status="active")
        serializer = self.get_serializer(query, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None, *args, **kwargs):
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
            author.status = "blocked"
            author.save()
            """
            код, который блокирует все книги заблокированного автора или убирает автора из авторов книги
            """
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
    serializer_class = CompaniesSerializer
    permission_classes = [IsAuthenticated, IsSuperuser]

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
            query = self.queryset
            serializer = self.get_serializer(query, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, pk=None, *args, **kwargs):
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