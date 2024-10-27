from django.contrib.auth import authenticate
from rest_framework.serializers import ModelSerializer, CharField, ValidationError, EmailField
from rest_framework.authtoken.models import Token
from .models import User, Companies


class UserRGSTRSerializer(ModelSerializer):
    password2 = CharField()

    class Meta:
        model = User

        fields = ["email", "password", "password2"]

    def save(self, **kwargs):
        user = User(
            email=self.validated_data["email"]
        )

        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise ValidationError({"password": "Пароль не совпадает"})
        else:
            user.set_password(password)

            user.save()
            token = Token.objects.create(user=user)
            token.save()

            return user


class UserChangePasswordSerializer(ModelSerializer):
    new_password = CharField()
    password = CharField()
    email = EmailField()

    class Meta:
        model = User

        fields = ["email", "password", "new_password"]

    def save(self, **kwargs):
        email = self.validated_data["email"]
        password = self.validated_data["password"]
        new_password = self.validated_data["new_password"]

        user = authenticate(email=email, password=password)
        if user:
            user.set_password(self.validated_data["new_password"])
            user.save()
            return user
        raise ValidationError({"password": "The wrong password or email was entered"})


class UserToStaffSerializer(ModelSerializer):
    email = EmailField()
    company_name = CharField()

    class Meta:
        model = User
        fields = ["email", "company_name"]

    def validate(self, attrs):
        email = attrs.get("email")
        company_name = attrs.get("company_name")
        # print(email, company_name)

        if not User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Пользователь с таким email не существует."})

        if not Companies.objects.filter(name=company_name).exists():
            raise ValidationError({"company_name": "Компания с таким названием не существует."})

        return attrs

    def save(self, **kwargs):
        user = User.objects.filter(email=self.validated_data["email"]).first()
        company = Companies.objects.filter(name=self.validated_data["company_name"]).first()
        user.company = company
        user.is_staff = True
        user.save()

        return user


class UserDeleteStaffStatusSerializer(ModelSerializer):
    email = EmailField()

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")

        if not User.objects.filter(email=email).exists():
            raise ValidationError({"email": "Пользователь с таким email не существует."})

        return attrs

    def save(self, **kwargs):
        user = User.objects.filter(email=self.validated_data["email"]).first()
        user.is_staff = False
        user.company = None
        user.save()

        return user