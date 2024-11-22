from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from catalog.managers import CategoryManager
from slugify import slugify

def upload_category_gallery(instance, filename):
    return f"categories/{slugify(instance.category.title)}/gallery/{filename}"

class Category(MPTTModel):

    objects = CategoryManager()

    title = models.CharField(
        verbose_name="Имя",
        max_length=200
    )

    active = models.BooleanField(
        verbose_name="Категория активна",
        default=False
    )

    parent = TreeForeignKey(
        'self', 
        verbose_name="Родитель", 
        related_name="children", 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )

    def get_active(self):
        return self.active

    def get_title(self):
        return self.title

    def get_parent(self):
        return self.parent

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class CategoryImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="gallery", verbose_name="Категория")
    image = models.ImageField(verbose_name="Изображение", upload_to=upload_category_gallery)
    sort = models.PositiveIntegerField(verbose_name="Сортировка", default=0)

    def get_image_full_url(self):
        return "http://poedalkin.ru" + self.image.url

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Галерея"