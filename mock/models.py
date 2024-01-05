from collections.abc import Iterable
from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Product(models.Model):
    name = models.CharField(unique=True, primary_key=True, max_length=10)

class Page(Product):
    class Meta:
        proxy = True


class ContentCategory(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self) -> str:
        return f"<ContentCategory: {self.name}>"

class Content(models.Model):
    parent = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=10, null=True)
    category = models.ForeignKey(ContentCategory, on_delete=models.CASCADE, null=True, blank=True)

class ContentDetail(models.Model):
    # contents = models.ManyToManyField(Content)
    detail_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True,
                                    limit_choices_to={
                                        "app_label": "mock"
                                    })

    def save(self, *args, **kwargs) -> None:
        if type(self) is ContentDetail:
            raise TypeError("このモデルを継承したモデルから作成する必要があります。")
        
        self.detail_type = ContentType.objects.get(app_label="mock", model=type(self).__name__.lower())
        super().save(*args, **kwargs)
    
    @property
    def detail(self):
        return self.detail_type.get_object_for_this_type(pk=self.pk)

    def __str__(self) -> str:
        return f"<{self.detail}>"

class ContentStyle(models.Model):
    content_root = models.ForeignKey(Content, on_delete=models.CASCADE)
    content_detail = models.ForeignKey(ContentDetail, on_delete=models.CASCADE)

class Button(ContentDetail):
    name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return f"<Button: {self.name}>"

class Linked(ContentDetail):
    next = models.ForeignKey(Product, null=True, blank=True, on_delete=models.CASCADE)



