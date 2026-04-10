from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('',                          views.inventory_dashboard,    name='dashboard'),
    path('ingredient/create/',        views.ingredient_create,      name='ingredient_create'),
    path('ingredient/<int:pk>/edit/', views.ingredient_update,      name='ingredient_update'),
    path('movement/create/',          views.stock_movement_create,  name='movement_create'),
    path('link/',                     views.link_ingredient,        name='link_ingredient'),
    # Live-poll partial
    path('partial/levels/',           views.partial_inventory_levels, name='partial_levels'),
]
