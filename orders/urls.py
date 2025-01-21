from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('order/new/', views.OrderCreateView.as_view(), name='order-create'),
    path('order/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order-update'),
    path('order/<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order-delete'),
    path('revenue/', views.revenue_report, name='revenue-report'),
]
