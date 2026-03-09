from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('assets/', views.asset_list, name='asset_list'),
    path('asset/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('asset/<int:pk>/book/', views.book_asset, name='book_asset'),
    path('init-db/', views.init_db, name='init_db'),
]
