from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('my-orders/', views.get_my_orders, name='get_my_orders'),
    path('<str:order_id>/', views.get_order_detail, name='get_order_detail'),
    path('admin/all/', views.get_all_orders, name='get_all_orders'),
    path('admin/<str:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('admin/dashboard/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
]
