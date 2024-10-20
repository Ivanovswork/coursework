from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from rest_framework.authtoken.models import Token
from mysite.bookshop.models import User


class UserRGSTRSerializer(ModelSerializer):
    password2 = CharField()

    class Meta:
        model = User

        fields = ["email", "username", "password", "password2"]

    def save(self, **kwargs):
        user = User(
            email=self.validated_data["email"], username=self.validated_data["username"]
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