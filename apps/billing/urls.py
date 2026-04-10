from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('order/<int:order_pk>/generate/', views.generate_bill,     name='generate_bill'),
    path('<int:pk>/',                      views.bill_detail,        name='bill_detail'),
    path('<int:pk>/print/',                views.bill_print,         name='bill_print'),
    path('list/',                          views.bill_list,          name='bill_list'),
    # Live-poll partial
    path('partial/list/',                  views.partial_bill_list,  name='partial_bill_list'),
]
