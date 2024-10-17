from decimal import Decimal

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


COMPANIES_CHOICES = [
    ("self-publishing", "Самиздат"),
    ("publishing house", "Издательство"),
]

BOOK_STATUS_CHOICES = [
    ("released", "Выпущена"),
    ("blocked", "Заблокирована"),
    ("coming soon", "Анонс"),
    ("request", "Заявка")
]

AGE_CHOICES = [
    ("zero", "0+"),
    ("six", "6+"),
    ("twelve", "12+"),
    ("sixteen", "16+"),
    ("eighteen", "18+")
]

PURCHASE_CHOICES = [
    ("pre-order", "Предзаказ"),
    ("purchase", "Покупка"),
]

REL_TYPE_CHOICES = [
    ("basket", "Корзина"),
    ("personal_library", "Личная библиотека"),
]

REL_STATUS_CHOICES = [
    ("selected", "Выбрано"),
    ("not_selected", "Не выбрано"),
    ("read", "Прочитано"),
    ("reading", "Читаю"),

]

COMMENT_TYPE_CHOICES = [
    ("feedback", "Отзыв"),
    ("complaint", "Жалоба")
]


class Companies(models.Model):
    name = models.CharField(verbose_name="Название", max_length=40, blank=False)
    status = models.CharField(verbose_name="Статус", choices=COMPANIES_CHOICES, blank=False)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self):
        return self.name


class Groups(models.Model):
    name = models.CharField(verbose_name="Имя", max_length=60, blank=False, null=True)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"{self.name}"


class Authors(models.Model):
    name = models.CharField(verbose_name="Имя", max_length=60, blank=False, null=True)
    b_day = models.DateField(verbose_name="Дата рождения", blank=True)
    info = models.TextField(verbose_name="Дополнительная информация", blank=True)

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Список авторов"

    def __str__(self):
        return f"{self.name}"


class Genres(models.Model):
    name = models.CharField(verbose_name="Имя", max_length=60, blank=False, null=True)
    groups = models.ManyToManyField(Groups)

    class Meta:
        verbose_name = "Жанр или тег"
        verbose_name_plural = "Жанры и теги"

    def __str__(self):
        return f"{self.name}"


