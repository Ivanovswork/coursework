from django.contrib.auth import authenticate
from django.contrib.postgres.search import SearchVector
from rest_framework.serializers import (ModelSerializer, CharField, ValidationError, EmailField, IntegerField, JSONField,
                                        ListField,)
from rest_framework.authtoken.models import Token
from .models import User, Companies, Groups, Genres, Authors, Support_Messages, Comments, Books, Comments_Books, \
    Comments_Authors, AuthorBook, Relations_books, Purchases
from rest_framework.response import Response
from rest_framework import status


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


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "company", "is_superuser", "is_staff", "is_active", "chat"]


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
        new_name = attrs.get("new_name")
        if not Groups.objects.filter(name=name).exists():
            raise ValidationError()
        if Groups.objects.filter(name=new_name).exists():
            raise ValidationError()

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
        new_name = attrs.get("new_name")
        if not Genres.objects.filter(name=name).exists():
            raise ValidationError()
        if Genres.objects.filter(name=new_name).exists():
            raise ValidationError()

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

    def save(self, **kwargs):
        print(self.validated_data)
        author = Authors.objects.create(**self.validated_data)
        print(author)
        author.search_vector = SearchVector("name")
        author.save()
        return author


class PatchAuthorSerializer(ModelSerializer):
    class Meta:
        model = Authors
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.b_day = validated_data.get('b_day', instance.b_day)
        instance.info = validated_data.get('info', instance.info)
        instance.status = validated_data.get('status', instance.status)
        instance.search_vector = SearchVector("name")
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


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Support_Messages
        fields = "__all__"


class BookCommentsSerializer(ModelSerializer):
    book_id = IntegerField()

    class Meta:
        model = Comments
        fields = ["rating", "book_id", "text"]

    def validate(self, attrs):
        rating = attrs.get("rating")
        book_id = attrs.get("book_id")
        text = attrs.get("text")
        print(rating, book_id)
        if Books.objects.filter(pk=book_id).exists() and rating and text:
            return attrs
        raise ValidationError({"status": "Bad request"})

    def save(self, user, **kwargs):
        book = Books.objects.filter(pk=self.validated_data["book_id"]).first()
        if Comments_Books.objects.select_related("comment").values("comment__user", "book").filter(
                comment__user=user, book=book, comment__type="feedback").exists():
            raise ValidationError({"status": "Bad request"})
        comment = Comments.objects.create(
            user=user,
            rating=self.validated_data["rating"],
            text=self.validated_data["text"])
        comment.save()
        comment_book = Comments_Books.objects.create(comment=comment, book=book)
        comment_book.save()

        return comment


class AuthorCommentsSerializer(ModelSerializer):
    author_id = IntegerField()

    class Meta:
        model = Comments
        fields = ["rating", "author_id", "text"]

    def validate(self, attrs):
        rating = attrs.get("rating")
        author_id = attrs.get("author_id")
        text = attrs.get("text")
        print(rating, author_id)
        if Authors.objects.filter(pk=author_id).exists() and rating and text:
            return attrs
        raise ValidationError({"status": "Bad request"})

    def save(self, user, **kwargs):
        author = Authors.objects.filter(pk=self.validated_data["author_id"]).first()
        if Comments_Authors.objects.select_related("comment").values("comment__user", "author").filter(
                comment__user=user, author=author, comment__type="feedback").exists():
            raise ValidationError({"status": "Bad request"})
        comment = Comments.objects.create(
            user=user,
            rating=self.validated_data["rating"],
            text=self.validated_data["text"])
        comment.save()
        comment_author = Comments_Authors.objects.create(comment=comment, author=author)
        comment_author.save()

        return comment


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"


class BooksCommentsSerializer(ModelSerializer):
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = Comments_Books
        fields = ["book", "comment"]


class AuthorsCommentsSerializer(ModelSerializer):
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = Comments_Authors
        fields = ["author", "comment"]


class AuthorComplaintSerializer(ModelSerializer):
    author_id = IntegerField()

    class Meta:
        model = Comments
        fields = ["author_id", "text"]

    def validate(self, attrs):
        author_id = attrs.get("author_id")
        text = attrs.get("text")
        print(author_id)
        if Authors.objects.filter(pk=author_id).exists() and text:
            return attrs
        raise ValidationError({"status": "Bad request"})

    def save(self, user, **kwargs):
        author = Authors.objects.filter(pk=self.validated_data["author_id"]).first()
        comment = Comments.objects.create(
            user=user,
            text=self.validated_data["text"],
            type="complaint")
        comment.save()
        comment_author = Comments_Authors.objects.create(comment=comment, author=author)
        comment_author.save()

        return comment


