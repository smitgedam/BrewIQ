from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Full pages
    path('dashboard/',               views.dashboard,              name='dashboard'),
    path('create/',                  views.order_create,           name='order_create'),
    path('<int:pk>/',                views.order_detail,           name='order_detail'),
    path('<int:pk>/items/',          views.order_add_items,        name='order_add_items'),
    path('<int:pk>/status/',         views.order_status_update,    name='order_status_update'),
    path('<int:pk>/cancel/',         views.cancel_order,           name='cancel_order'),
    path('list/',                    views.order_list,             name='order_list'),
    path('kds/',                     views.kds_view,               name='kds'),
    path('tables/',                  views.table_list,             name='table_list'),
    # Live-poll HTMX partials
    path('kds/partial/',             views.kds_partial,            name='kds_partial'),
    path('partial/stats/',           views.partial_dashboard_stats, name='partial_stats'),
    path('partial/active/',          views.partial_active_orders,  name='partial_active_orders'),
    path('partial/tables/',          views.partial_table_grid,     name='partial_table_grid'),
    path('partial/list/',            views.partial_order_list,     name='partial_order_list'),
    path('<int:pk>/partial/detail/', views.partial_order_detail,   name='partial_order_detail'),
]
