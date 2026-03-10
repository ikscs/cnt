from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import jwt_worker, TUNE_API_KEY, TUNE_BASE_URL

import requests
KV_DB_URL = 'http://kv_db:5000'

def get_img(uuid):
    url = f'{KV_DB_URL}/{uuid}'

    try:
        response = requests.get(url)
    except Exception as err:
        return {'success': False, 'description': str(err)}
    if response.status_code != 200:
        return {'success': False, 'description': response.text}

    try:
        return {'success': True, 'data': response.content}
    except Exception as err:
        return {'success': False, 'description': response.text}

class ImageView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, *args, **kwargs):
        image_name = kwargs.get('image_name')
        if not image_name:
            return HttpResponseNotFound('404')

        img_uuid = jwt_worker.get_uuid(image_name)
        if not img_uuid:
            return HttpResponseNotFound('404')

        result = get_img(img_uuid)
        if result['success']:
            response = HttpResponse(result['data'], content_type="image/jpeg")
            response["Access-Control-Allow-Origin"] = "*"
        else:
            response = HttpResponseNotFound('404')

        return response

class IsInternalService(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.META.get('HTTP_TUNE_API_KEY')
        return api_key == TUNE_API_KEY

class DataEncoderView(APIView):
    permission_classes = [IsInternalService]
    def post(self, request):
        if isinstance(request.data, dict):
            is_url = request.data.get("is_url", False)
            head = TUNE_BASE_URL if is_url else ''
            tail = '.jpg' if is_url else ''
            data = request.data.get('data')
            if data:
                result = {e: f'{head}{jwt_worker.mk_jwt(e)}{tail}' for e in data}
            else:
                result = {}
            return Response({"success": True, "data": result})
        else:
            return Response({"success": False, "data": {}})

class DataDecoderView(APIView):
    permission_classes = [IsInternalService]
    def post(self, request):
        if isinstance(request.data, dict):
            data = request.data.get('data')
            if data:
                result = {e: jwt_worker.get_uuid(e) for e in data}
            else:
                result = {}
            return Response({"success": True, "data": result})
        else:
            return Response({"success": False, "data": {}})
