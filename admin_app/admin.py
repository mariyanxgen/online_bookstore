from django.contrib import admin
from .models import Category, Book

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'cat_description']
    search_fields = ['category_name']

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'author']
    date_hierarchy = 'created_at'