class BookComplaintSerializer(ModelSerializer):
    book_id = IntegerField()

    class Meta:
        model = Comments
        fields = ["id", "book_id", "text"]

    def validate(self, attrs):
        book_id = attrs.get("book_id")
        text = attrs.get("text")
        print(book_id)
        if Books.objects.filter(pk=book_id).exists() and text:
            return attrs
        raise ValidationError({"status": "Bad request"})

    def save(self, user, **kwargs):
        book = Books.objects.filter(pk=self.validated_data["book_id"]).first()
        comment = Comments.objects.create(
            user=user,
            text=self.validated_data["text"],
            type="complaint")
        comment.save()
        comment_book = Comments_Books.objects.create(comment=comment, book=book)
        comment_book.save()

        return comment


class CommentComplaintSerializer(ModelSerializer):
    comment_id = IntegerField()

    class Meta:
        model = Comments
        fields = ["comment_id", "text"]

    def validate(self, attrs):
        comment_id = attrs.get("comment_id")
        text = attrs.get("text")
        print(comment_id)
        if (Comments.objects.filter(pk=comment_id).exists() and text
            and Comments.objects.filter(pk=comment_id).first().type == "feedback"):
            return attrs
        raise ValidationError({"status": "Bad request"})

    def save(self, user, **kwargs):
        parent_comment = Comments.objects.filter(pk=self.validated_data["comment_id"]).first()
        comment = Comments.objects.create(
            user=user,
            text=self.validated_data["text"],
            type="complaint",
            parent=parent_comment)
        comment.save()

        return comment


class CommentComplaintPresentationSerializer(ModelSerializer):
    parent = CommentSerializer(read_only=True)

    class Meta:
        model = Comments
        fields = "__all__"


class AuthorRequestSerializer(ModelSerializer):
    priority = IntegerField()

    class Meta:
        model = Authors
        fields = "__all__"

    def validate(self, attrs):
        name = attrs.get("name")
        print(name)
        if name is None:
            raise ValidationError({"status": "Bad request"})
        return attrs


class BookSerializer(ModelSerializer):
    authors_set = JSONField()

    class Meta:
        model = Books
        fields = "__all__"

    def validate(self, attrs):
        name = attrs.get("name")
        publication_date = attrs.get("publication_date")
        content = attrs.get("content")
        price = attrs.get("price")
        age_limit = attrs.get("age_limit")
        isbn = attrs.get("isbn")
        bbk = attrs.get("bbk")
        udk = attrs.get("udk")
        author_mark = attrs.get("author_mark")
        language = attrs.get("language")
        priority = attrs.get("priority")
        genres = attrs.get("genres")
        authors = attrs.get("authors_set")
        print(genres)
        print(authors)

        if (name and publication_date and content and price and age_limit and isbn and bbk and udk and author_mark and
                language and priority and genres and authors):
            try:
                for author in authors["authors"]:
                    if not (Authors.objects.filter(pk=author["id"]).exists() and author["priority"]):
                        raise ValidationError()
            except Exception:
                raise ValidationError()

            if authors["new_authors"]:
                for new_author in authors["new_authors"]:
                    print(new_author)
                    serializer = AuthorRequestSerializer(data=new_author)
                    if not serializer.is_valid():
                        raise ValidationError()
            return attrs
        else:
            raise ValidationError()

    def save(self, company_id=None, user=None, **kwargs):
        if company_id:
            if Companies.objects.filter(pk=company_id).exists():
                book = Books.objects.create(name=self.validated_data["name"],
                                            publication_date=self.validated_data["publication_date"],
                                            content=self.validated_data["content"],
                                            price=self.validated_data["price"],
                                            age_limit=self.validated_data["age_limit"],
                                            isbn=self.validated_data["isbn"],
                                            bbk=self.validated_data["bbk"],
                                            udk=self.validated_data["udk"],
                                            author_mark=self.validated_data["author_mark"],
                                            language=self.validated_data["language"],
                                            priority=self.validated_data["priority"],
                                            company=Companies.objects.filter(pk=company_id).first())
                book.search_vector = SearchVector("name")
            else:
                raise ValidationError()
        else:
            book = Books.objects.create(name=self.validated_data["name"],
                                        publication_date=self.validated_data["publication_date"],
                                        content=self.validated_data["content"],
                                        price=self.validated_data["price"],
                                        age_limit=self.validated_data["age_limit"],
                                        isbn=self.validated_data["isbn"],
                                        bbk=self.validated_data["bbk"],
                                        udk=self.validated_data["udk"],
                                        author_mark=self.validated_data["author_mark"],
                                        language=self.validated_data["language"],
                                        priority=self.validated_data["priority"],
                                        company=user.company)
            book.search_vector = SearchVector("name")
        # book.save()

        for genre in self.validated_data["genres"]:
            book.genres.add(genre)
        for author in self.validated_data["authors_set"]["authors"]:
            a = Authors.objects.filter(pk=author["id"]).first()
            a_b = AuthorBook.objects.create(book=book, author=a,priority=author["priority"])
            a.search_vector = SearchVector("name")
            a.save()
            a_b.save()
        for author in self.validated_data["authors_set"]["new_authors"]:
            priority = author.pop("priority")

            serializer = AuthorSerializer(data=author)
            serializer.is_valid(raise_exception=True)
            a = serializer.save()
            print(a)
            a.search_vector = SearchVector("name")
            a_b = AuthorBook.objects.create(book=book, author=a, priority=priority)
            a_b.save()
        book.save()
        return book


