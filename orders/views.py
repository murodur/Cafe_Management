from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.db.models import Sum
from django.contrib import messages
from rest_framework import viewsets
from .models import Order, OrderItem
from .serializers import OrderSerializer
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderListView(ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.all()
        status = self.request.GET.get('status')
        table = self.request.GET.get('table')
        
        if status:
            queryset = queryset.filter(status=status)
        if table:
            queryset = queryset.filter(table_number=table)
            
        return queryset.order_by('-created_at')

class OrderCreateView(CreateView):
    model = Order
    template_name = 'orders/order_form.html'
    fields = ['table_number']
    success_url = '/'  # Explicitly set to root URL

    def form_valid(self, form):
        response = super().form_valid(form)
        items_data = self.request.POST.getlist('items[]')
        prices_data = self.request.POST.getlist('prices[]')
        
        for item, price in zip(items_data, prices_data):
            if item and price:
                OrderItem.objects.create(
                    order=self.object,
                    name=item,
                    price=price
                )
        
        self.object.calculate_total()
        messages.success(self.request, f'Заказ для стола {self.object.table_number} успешно создан!')
        return response

class OrderUpdateView(UpdateView):
    model = Order
    template_name = 'orders/order_form.html'
    fields = ['status']
    success_url = '/'  # Explicitly set to root URL

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Статус заказа #{self.object.id} успешно обновлен!')
        return response

class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = '/'  # Explicitly set to root URL

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        messages.success(request, f'Заказ #{order.id} успешно удален!')
        return super().delete(request, *args, **kwargs)

def revenue_report(request):
    total_revenue = Order.objects.filter(status='paid').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    return render(request, 'orders/revenue_report.html', {
        'total_revenue': total_revenue
    })
