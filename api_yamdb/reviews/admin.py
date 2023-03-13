from django.contrib import admin

from .models import Category, Genre, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = '-пусто-'


@admin.register(Category, Genre)
class CategoryGenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
