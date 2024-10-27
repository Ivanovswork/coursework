import ast
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Books, User, ConfirmEmailKey
from .email_class import Email
from .permissions import IsStaff, IsSuperuser
from .serializers import UserChangePasswordSerializer, UserToStaffSerializer, UserDeleteStaffStatusSerializer

from .serializers import UserRGSTRSerializer


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
        return Response({"status": "User is not staff now"}, status=status.HTTP_200_OK)
    return Response({"status": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaff])
def upload_file(request):
    if request.method == 'POST' and is_staff_this_company(request):
        # file = request.FILES['file']
        # file_str = file.read()
        # file_model = Books.objects.create(file=file_str)
        return HttpResponse('File saved to database')

    return HttpResponse('Invalid request method')


@csrf_exempt
@api_view(['GET'])
def download_file(request, id):
    file_model = Books.objects.filter(pk=id).first()
    print(file_model.pk)
    if file_model:
        file_data = file_model.file
        response = HttpResponse(
            ast.literal_eval(file_data),
            content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="file.pdf"'
        return response
    else:
        return HttpResponse('No file found in database')