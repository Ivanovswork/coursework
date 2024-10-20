import ast
import codecs
import os
import tempfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Books


from pydrive.auth import GoogleAuth

from .script import create_and_upload_file
import json
from wsgiref.util import FileWrapper
import base64


@csrf_exempt
@api_view(['POST'])
def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']
        file_str = file.read()
        file_model = Books.objects.create(file=file_str)
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


