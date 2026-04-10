from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('category/create/', views.category_create, name='category_create'),
    path('category/<int:pk>/edit/', views.category_update, name='category_update'),
    path('item/create/', views.item_create, name='item_create'),
    path('item/<int:pk>/edit/', views.item_update, name='item_update'),
    path('item/<int:pk>/toggle/', views.item_toggle, name='item_toggle'),
]