class GetBookSerializer(ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    company = CompaniesSerializer(many=False, read_only=True)

    class Meta:
        model = Books
        fields = ["id", "name", "publication_date", "company", "content", "price", "age_limit", "isbn", "bbk", "udk",
                  "author_mark", "language", "priority", "genres", "authors", "reason", "status"]


class PatchBookSerializer(ModelSerializer):
    class Meta:
        model = Books
        fields = ["id", "name", "publication_date", "content", "price", "age_limit", "isbn", "bbk", "udk",
                  "author_mark", "language", "priority", "reason"]

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.publication_date = validated_data.get('publication_date', instance.publication_date)
        instance.content = validated_data.get('content', instance.content)
        instance.age_limit = validated_data.get('age_limit', instance.age_limit)
        instance.price = validated_data.get('price', instance.price)
        instance.isbn = validated_data.get('isbn', instance.isbn)
        instance.bbk = validated_data.get('bbk', instance.bbk)
        instance.udk = validated_data.get('udk', instance.udk)
        instance.author_mark = validated_data.get('author_mark', instance.author_mark)
        instance.language = validated_data.get('language', instance.language)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.reason = validated_data.get('reason', instance.reason)
        instance.search_vector = SearchVector("name")
        instance.save()
        return instance


class AddBookAuthorSerializer(ModelSerializer):
    author_id = IntegerField()

    class Meta:
        model = Books
        fields = ["author_id"]

    def validate(self, attrs):
        author_id = attrs.get("author_id")
        if not author_id:
            raise ValidationError()

        if not Authors.objects.filter(pk=author_id).exists():
            raise ValidationError()

        if Authors.objects.filter(pk=author_id).first().status in ["blocked", "rejected"]:
            raise ValidationError()

        return attrs

    def save(self, book, **kwargs):
        author = Authors.objects.filter(pk=self.validated_data["author_id"]).first()
        if author in book.authors.all():
            raise ValidationError()
        book.authors.add(author)
        book.save()
        return book


class DeleteBookAuthorSerializer(ModelSerializer):
    author_id = IntegerField()

    class Meta:
        model = Books
        fields = ["author_id"]

    def validate(self, attrs):
        author_id = attrs.get("author_id")
        if not author_id:
            raise ValidationError()

        if not Authors.objects.filter(pk=author_id).exists():
            raise ValidationError()

        return attrs

    def save(self, book, **kwargs):
        author = Authors.objects.filter(pk=self.validated_data["author_id"]).first()
        if not author in book.authors.all():
            raise ValidationError()
        book.authors.remove(author)
        book.save()
        return book


class AddBookGenreSerializer(ModelSerializer):
    genre_id = IntegerField()

    class Meta:
        model = Books
        fields = ["genre_id"]

    def validate(self, attrs):
        genre_id = attrs.get("genre_id")
        if not genre_id:
            raise ValidationError()

        if not Genres.objects.filter(pk=genre_id).exists():
            raise ValidationError()

        return attrs

    def save(self, book, **kwargs):
        genre = Genres.objects.filter(pk=self.validated_data["genre_id"]).first()
        if genre in book.genres.all():
            raise ValidationError()
        book.genres.add(genre)
        book.save()
        return book


class DeleteBookGenreSerializer(ModelSerializer):
    genre_id = IntegerField()

    class Meta:
        model = Books
        fields = ["genre_id"]

    def validate(self, attrs):
        genre_id = attrs.get("genre_id")
        if not genre_id:
            raise ValidationError()

        if not Genres.objects.filter(pk=genre_id).exists():
            raise ValidationError()

        return attrs

    def save(self, book, **kwargs):
        genre = Genres.objects.filter(pk=self.validated_data["genre_id"]).first()
        if not genre in book.genres.all():
            raise ValidationError()
        book.genres.remove(genre)
        book.save()
        return book


class BasketPositionSerializer(ModelSerializer):
    book = GetBookSerializer(read_only=True, many=False)
    # user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Relations_books
        fields = ["user", "book", "type", "is_favorite"]


class CreateBasketSerializer(ModelSerializer):
    book_id = IntegerField()

    class Meta:
        model = Relations_books
        fields = ["book_id"]

    def validate(self, attrs):
        book_id = attrs.get("book_id")
        if not book_id:
            raise ValidationError()

        if not Books.objects.filter(pk=book_id).exists():
            raise ValidationError()

        if Books.objects.filter(pk=book_id).first().status in ["blocked", "rejected", "request"]:
            raise ValidationError()

        return attrs

    def save(self, user, **kwargs):
        book = Books.objects.filter(pk=self.validated_data["book_id"]).first()
        if book in user.relations.all():
            raise ValidationError()
        rel = Relations_books.objects.create(user=user, book=book)

        return rel


class DeleteBasketSerializer(ModelSerializer):
    book_id = IntegerField()

    class Meta:
        model = Relations_books
        fields = ["book_id"]

    def validate(self, attrs):
        book_id = attrs.get("book_id")
        if not book_id:
            raise ValidationError()

        if not Books.objects.filter(pk=book_id).exists():
            raise ValidationError()

        if Books.objects.filter(pk=book_id).first().status in ["rejected", "request"]:
            raise ValidationError()

        return attrs

    def save(self, user, **kwargs):
        book = Books.objects.filter(pk=self.validated_data["book_id"]).first()
        try:
            if book not in user.relations.all():
                raise ValidationError()
            rel = Relations_books.objects.filter(user=user, book=book, type="basket").delete()
        except:
            raise ValidationError({"status": "Book not in basket"})

        return rel


class CreatePurchaseSerializer(ModelSerializer):
    books = ListField()

    class Meta:
        model = Purchases
        fields = ["books"]

    def validate(self, attrs):
        books = attrs.get("books")
        if books:
            for book in books:
                book = Books.objects.filter(pk=book)
                if not book.exists():
                    raise ValidationError()
                book = book.first()
                if book.status not in ["coming soon", "released"]:
                    raise ValidationError()
            print("ok")
            return attrs
        else:
            raise ValidationError()

    def save(self, user, **kwargs):
        if Purchases.objects.filter(user=user, type="waiting").exists():
            raise ValidationError({"status": "Already has unpaid purchase"})
        books = self.validated_data["books"]
        basket = []
        for book in books:
            book = Books.objects.filter(pk=book).first()
            print(book)
            if (book not in map(lambda elem: elem.book, Relations_books.objects.filter(user=user, type="basket"))
                    or book in
                    map(lambda elem: elem.book, Relations_books.objects.filter(user=user, type="personal_library"))):
                print(Relations_books.objects.filter(user=user, type="basket"))
                raise ValidationError({"status": "Еhe book is not in the basket or has already been purchased"})
            basket.append(book)

        purchase = Purchases.objects.create(user=user, type="waiting")

        total = 0
        for book in basket:
            total += book.price
            purchase.books.add(book)
        purchase.total = total

        purchase.save()
        return purchase


class PurchaseSerializer(ModelSerializer):
    books = GetBookSerializer(read_only=True, many=True)

    class Meta:
        model = Purchases
        fields = ["user", "type", "total", "books"]




