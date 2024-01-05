from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("a/<slug:pk>", views.PageView.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json"])