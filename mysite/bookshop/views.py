import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Books
from .forms import BookForm

from pydrive.auth import GoogleAuth

from .script import create_and_upload_file
import json

gauth = GoogleAuth()


@csrf_exempt
@api_view(['POST'])
def upload_file(request):
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            data = request.FILES['file']
            json_data = request.POST

            book = Books(name=json_data["name"])
            book.save()

            file_name = f"{book.pk}.pdf"
            default_storage.save(file_name, ContentFile(data.read()))
            link = create_and_upload_file(file_name)
            default_storage.delete(file_name)

            book.file = link

            book.save()

            return HttpResponse("/success/url/")
    else:
        form = BookForm()
    return HttpResponse("/unnnsuccess/url/")


@api_view(['GET'])
def download_file(request, book_id):
    uploaded_file = Books.objects.get(pk=book_id)
    return HttpResponse(json.dumps({"link": f"{uploaded_file.file}"}), content_type='application/json')


@api_view(['GET'])
def download_cover(request, book_id):
    uploaded_cover = Books.objects.get(pk=book_id)
    return HttpResponse(uploaded_cover.cover, content_type='application/jpg')
