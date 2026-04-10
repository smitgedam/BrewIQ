from django.urls import path
from . import views

app_name = 'intelligence'

urlpatterns = [
    path('', views.intelligence_dashboard, name='dashboard'),
    path('run/', views.run_engine, name='run_engine'),
    path('suggestion/<int:pk>/accept/', views.accept_suggestion, name='accept_suggestion'),
    path('suggestion/<int:pk>/reject/', views.reject_suggestion, name='reject_suggestion'),
    path('api/revenue/', views.revenue_chart_data, name='revenue_data'),
    path('api/top-items/', views.top_items_data, name='top_items_data'),
]