class Books(models.Model):
    name = models.CharField(verbose_name="Название", max_length=20, null=True, blank=True)
    company = models.ForeignKey(
        Companies,
        verbose_name="Издательство",
        related_name="books",
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )
    file = models.TextField(
        verbose_name="Файл с книгой",
        null=True
    )
    cover = models.TextField(
        verbose_name="Файл с обложкой",
        null=True
    )
    publication_date = models.DateField(verbose_name="Дата публикации", blank=False, null=True)
    content = models.TextField(verbose_name="Содержание", blank=False, null=True)
    price = models.DecimalField(
        verbose_name="Цена",
        decimal_places=0,
        max_digits=12,
        validators=[MinValueValidator(Decimal('1'))],
        blank=False,
        null=True
    )
    status = models.CharField(verbose_name="Статус", choices=BOOK_STATUS_CHOICES, blank=False, default="request")
    age_limit = models.CharField(
        verbose_name="Возрастное ограничение",
        choices=AGE_CHOICES,
        blank=False,
        default="zero")
    isbn = models.CharField(verbose_name="ISBN", blank=False, null=True)
    bbk = models.CharField(verbose_name="ББК", blank=False, null=True)
    udk = models.CharField(verbose_name="УДК", blank=False, null=True)
    author_mark = models.CharField(verbose_name="Авторский знак", blank=False, null=True)
    language = models.CharField(verbose_name="Язык", blank=False, null=True)
    priority = models.DecimalField(
        verbose_name="Приоритет отображения",
        decimal_places=0,
        max_digits=2, validators=[
            MinValueValidator(Decimal('1')),
            MaxValueValidator(Decimal('10'))
        ],
        blank=False,
        null=True
    )
    genres = models.ManyToManyField(Genres)
    authors = models.ManyToManyField(Authors)

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Список книг"

    def __str__(self):
        return f"{self.name} {self.pk}"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            email=self.normalize_email(email), password=password, **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    email = models.EmailField(verbose_name="e-mail", null=False, unique=True)
    name_validator = UnicodeUsernameValidator()
    name = models.CharField(
        verbose_name="Имя",
        max_length=80,
        validators=[name_validator],
        blank=True
    )
    company = models.ForeignKey(
        Companies,
        verbose_name="Компания",
        related_name="worker",
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(verbose_name="Аккаунт активирован", default=False)
    is_staff = models.BooleanField(verbose_name="Аккаунт уполномоченного лица", default=False)
    is_superuser = models.BooleanField(verbose_name="Аккаунт администратора", default=False)
    favorite_g = models.ManyToManyField(Genres)
    favorite_a = models.ManyToManyField(Authors)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Список пользователей"

    def __str__(self):
        return f"{self.email} {self.name}"


class Support_Messages(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Отправитель",
        related_name="messages",
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )
    parent_message = models.ForeignKey(
        "self",
        verbose_name="Ответ на",
        related_name="response",
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    text = models.TextField(verbose_name="Текст сообщения", blank=False)
    date_time = models.DateTimeField(verbose_name="Дата отправки", auto_now=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"Сообщение {self.user} id:{self.pk}"


class Purchases(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="purchases",
        blank=False,
        null=True,
        on_delete=models.CASCADE)
    date_time = models.DateTimeField(verbose_name="Время совершения покупки", auto_now=True)
    type = models.CharField(verbose_name="Тип покупки", choices=PURCHASE_CHOICES, blank=False, null=True)
    books = models.ManyToManyField(Books, verbose_name="Позиции покупки", blank=False)

    class Meta:
        verbose_name = "Покупка"
        verbose_name_plural = "Покупка"

    def __str__(self):
        return f"{self.pk}, {self.user}, {self.date_time}"


class Relations_books(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="rel_books",
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(
        Books,
        verbose_name="Книга",
        related_name="rel_books",
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )
    is_favorite = models.BooleanField(verbose_name="Является избранной", default=False)
    type = models.CharField(verbose_name="Тип", choices=REL_TYPE_CHOICES, default="basket")
    status = models.CharField(verbose_name="Статус", choices=REL_STATUS_CHOICES, default="not_selected")

    class Meta:
        verbose_name = "Связь с книгой"
        verbose_name_plural = "Связи с книгами"

    def __str__(self):
        return f"{self.pk}, {self.user}, {self.type}, {self.book}"


class Comments(models.Model):
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE, null=True, blank=False)
    rating = models.DecimalField(
        verbose_name="Оценка",
        decimal_places=0,
        max_digits=2, validators=[
            MinValueValidator(Decimal('1')),
            MaxValueValidator(Decimal('5'))
        ],
        blank=True,
        null=True
    )
    date_time = models.DateTimeField(verbose_name="Время публикации", auto_now=True)
    type = models.CharField(verbose_name="Тип", choices=COMMENT_TYPE_CHOICES, default="feedback")
    parent = models.ForeignKey(
        'self',
        verbose_name="Ответ на",
        related_name="response",
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Отзыв или жалоба"
        verbose_name_plural = "Отзывы и жалобы"

    def __str__(self):
        return f"{self.pk}, {self.user}, {self.type}"


class Comments_Authors(models.Model):
    comment = models.OneToOneField(Comments, primary_key=True, on_delete=models.CASCADE, related_name="c_author")
    parent = models.ForeignKey(
        Authors,
        verbose_name="Отзыв на автора",
        related_name="c_author",
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Отзыв или жалоба на автора"
        verbose_name_plural = "Отзывы или жалобы на автора"

    def __str__(self):
        return f"{self.pk}, {self.comment}"


class Comments_Books(models.Model):
    comment = models.OneToOneField(Comments, primary_key=True, on_delete = models.CASCADE, related_name="comment_book")
    parent = models.ForeignKey(
        Books,
        verbose_name="Отзыв на книгу",
        related_name="comment_book",
        blank=False,
        null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Отзыв или жалоба на книгу"
        verbose_name_plural = "Отзывы и жалобы на книги"

    def __str__(self):
        return f"{self.pk}, {self.comment}"