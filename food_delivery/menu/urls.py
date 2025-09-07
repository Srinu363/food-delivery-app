from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.get_categories, name='get_categories'),
    path('items/', views.get_menu_items, name='get_menu_items'),
    path('items/<str:item_id>/', views.get_menu_item, name='get_menu_item'),
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<str:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
]
