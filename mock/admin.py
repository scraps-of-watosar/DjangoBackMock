from collections.abc import Mapping, Sequence
from dataclasses import fields
from pprint import pprint
from typing import Any
from django import forms
from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.sites import AdminSite
from django.core.files.base import File
from django.db.models.base import Model
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import ForeignObjectRel
from django.forms import ModelChoiceField, ModelForm, Select, Widget, inlineformset_factory
from django.forms.models import ModelChoiceField
from django.forms.utils import ErrorList
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib.admin.exceptions import NotRegistered
from django.urls import path
from django.urls.resolvers import URLPattern
from django.core.handlers.wsgi import WSGIRequest
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

import nested_admin.nested

from .models import *
# Register your models here.

_OptAttrs = dict[str, Any]
APPNAME = "mock"

class CustomRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    template_name = "mock/custom_related_widget_wrapper.html"

    def get_context(self, name: str, value: Any, attrs) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context["customed"] = True
        context["name_used_inside"] = name
        context["id_used_inside"] = attrs.get("id")

        assert type(self.widget) is CustomSelect
        context["selected"] = None
        if (self.widget._selected_instance):
            instance = self.widget._selected_instance
            context["selected"] = {
                "name": instance.detail.name
            }            

        model_name = "button"
        info = (APPNAME, model_name)
        for key, args in [("add_related_url", ["add"]), ("delete_related_template_url", ["delete", "__fk__"]), ("change_related_template_url", ["change", "__fk__"])]:
            context[f"{key}_1"]  = self.get_related_url(info, *args)
        return context


class CustomSelect(Select):
    template_name = "mock/select.html"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._selected_instance = None

    def get_context(self, name: str, value: Any, attrs) -> dict[str, Any]:
        ctx = super().get_context(name, value, attrs)
        for i in ctx["widget"]["optgroups"]:
            v = i[1][0]
            if v['selected'] and v['value']:
                value = v['value']
                self._selected_instance = value.instance
                print(type(value), value.value, value.instance)
                break
        return ctx
    

class ContentStyleInline(nested_admin.nested.NestedTabularInline):
    model = ContentStyle
    max_num = 1
    extra = 1

    def formfield_for_foreignkey(self, db_field: ForeignKey, request: HttpRequest | None, **kwargs: Any) -> ModelChoiceField | None | bool:
        if (db_field.name == "content_detail"):
            kwargs["widget"] = CustomSelect
            kwargs["queryset"] = ContentDetail.objects.all()
        self.__formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
        return False
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        res = super().formfield_for_dbfield(db_field, request, **kwargs)
        if res is not False:
            return res

        formfield = self.__formfield
        try:
            related_modeladmin = self.admin_site.get_model_admin(
                db_field.remote_field.model
            )
        except NotRegistered:
            wrapper_kwargs = {}
        else:
            wrapper_kwargs = {
                "can_add_related": related_modeladmin.has_add_permission(
                    request
                ),
                "can_change_related": related_modeladmin.has_change_permission(
                    request
                ),
                "can_delete_related": related_modeladmin.has_delete_permission(
                    request
                ),
                "can_view_related": related_modeladmin.has_view_permission(
                    request
                ),
            }
        formfield.widget = CustomRelatedFieldWidgetWrapper(
            formfield.widget,
            db_field.remote_field,
            self.admin_site,
            **wrapper_kwargs,
        )
        return formfield


class ContentInline(nested_admin.nested.NestedTabularInline):
    model = Content
    inlines = [ContentStyleInline]
    show_change_link = True
    extra = 1

    def get_inline_instances(self, request: HttpRequest, obj: Any | None) -> list[InlineModelAdmin]:
        inlines = super().get_inline_instances(request, obj)
        contentstyle_inline = inlines[0]
        self._contentstyle_inline_instance: ContentStyleInline = contentstyle_inline # type: ignore
        #print("ContentInline Inlines = content_style inline", contentstyle_inline, dir(contentstyle_inline))
        return inlines


@admin.register(Product)
class ProductAdmin(nested_admin.nested.NestedModelAdmin):
    inlines = [ContentInline]

    def get_urls(self):
        url =  [path("update_product_admin/", self.admin_site.admin_view(self.update_product_admin))]
        url.extend(super().get_urls())
        return url

    def update_product_admin(self, request:WSGIRequest):
        content_style_inline = self._content_inline_instance._contentstyle_inline_instance
        print(self, request.POST, request.POST.get("name"), content_style_inline)
        filtered = []
        for i in ContentDetail.objects.all():
            try:
                filter_value = request.POST.get("name")
            except Exception:
                continue
            if filter_value != "" and getattr(i.detail, "name") != filter_value:
                continue
            filtered.append(str(i.pk))
        return JsonResponse({"pk":filtered}, safe=True)

    def get_inline_instances(self, request: HttpRequest, obj: Any | None) -> list[InlineModelAdmin]:
        inlines = super().get_inline_instances(request, obj)
        content_inline = inlines[0]
        self._content_inline_instance: ContentInline = content_inline # type: ignore
        #print("Product Admin Inlines = content inline", content_inline, dir(content_inline))
        return inlines


@admin.register(ContentDetail)
class ContentDetailAdmin(admin.ModelAdmin):
    exclude = ["detail_type"]


@admin.register(Button, Linked)
class DetailModelAdmin(admin.ModelAdmin):
    exclude = ["detail_type"]

for i in [ContentCategory,]:
    admin.site.register(i)

