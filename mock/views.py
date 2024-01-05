from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PageSerializer
from .models import Page

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class PageView(APIView):
    queryset = Page.objects.all()

    def get(self, request, pk, format=None):
        page = Page.objects.get(pk = pk)
        serializer = PageSerializer(page)
        return Response(serializer.data)