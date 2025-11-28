from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.Register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('catalog/', views.book_catalog, name='book_catalog'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('add-to-cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('toggle-wishlist/<int:book_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('session-login/', views.session_login, name='session_login'),
    path('session-dashboard/', views.session_dashboard, name='session_dashboard'),
    path('session-logout/', views.session_logout, name='session_logout'),
]
