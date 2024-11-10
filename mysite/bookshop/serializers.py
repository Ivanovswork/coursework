from django.contrib.auth import authenticate
from rest_framework.serializers import ModelSerializer, CharField, ValidationError, EmailField
from rest_framework.authtoken.models import Token
from .models import User, Companies, Groups, Genres, Authors


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


class PostDeleteGroupSerializer(ModelSerializer):
    class Meta:
        model = Groups
        fields = ["name"]

    def validate(self, attrs):
        try:
            name = attrs["name"]
            return attrs
        except Exception:
            raise ValidationError({"status": "Need name in request"})

    def save(self, **kwargs):
        group = Groups.objects.create(name=self.validated_data["name"])
        group.save()

        return group


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Groups
        fields = ["id", "name"]


class PatchGroupSerializer(ModelSerializer):
    new_name = CharField()

    class Meta:
        model = Groups
        fields = ["name", "new_name"]

    def validate(self, attrs):
        name = attrs.get("name")
        if not Groups.objects.filter(name=name).exists():
            raise ValidationError({"name": "Группы с таким name не существует"})

        return attrs

    def save(self, **kwargs):
        group = Groups.objects.filter(name=self.validated_data["name"]).first()
        group.name = self.validated_data["new_name"]
        group.save()

        return group


class PostDeleteGenreSerializer(ModelSerializer):
    class Meta:
        model = Genres
        fields = ["name"]

    def validate(self, attrs):
        try:
            name = attrs["name"]
            return attrs
        except Exception:
            raise ValidationError({"status": "Need name in request"})

    def save(self, **kwargs):
        genre = Genres.objects.create(name=self.validated_data["name"])
        genre.save()

        return genre


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genres
        fields = ["id", "name"]


class PatchGenreSerializer(ModelSerializer):
    new_name = CharField()

    class Meta:
        model = Genres
        fields = ["name", "new_name"]

    def validate(self, attrs):
        name = attrs.get("name")
        if not Genres.objects.filter(name=name).exists():
            raise ValidationError({"name": "Жанра с таким name не существует"})

        return attrs

    def save(self, **kwargs):
        genre = Genres.objects.filter(name=self.validated_data["name"]).first()
        genre.name = self.validated_data["new_name"]
        genre.save()

        return genre


class AddGenreToGroupSerializer(ModelSerializer):
    group = CharField()

    class Meta:
        model = Genres
        fields = ["name", "group"]

    def validate(self, attrs):
        name = attrs.get("name")
        group = attrs.get("group")
        print(name, group)

        if not Genres.objects.filter(name=name).exists() or not Groups.objects.filter(name=group).exists():
            raise ValidationError({"status": "Bad request"})
        elif Genres.objects.filter(name=name).first().groups.filter(name=group).exists():
            print(Genres.objects.filter(name=name).first().groups.filter(name=group).first())
            raise ValidationError({"status": "Bad request"})

        return attrs

    def save(self, **kwargs):
        genre = Genres.objects.filter(name=self.validated_data["name"]).first()
        group = Groups.objects.filter(name=self.validated_data["group"]).first()
        genre.groups.add(group)

        genre.save()

        return genre


class DeleteGenreFromGroupSerializer(ModelSerializer):
    group = CharField()

    class Meta:
        model = Genres
        fields = ["name", "group"]

    def validate(self, attrs):
        name = attrs.get("name")
        group = attrs.get("group")
        print(name, group)

        if not Genres.objects.filter(name=name).exists() or not Groups.objects.filter(name=group).exists():
            raise ValidationError({"status": "Bad request"})
        elif not Genres.objects.filter(name=name).first().groups.filter(name=group).exists():
            print(Genres.objects.filter(name=name).first().groups.filter(name=group).first())
            raise ValidationError({"status": "Bad request"})

        return attrs

    def save(self, **kwargs):
        genre = Genres.objects.filter(name=self.validated_data["name"]).first()
        group = Groups.objects.filter(name=self.validated_data["group"]).first()
        genre.groups.remove(group)

        genre.save()

        return genre


class AuthorSerializer(ModelSerializer):
    class Meta:
        model = Authors
        fields = "__all__"

    def validate(self, attrs):
        name = attrs.get("name")
        print(name)
        if name is None:
            raise ValidationError({"status": "Bad request"})
        return attrs


class PatchAuthorSerializer(ModelSerializer):
    class Meta:
        model = Authors
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.b_day = validated_data.get('b_day', instance.b_day)
        instance.info = validated_data.get('info', instance.info)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class CompaniesSerializer(ModelSerializer):
    class Meta:
        model = Companies
        fields = "__all__"


class PatchCompanySerializer(ModelSerializer):
    class Meta:
        model = Companies
        fields = ["name", "status"]

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


# class PostDeleteFavoriteGenreSerializer(ModelSerializer):
#
#     class Meta:
#         model = Genre