"""
URL configuration for oneline_book_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_book/', views.add_book, name='add_book'),
    path('book_list/', views.book_list, name='book_list'),
    path('category_list/', views.category_list, name='category_list'),
    path('add_category/', views.add_category, name='add_category'),
    path('edit_book/<int:id>/', views.edit_book, name='edit_book'),
    path('delete_book/<int:id>/', views.delete_book, name='delete_book'),
]
